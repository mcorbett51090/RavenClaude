#!/usr/bin/env python3
"""precompact-digest.py — extract a curated critical-info digest from the SPAN of a
conversation transcript about to be dropped by the next compaction, before it is lost.

P1 of the precompact-critical-context FORGE plan
(.ravenclaude/runs/forge/precompact-critical-context/plan.md). Host-agnostic: called
by hooks/precompact-digest.sh (Claude Code + VS Code PreCompact archiving) and by the
VS Code extension's manual command (vscode-extension/src/extension.ts).

SECURITY MODEL (P4 review, hardened — see security-review-p4.md):

  B1 — POSTURE GATE + FAIL-CLOSED EGRESS FLOOR. The hook itself is inert unless
  `cheap_lane.mode` is set (absent/off ⇒ nothing is ever called — see
  hooks/precompact-digest.sh). ABOVE that, and evaluated ONCE (not per-path), this
  module refuses to egress AT ALL unless the posture declares `orchestrator_repo_pii:
  false` (repo is PII-clean) OR `cheap_lane_zdr_confirmed: true` (ZDR attested) — the
  same A-on-C floor `claude-orchestrate.sh`'s relay-all path already enforces. Neither
  present ⇒ `extract_digest()` returns (None, "egress-floor-blocked", ...) and calls
  no external process at all.

  B1.3 — a REFUSAL never cascades. `grok-delegate.sh --task-file` exits 8 when it
  detects a secret and refuses BEFORE egress. That refusal must not route the same
  payload to a second processor (`claude -p`) — only genuine unavailability (exit
  2/4/7/9, or a timeout) falls through to the fallback.

  B3 — the excerpt is the HEAD of the span since the last `compact_boundary` (the
  turns about to be dropped by the NEXT compaction), not the tail of the whole file
  (what survives verbatim and needs no preserving). Boundary detection reuses
  compact-anchor.py's own `scan_transcript()` rather than reimplementing it.

  C1/C2 — the pipeline is record-slice → scrub → bound, in that order (never
  bound-then-scrub, which lets a truncation cut split a secret in half and leak the
  surviving fragment). Every path scrubs secret-shaped text BEFORE egress — this
  reuses the exact pattern already shipped in scripts/thing-denial-kb.py's
  `_scrub_secrets` (itself a port of hooks/_scrub.sh / scripts/thing-seat.sh's
  `_secret_patterns` — SOURCE OF TRUTH is hooks/_scrub.sh; keep this copy in sync).

  C3 — the prompt travels via `--task-file <0600 path in a mktemp -d>`, never
  `--task "<text>"` (argv is readable by any local user via `ps -ww`).

Usage:
  precompact-digest.py --input <transcript.jsonl> --out <file> [--max-chars N]
                        [--receipt <path>]
  precompact-digest.py --self-test

Exit codes:
  0  digest written (or self-test passed)
  1  bad args
  2  no usable input (missing file, unreadable)
  3  no digest written — either the egress floor blocked it, the excerpt was empty
     after scrubbing, or both extraction paths failed/were refused. The caller
     (hooks/precompact-digest.sh) must never treat this as a reason to block.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent

# Secret-shaped patterns — a Python port of hooks/_scrub.sh `_secret_patterns` (ERE),
# extended per the P4 security review (C1). SOURCE OF TRUTH is hooks/_scrub.sh /
# scripts/thing-seat.sh / knowledge/concerns-catalog.md — keep this list in sync with
# those (same byte-for-byte core set as scripts/thing-denial-kb.py's copy, plus the
# four P4 additions below). Applied to the excerpt BEFORE it ever reaches a
# subprocess, so a pasted credential in the conversation never leaves this process.
#
# The four new patterns each carry `(?i)` at the START of their own pattern string
# (never mid-pattern — a scoped inline flag not at position 0 is invalid/deprecated
# across the Python versions this repo supports, incl. stock macOS's 3.9). Adding
# case-insensitivity was re-verified against this repo's own false-positive corpus
# (`ssh -p 22222`, `docker run -p 8080:8080`, `kubectl -p prod-cluster` — see
# `_self_test`) before shipping, per the review's explicit warning that blind
# case-insensitivity broke `srm.force-push` before (CLAUDE.md v0.242.0). None of the
# three probe strings contain the literal words (pass/secret/api_key/access_token/
# client_secret/Bearer) or a `gh[pousr]_` prefix, so none of the new patterns can fire
# on them — verified, not assumed (see _self_test).
_SECRET_RES = [
    re.compile(p)
    for p in (
        r"AKIA[0-9A-Z]{12,}",
        r"sk-(?:ant-)?[A-Za-z0-9-]{20,}",
        r"sk_live_[A-Za-z0-9]{24,}",
        r"rk_live_[A-Za-z0-9]{24,}",
        # Widened ghp_ -> gh[pousr]_ (C1): covers ghp_/gho_/ghu_/ghs_/ghr_, not just
        # the personal-access-token prefix. This repo's own root CLAUDE.md has
        # documented a `ghu_` token in-session before this widening existed.
        r"gh[pousr]_[A-Za-z0-9]{30,}",
        r"github_pat_[A-Za-z0-9_]{20,}",
        r"glpat-[A-Za-z0-9_-]{15,}",
        r"xox[baprs]-[A-Za-z0-9-]{10,}",
        r"AIza[0-9A-Za-z_-]{30,}",
        r"npm_[A-Za-z0-9]{30,}",
        r"hf_[A-Za-z0-9]{30,}",
        r"AccountKey=[A-Za-z0-9+/=]{20,}",
        r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}",
        # PEM block SPAN (C1) — the header-only pattern below caught only the BEGIN
        # line, leaving the actual key body to egress in full (worse than no match:
        # the digest LOOKS scrubbed). This one greedily-minimally spans BEGIN..END.
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----",
        # Header-only kept as a defense-in-depth fallback for a torn/truncated PEM
        # block with no matching END line (the span pattern requires both).
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"--password[=\s]\S+",
        r"--token[=\s]\S+",
        r"(?:https?|postgres(?:ql)?|mysql|mongodb|redis|amqp|smtp)s?://"
        r"[A-Za-z0-9._-]{2,}:[A-Za-z0-9._%+-]{4,}@",
        # Generic key-value secret (C1) — JSON/YAML/.env-shaped `password:`/
        # `secret:`/`api_key:`/`access_token:`/`client_secret:` assignments.
        r"(?i)\b(pass(word|wd)?|secret|api[_-]?key|access[_-]?token|client[_-]?secret)\b"
        r"\s*[:=]\s*[\"']?\S{8,}",
        # Opaque Bearer token (C1).
        r"(?i)\bBearer\s+[A-Za-z0-9._\-]{20,}",
    )
]
_SECRET_P_FLAG = re.compile(r"(^|\s)-p[^\s\d]\S{15,}")

_DEFAULT_MAX_CHARS = 12000  # bound egress size independent of the scrub (P4 defense in depth)

_EXTRACTION_INSTRUCTIONS = (
    "You are extracting a CRITICAL-INFO DIGEST from a coding-agent conversation "
    "excerpt that is about to be lost to context compaction. Output ONLY a compact "
    "bulleted list (<=20 bullets) covering: open decisions, pending TODOs, key facts, "
    "file paths mentioned, and unresolved questions. No preamble, no closing remarks. "
    "If the excerpt carries no such content, output exactly: (no critical items found)"
)

# ----------------------------------------------------------------------------------
# B1 — posture read (minimal-scalar, no PyYAML — mirrors conserve-tokens.py /
# stream-session-start.py's own pattern, the established house style for a hook-side
# posture read). Bounded scan so a hostile cloned repo's comfort-posture.yaml can't
# turn this into a latency problem.
# ----------------------------------------------------------------------------------
_POSTURE_MAX_BYTES = 256 * 1024

_CHEAP_LANE_BLOCK_RE = re.compile(r"^[ \t]*cheap_lane[ \t]*:[ \t]*$", re.MULTILINE)
_CL_MODE_RE = re.compile(r"^[ \t]+mode[ \t]*:[ \t]*([A-Za-z_]{1,20})[ \t]*(?:#.*)?$", re.MULTILINE)
_CL_AGENT_RE = re.compile(r"^[ \t]+agent[ \t]*:[ \t]*([A-Za-z_]{1,20})[ \t]*(?:#.*)?$", re.MULTILINE)
_PII_CLEAN_RE = re.compile(
    r"^[ \t]*orchestrator_repo_pii[ \t]*:[ \t]*(true|false|on|off|yes|no)\b",
    re.IGNORECASE | re.MULTILINE,
)
_ZDR_RE = re.compile(
    r"^[ \t]*cheap_lane_zdr_confirmed[ \t]*:[ \t]*(true|false|on|off|yes|no)\b",
    re.IGNORECASE | re.MULTILINE,
)


def _truthy(word: str) -> bool:
    return word.lower() in {"true", "on", "yes"}


def _read_posture_text(project_dir: str | None) -> str:
    try:
        root = Path(project_dir) if project_dir else Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
        path = root / ".ravenclaude" / "comfort-posture.yaml"
        if not path.is_file():
            return ""
        if path.stat().st_size > _POSTURE_MAX_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def read_posture(project_dir: str | None = None) -> dict:
    """Derived posture facts only, minimally parsed (no PyYAML):
      cheap_lane_mode   -- raw scalar, lowercased ("" if absent)
      cheap_lane_agent  -- "grok" | "copilot" (default "grok" -- today's behavior)
      pii_clean         -- True iff `orchestrator_repo_pii: false` is set
      zdr_confirmed     -- True iff `cheap_lane_zdr_confirmed: true` is set
    Fail-safe: an absent/unreadable/oversized file returns the safe defaults, which
    is EGRESS-BLOCKED (pii_clean and zdr_confirmed both default False).
    """
    out = {
        "cheap_lane_mode": "",
        "cheap_lane_agent": "grok",
        "pii_clean": False,
        "zdr_confirmed": False,
    }
    text = _read_posture_text(project_dir)
    if not text:
        return out
    blk = _CHEAP_LANE_BLOCK_RE.search(text)
    if blk:
        tail = text[blk.end() : blk.end() + 4096]
        m = _CL_MODE_RE.search(tail)
        if m:
            out["cheap_lane_mode"] = m.group(1).lower()
        m = _CL_AGENT_RE.search(tail)
        if m and m.group(1).lower() in ("grok", "copilot"):
            out["cheap_lane_agent"] = m.group(1).lower()
    m = _PII_CLEAN_RE.search(text)
    if m:
        out["pii_clean"] = not _truthy(m.group(1))  # "false" == repo declared PII-clean
    m = _ZDR_RE.search(text)
    if m:
        out["zdr_confirmed"] = _truthy(m.group(1))
    return out


def _egress_floor_ok(posture: dict) -> bool:
    """B1.2 — the fail-closed floor. Mirrors claude-orchestrate.sh's `_orch_posture_flag`
    A-on-C gate exactly: PII-clean OR ZDR-confirmed. Neither -> no egress, period."""
    return bool(posture.get("pii_clean")) or bool(posture.get("zdr_confirmed"))


# ----------------------------------------------------------------------------------
# B3 — boundary-aware record slicing. Reuses compact-anchor.py's own boundary-parsing
# logic (its `_BOUNDARY_NEEDLE` prefilter + `scan_transcript()`) rather than a second
# implementation, per the review's explicit instruction.
# ----------------------------------------------------------------------------------
def _load_compact_anchor():
    """Import compact-anchor.py as a module (hyphenated filename -> can't `import`
    it directly). Fail-safe: any failure here just means boundary detection degrades
    to "no boundary found" (the conservative, whole-file-is-the-span fallback) rather
    than raising — this module must never crash the hook it serves."""
    path = _HERE / "compact-anchor.py"
    try:
        spec = importlib.util.spec_from_file_location("_rc_compact_anchor_for_digest", str(path))
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


_compact_anchor = _load_compact_anchor()

# Mirrors compact-anchor.py's own MAX_TRANSCRIPT_BYTES -- a transcript larger than
# this is not scanned; a digest is a best-effort convenience, not worth stalling on.
_MAX_TRANSCRIPT_SCAN_BYTES = 512 * 1024 * 1024


def _record_text(record) -> str:
    """Extract meaningful user/assistant TEXT from one transcript record. Returns ""
    for tool_use/tool_result/thinking-only records, system records, boundary markers,
    and anything not a plain user/assistant turn — per the review's explicit "not raw
    tool_result blobs or thinking-block scaffolding" instruction. This also happens to
    exclude tool_result content (which can carry untrusted fetched/tool output) from
    ever reaching the digest prompt at all, independent of the scrub pass below."""
    if not isinstance(record, dict):
        return ""
    if record.get("type") not in ("user", "assistant"):
        return ""
    message = record.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    parts: list[str] = []
    if isinstance(content, str):
        parts.append(content)
    elif isinstance(content, list):
        for blk in content:
            if isinstance(blk, dict) and blk.get("type") == "text":
                text = blk.get("text")
                if isinstance(text, str):
                    parts.append(text)
    return "\n".join(p for p in parts if p).strip()


def slice_since_boundary(transcript_path: str, max_chars: int) -> str:
    """B3 fix for `raw_excerpt[-max_chars:]`.

    Locates the last `compact_boundary` record (reusing compact-anchor.py's own
    scan_transcript()) and extracts conversational TEXT from the HEAD of the span
    since that boundary -- the turns about to be dropped by the NEXT compaction --
    rather than the tail of the whole file (what the old, wrong slice took, and
    which is exactly the span that needs no preserving: it survives compaction
    verbatim). No boundary yet -> the whole file is the span, from its start (the
    documented first-compaction default case).

    Sliced by RECORD, never by raw byte truncation: each record's full text is taken
    whole, so nothing here ever splits a token mid-record. The loop stops taking
    NEW records once the budget is met -- it does not truncate a record it has
    already decided to include. The final hard byte cap is a SEPARATE, later step
    (extract_digest()'s `bound`), applied AFTER scrubbing (C2) -- never here.
    """
    start_line = 1
    if _compact_anchor is not None:
        try:
            facts = _compact_anchor.scan_transcript(transcript_path)
        except Exception:
            facts = None
        if facts is not None:
            last_line = facts.get("last_line")
            if isinstance(last_line, int) and last_line > 0:
                start_line = last_line + 1

    try:
        if os.path.getsize(transcript_path) > _MAX_TRANSCRIPT_SCAN_BYTES:
            return ""
    except OSError:
        return ""

    parts: list[str] = []
    total = 0
    try:
        with open(transcript_path, "rb") as handle:
            for lineno, raw in enumerate(handle, 1):
                if lineno < start_line:
                    continue
                if total >= max_chars:
                    break
                try:
                    record = json.loads(raw.decode("utf-8", "replace"))
                except (ValueError, UnicodeDecodeError):
                    continue
                text = _record_text(record)
                if not text:
                    continue
                parts.append(text)
                total += len(text)
    except OSError:
        return ""
    return "\n\n".join(parts)


def _scrub_secrets(text: str) -> str:
    """Redact secret-shaped tokens. Fail-safe toward redaction: on any error,
    return a wholesale-redacted marker rather than risk leaking the input."""
    if not text:
        return text
    try:
        out = _SECRET_P_FLAG.sub(lambda m: m.group(1) + "[REDACTED]", text)
        for rx in _SECRET_RES:
            out = rx.sub("[REDACTED]", out)
        return out
    except Exception:
        return "[REDACTED]"


def _cheap_lane_script() -> str:
    return os.environ.get(
        "RC_CHEAP_LANE_SCRIPT", str(_HERE / "cheap-lane-delegate.sh")
    )


def _claude_orchestrate_script() -> str:
    return os.environ.get(
        "RC_CLAUDE_ORCHESTRATE_SCRIPT", str(_HERE / "claude-orchestrate.sh")
    )


def _try_cheap_lane(prompt: str, agent: str = "grok", timeout_s: int = 60) -> tuple[str | None, int | None]:
    """C3/C4: the prompt travels via a 0600 --task-file in a mktemp -d (never argv --
    `ps -ww` on any local user can read a process's argv), unlinked in a `finally`
    whether the call succeeds or fails; the agent comes from the posture's
    `cheap_lane.agent`, not a hard-coded "grok".

    Returns (output_or_None, returncode_or_None). returncode is None only when the
    script is absent or the call itself raised (timeout/exception) -- both are
    genuine UNAVAILABILITY and the caller falls through to the fallback. A real
    returncode (2/4/7/8/9) is always surfaced so the caller can distinguish a
    REFUSAL (8, B1.3 -- must never cascade) from unavailability (2/4/7/9 -- falls
    through)."""
    script = _cheap_lane_script()
    if not Path(script).is_file():
        return None, None
    scratch = None
    try:
        scratch = tempfile.mkdtemp(prefix="rc-precompact-")
        task_file = Path(scratch) / "task.txt"
        task_file.write_text(prompt, encoding="utf-8")
        try:
            os.chmod(task_file, 0o600)
        except OSError:
            pass
        result = subprocess.run(
            [
                "bash",
                script,
                "--agent",
                agent,
                "--mode",
                "advise",
                "--tier",
                "fast",
                "--task-file",
                str(task_file),
            ],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except Exception:
        return None, None
    finally:
        if scratch:
            shutil.rmtree(scratch, ignore_errors=True)
    rc = result.returncode
    if rc != 0:
        return None, rc
    out = (result.stdout or "").strip()
    return (out or None), rc


def _try_claude_fallback(prompt: str, timeout_s: int = 90) -> str | None:
    script = _claude_orchestrate_script()
    if not Path(script).is_file():
        return None
    env = dict(os.environ)
    env["RAVENCLAUDE_ORCH_BRIEF"] = prompt
    try:
        result = subprocess.run(
            ["bash", script, "full"],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            env=env,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    out = (result.stdout or "").strip()
    return out or None


def extract_digest(
    transcript_path: str,
    max_chars: int = _DEFAULT_MAX_CHARS,
    *,
    project_dir: str | None = None,
) -> tuple[str | None, str, dict]:
    """Returns (digest_or_None, method, receipt).

    method: 'cheap-lane' | 'claude-fallback' | 'none' | 'egress-floor-blocked'

    receipt (derived-values-only, never content -- what the hook forwards to
    _emit_hook_event):
      attempted     bool  -- True iff the floor passed AND content was non-empty AND
                              at least one egress path was actually invoked
      destination   str   -- 'cheap-lane' | 'claude-fallback' | 'none'
      bytes_sent    int   -- len(prompt.encode()) actually handed to a subprocess
      outcome       str   -- 'ok' | 'blocked' | 'refused' | 'unavailable' | 'empty'
    """
    posture = read_posture(project_dir)

    # B1.2 -- fail-closed egress floor. ABOVE both the cheap-lane and fallback calls,
    # evaluated exactly ONCE here (not per-path), so a floor block can never be
    # bypassed by falling through to a second processor.
    if not _egress_floor_ok(posture):
        return None, "egress-floor-blocked", {
            "attempted": False,
            "destination": "none",
            "bytes_sent": 0,
            "outcome": "blocked",
        }

    sliced = slice_since_boundary(transcript_path, max_chars)
    scrubbed = _scrub_secrets(sliced)  # C2: scrub BEFORE bound, never after
    bounded = scrubbed[:max_chars] if len(scrubbed) > max_chars else scrubbed
    if not bounded.strip():
        return None, "none", {
            "attempted": False,
            "destination": "none",
            "bytes_sent": 0,
            "outcome": "empty",
        }

    prompt = f"{_EXTRACTION_INSTRUCTIONS}\n\n---EXCERPT START---\n{bounded}\n---EXCERPT END---"
    bytes_sent = len(prompt.encode("utf-8"))
    agent = posture.get("cheap_lane_agent", "grok")

    cheap_digest, cheap_rc = _try_cheap_lane(prompt, agent=agent)
    if cheap_digest:
        return cheap_digest, "cheap-lane", {
            "attempted": True,
            "destination": "cheap-lane",
            "bytes_sent": bytes_sent,
            "outcome": "ok",
        }
    if cheap_rc == 8:
        # B1.3 -- a REFUSAL (secret detected, refused BEFORE egress) must never
        # cascade the same payload to a second processor.
        return None, "none", {
            "attempted": True,
            "destination": "none",
            "bytes_sent": bytes_sent,
            "outcome": "refused",
        }

    digest = _try_claude_fallback(prompt)
    if digest:
        return digest, "claude-fallback", {
            "attempted": True,
            "destination": "claude-fallback",
            "bytes_sent": bytes_sent,
            "outcome": "ok",
        }

    return None, "none", {
        "attempted": True,
        "destination": "none",
        "bytes_sent": bytes_sent,
        "outcome": "unavailable",
    }


def _write_digest(out_path: Path, digest: str, method: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = (
        f"# Pre-compaction critical-info digest\n\n"
        f"captured: {ts}\n"
        f"extraction method: {method}\n\n"
        f"---\n\n"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(header + digest.rstrip() + "\n", encoding="utf-8")
    # C6 -- conversation-derived content; 0600, not the default 0644.
    try:
        out_path.chmod(0o600)
    except OSError:
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description="Pre-compaction critical-info digest extractor")
    ap.add_argument("--input", help="path to the transcript (JSONL) to extract from")
    ap.add_argument("--out", help="path to write the digest markdown file")
    ap.add_argument("--max-chars", type=int, default=_DEFAULT_MAX_CHARS)
    ap.add_argument(
        "--receipt",
        help="optional path to write a derived-values-only JSON audit receipt "
        "(attempted/destination/bytes_sent/outcome -- never content) for the "
        "caller hook to forward via _emit_hook_event",
    )
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    if not args.input or not args.out:
        print("precompact-digest.py: --input and --out are required (or --self-test)", file=sys.stderr)
        return 1

    in_path = Path(args.input)
    if not in_path.is_file():
        print(f"precompact-digest.py: no such input file: {in_path}", file=sys.stderr)
        return 2

    digest, method, receipt = extract_digest(str(in_path), max_chars=args.max_chars)

    if args.receipt:
        try:
            Path(args.receipt).write_text(json.dumps(receipt), encoding="utf-8")
        except OSError:
            pass

    if not digest:
        if method == "egress-floor-blocked":
            reason = (
                "egress floor blocked -- neither orchestrator_repo_pii: false nor "
                "cheap_lane_zdr_confirmed: true is set (no digest written, nothing called)"
            )
        else:
            reason = "extraction failed on every path (no digest written)"
        print(f"precompact-digest.py: {reason}", file=sys.stderr)
        return 3

    _write_digest(Path(args.out), digest, method)
    print(f"precompact-digest.py: digest written -> {args.out} (method: {method})")
    return 0


# --------------------------------------------------------------------------------
# Self-test — no network, no real subprocess. Stub scripts stand in for the cheap
# lane and the claude fallback via RC_CHEAP_LANE_SCRIPT / RC_CLAUDE_ORCHESTRATE_SCRIPT
# env overrides, and a captured-args file proves what was actually sent.
# --------------------------------------------------------------------------------
def _self_test() -> int:
    failures = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        status = "ok" if cond else "FAIL"
        print(f"  [{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
        if not cond:
            failures.append(name)

    orig_cheap = os.environ.get("RC_CHEAP_LANE_SCRIPT")
    orig_claude = os.environ.get("RC_CLAUDE_ORCHESTRATE_SCRIPT")

    _posture_seq = [0]

    def _mk_posture(td: Path, *, pii_clean: bool = False, zdr: bool = False, agent: str = "") -> Path:
        # A UNIQUE directory per call -- reusing one shared "proj" dir across calls
        # would let a LATER _mk_posture() call silently overwrite an EARLIER one's
        # comfort-posture.yaml on disk, corrupting any test still holding a
        # reference to the earlier Path (exactly the kind of bug this repo's own
        # verification-discipline knowledge warns about: a fixture that looks
        # right and silently isn't).
        _posture_seq[0] += 1
        d = td / f"proj-{_posture_seq[0]}"
        (d / ".ravenclaude").mkdir(parents=True, exist_ok=True)
        lines = ["cheap_lane:", "  mode: agent"]
        if agent:
            lines.append(f"  agent: {agent}")
        if pii_clean:
            lines.append("orchestrator_repo_pii: false")
        if zdr:
            lines.append("cheap_lane_zdr_confirmed: true")
        (d / ".ravenclaude" / "comfort-posture.yaml").write_text("\n".join(lines) + "\n")
        return d

    def _user_rec(text: str) -> dict:
        return {"type": "user", "message": {"role": "user", "content": text}}

    def _asst_rec(text: str) -> dict:
        return {
            "type": "assistant",
            "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
        }

    def _thinking_rec(text: str) -> dict:
        return {
            "type": "assistant",
            "message": {"role": "assistant", "content": [{"type": "thinking", "thinking": text}]},
        }

    def _tool_result_rec(text: str) -> dict:
        return {
            "type": "user",
            "message": {"role": "user", "content": [{"type": "tool_result", "text": text}]},
        }

    def _boundary_rec(pre: int = 1000, post: int = 100) -> dict:
        return {
            "subtype": "compact_boundary",
            "isCompactSummary": True,
            "compactMetadata": {
                "trigger": "manual",
                "preTokens": pre,
                "postTokens": post,
                "cumulativeDroppedTokens": pre - post,
            },
        }

    def _mk_transcript(td: Path, name: str, records: list[dict]) -> Path:
        p = td / name
        with p.open("w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec) + "\n")
        return p

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)

        cheap_ok = tdp / "cheap-ok.sh"
        cheap_ok.write_text(
            "#!/usr/bin/env bash\n"
            'printf \'%s\\n\' "$@" > "$0.received"\n'
            'echo "- decision A"\n'
            'echo "- TODO B"\n'
        )
        cheap_ok.chmod(0o755)

        cheap_fail = tdp / "cheap-fail.sh"
        cheap_fail.write_text("#!/usr/bin/env bash\nexit 4\n")
        cheap_fail.chmod(0o755)

        cheap_refuse = tdp / "cheap-refuse.sh"
        cheap_refuse.write_text(
            "#!/usr/bin/env bash\n"
            'printf \'%s\\n\' "$@" > "$0.received"\n'
            "exit 8\n"
        )
        cheap_refuse.chmod(0o755)

        claude_ok = tdp / "claude-ok.sh"
        claude_ok.write_text(
            "#!/usr/bin/env bash\n"
            'echo "$RAVENCLAUDE_ORCH_BRIEF" > "$0.received"\n'
            'echo "- fallback digest item"\n'
        )
        claude_ok.chmod(0o755)

        default_proj = _mk_posture(tdp, pii_clean=True)  # floor OPEN by default below

        # =====================================================================
        # B1 — posture gate / fail-closed egress floor
        # =====================================================================

        # test B1a: neither PII-clean nor ZDR set -> BLOCKED, and neither stub is
        # ever invoked (positive control below proves the same setup DOES call out
        # once the floor is open, so this isn't vacuously green).
        blocked_proj = _mk_posture(tdp, pii_clean=False, zdr=False)
        os.environ["RC_CHEAP_LANE_SCRIPT"] = str(cheap_ok)
        os.environ["RC_CLAUDE_ORCHESTRATE_SCRIPT"] = str(claude_ok)
        transcript_a = _mk_transcript(tdp, "t-a.jsonl", [_user_rec("hello"), _asst_rec("some benign reply")])
        digest, method, receipt = extract_digest(str(transcript_a), project_dir=str(blocked_proj))
        check("floor blocks when neither pii_clean nor zdr_confirmed", method == "egress-floor-blocked", f"got {method}")
        check("floor-blocked: no digest", digest is None)
        check("floor-blocked receipt: attempted=False", receipt["attempted"] is False)
        check("floor-blocked receipt: outcome=blocked", receipt["outcome"] == "blocked")
        check(
            "floor-blocked: cheap-lane stub NEVER invoked",
            not (tdp / "cheap-ok.sh.received").exists(),
        )
        check(
            "floor-blocked: claude-fallback stub NEVER invoked",
            not (tdp / "claude-ok.sh.received").exists(),
        )

        # test B1b (positive control): the identical transcript + identical stubs,
        # with ONLY the floor flipped open -> the stub IS invoked. Proves B1a is a
        # real discriminator, not a fixture that never calls out regardless.
        digest, method, receipt = extract_digest(str(transcript_a), project_dir=str(default_proj))
        check("positive control: floor open -> cheap-lane runs", method == "cheap-lane", f"got {method}")
        check(
            "positive control: cheap-lane stub WAS invoked this time",
            (tdp / "cheap-ok.sh.received").exists(),
        )
        (tdp / "cheap-ok.sh.received").unlink(missing_ok=True)

        # test B1c: zdr_confirmed alone (without pii_clean) also opens the floor.
        zdr_proj = _mk_posture(tdp, pii_clean=False, zdr=True)
        digest, method, receipt = extract_digest(str(transcript_a), project_dir=str(zdr_proj))
        check("zdr_confirmed alone opens the floor", method == "cheap-lane", f"got {method}")
        (tdp / "cheap-ok.sh.received").unlink(missing_ok=True)

        # =====================================================================
        # B1.3 — a refusal (exit 8) must never cascade to the fallback
        # =====================================================================
        os.environ["RC_CHEAP_LANE_SCRIPT"] = str(cheap_refuse)
        digest, method, receipt = extract_digest(str(transcript_a), project_dir=str(default_proj))
        check("exit-8 refusal: digest is None", digest is None)
        check("exit-8 refusal: method is 'none', not 'claude-fallback'", method == "none")
        check("exit-8 refusal: receipt outcome=refused", receipt["outcome"] == "refused")
        check(
            "exit-8 refusal: claude-fallback NEVER invoked (no cascade)",
            not (tdp / "claude-ok.sh.received").exists(),
        )

        # test: genuine unavailability (exit 4) DOES fall through to the fallback.
        os.environ["RC_CHEAP_LANE_SCRIPT"] = str(cheap_fail)
        digest, method, receipt = extract_digest(str(transcript_a), project_dir=str(default_proj))
        check("exit-4 (genuine unavailability) falls back to claude-fallback", method == "claude-fallback", f"got {method}")
        check("fallback digest content used", digest is not None and "fallback digest item" in (digest or ""))
        check("fallback receipt outcome=ok", receipt["outcome"] == "ok")
        (tdp / "claude-ok.sh.received").unlink(missing_ok=True)

        # cheap lane tried first, claude fallback NOT invoked on success (legacy assertion, preserved)
        os.environ["RC_CHEAP_LANE_SCRIPT"] = str(cheap_ok)
        digest, method, receipt = extract_digest(str(transcript_a), project_dir=str(default_proj))
        check("cheap lane tried first", method == "cheap-lane", f"got method={method}")
        check(
            "claude fallback not invoked when cheap lane succeeds",
            not (tdp / "claude-ok.sh.received").exists(),
        )
        (tdp / "cheap-ok.sh.received").unlink(missing_ok=True)

        # =====================================================================
        # B3 — record-slice takes the HEAD of the span since the last boundary,
        # not the tail of the whole file.
        # =====================================================================
        multi = [
            _asst_rec("OLD-BEFORE-FIRST-BOUNDARY"),
            _boundary_rec(2000, 500),
            _asst_rec("HEAD-OF-MIDDLE-SPAN"),
            _asst_rec("MIDDLE-OF-MIDDLE-SPAN"),
            _boundary_rec(1500, 300),  # the LAST boundary
            _asst_rec("HEAD-OF-FINAL-SPAN"),
            _asst_rec("TAIL-OF-FILE"),
        ]
        transcript_b = _mk_transcript(tdp, "t-b.jsonl", multi)
        sliced_small = slice_since_boundary(str(transcript_b), max_chars=len("HEAD-OF-FINAL-SPAN"))
        check("B3: head-of-final-span present", "HEAD-OF-FINAL-SPAN" in sliced_small)
        check("B3: tail-of-file NOT the slice (small budget)", "TAIL-OF-FILE" not in sliced_small)
        check("B3: pre-last-boundary content excluded", "MIDDLE-OF-MIDDLE-SPAN" not in sliced_small)
        check("B3: content before the FIRST boundary excluded", "OLD-BEFORE-FIRST-BOUNDARY" not in sliced_small)

        sliced_wide = slice_since_boundary(str(transcript_b), max_chars=10000)
        check("B3: with a wide budget, head-of-final-span still comes FIRST", sliced_wide.startswith("HEAD-OF-FINAL-SPAN"))
        idx_head = sliced_wide.find("HEAD-OF-FINAL-SPAN")
        idx_tail = sliced_wide.find("TAIL-OF-FILE")
        check(
            "B3: head-of-span precedes tail-of-file in ordering",
            idx_head != -1 and idx_tail != -1 and idx_head < idx_tail,
        )

        # No boundary at all -> whole file is the span, sliced from ITS head (the
        # documented first-compaction default case).
        no_boundary = [_asst_rec("FIRST-TURN"), _asst_rec("SECOND-TURN"), _asst_rec("THIRD-TURN")]
        transcript_c = _mk_transcript(tdp, "t-c.jsonl", no_boundary)
        sliced_c = slice_since_boundary(str(transcript_c), max_chars=len("FIRST-TURN") + 2)
        check("B3: no boundary yet -> slice starts from the FILE's head", sliced_c.startswith("FIRST-TURN"))
        check("B3: no boundary yet -> later turns excluded once budget met", "THIRD-TURN" not in sliced_c)

        # thinking-block scaffolding and tool_result blobs are excluded from the slice.
        scaffolding = [
            _thinking_rec("some internal reasoning nobody should egress"),
            _tool_result_rec("raw tool output blob"),
            _asst_rec("the actual reply text"),
        ]
        transcript_d = _mk_transcript(tdp, "t-d.jsonl", scaffolding)
        sliced_d = slice_since_boundary(str(transcript_d), max_chars=10000)
        check("B3: thinking-block content excluded from the slice", "internal reasoning" not in sliced_d)
        check("B3: tool_result blob excluded from the slice", "raw tool output blob" not in sliced_d)
        check("B3: real assistant text IS included", "the actual reply text" in sliced_d)

        # =====================================================================
        # C1/C2 — pipeline order (record-slice -> scrub -> bound) + new patterns.
        # A secret planted right at the truncation boundary must be FULLY
        # redacted, not partially split.
        # =====================================================================
        prefix = "x" * 500
        secret = "ghp_" + ("A" * 40)  # 44 chars; ends at index 544 in `combined`
        combined = prefix + secret
        cut = 520  # lands squarely inside the secret (starts at 500, len 44)

        # must-fail control: the WRONG order (bound-then-scrub) DOES split the
        # secret and leak a fragment -- proves this fixture is a real discriminator,
        # not vacuously green because the pattern would have caught it either way.
        partial_secret = secret[: cut - len(prefix)]  # "ghp_" + 16 A's = 20 chars,
        # too short for the {30,} trailing-length requirement -> the pattern
        # genuinely does not match a truncated fragment, so a bound-then-scrub
        # pipeline leaks it verbatim.
        bad_order = _scrub_secrets(combined[:cut])
        check(
            "C2 must-fail control: bound-THEN-scrub leaks a partial secret fragment",
            partial_secret in bad_order and "[REDACTED]" not in bad_order,
            f"the fixture itself is broken -- bound-then-scrub should leak {partial_secret!r} here, got {bad_order!r}",
        )

        combined_rec = [_asst_rec(combined)]
        transcript_e = _mk_transcript(tdp, "t-e.jsonl", combined_rec)
        os.environ["RC_CHEAP_LANE_SCRIPT"] = str(cheap_ok)
        # The stub copies the --task-file's CONTENT to disk WHILE it is still
        # running (i.e. before _try_cheap_lane's `finally: shutil.rmtree(...)`
        # deletes the scratch dir once subprocess.run() returns) -- reading the
        # path back afterward would race the cleanup and always find it gone.
        cheap_ok.write_text(
            "#!/usr/bin/env bash\n"
            'while [ $# -gt 0 ]; do\n'
            '  if [ "$1" = "--task-file" ]; then cp "$2" "$0.receivedprompt" 2>/dev/null; fi\n'
            '  shift\n'
            "done\n"
            'echo "- ok"\n'
        )
        cheap_ok.chmod(0o755)
        digest, method, receipt = extract_digest(str(transcript_e), max_chars=cut, project_dir=str(default_proj))
        prompt_file = tdp / "cheap-ok.sh.receivedprompt"
        sent_prompt = prompt_file.read_text() if prompt_file.exists() else ""
        check("C2: correct order (record-slice->scrub->bound) -- secret fully redacted", secret not in sent_prompt)
        check("C2: redaction marker present, not a split fragment", "[REDACTED]" in sent_prompt)
        check("C2: no bare 'ghp_' fragment survives", "ghp_" not in sent_prompt)
        prompt_file.unlink(missing_ok=True)

        # =====================================================================
        # C1 — new pattern coverage: PEM block, key-value, Bearer, gh[pousr]_,
        # plus the case-insensitivity false-positive check.
        # =====================================================================
        pem_body = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIBOgIBAAJBAK...redacted-body-content-that-must-never-egress...\n"
            "-----END RSA PRIVATE KEY-----"
        )
        scrubbed_pem = _scrub_secrets(pem_body)
        check("C1: PEM block body fully redacted (not just the header)", "redacted-body-content" not in scrubbed_pem)
        check("C1: PEM redaction marker present", "[REDACTED]" in scrubbed_pem)

        kv_cases = [
            ('password: "hunter2hunter2"', "password"),
            ("api_key=sk_test_abcdefghij123456", "api_key"),
            ('SECRET="topsecretvalue123"', "secret (uppercase key -- case-insensitive)"),
            ("client_secret: abcdef0123456789", "client_secret"),
        ]
        for raw, label in kv_cases:
            out = _scrub_secrets(raw)
            check(f"C1: key-value pattern catches {label}", "[REDACTED]" in out, f"input={raw!r} output={out!r}")

        bearer_cases = [
            "Authorization: Bearer abcdefghijklmnopqrstuvwxyz012345",
            "authorization: bearer ABCDEFGHIJKLMNOPQRSTUVWXYZ012345",  # lowercase 'bearer'
        ]
        for raw in bearer_cases:
            out = _scrub_secrets(raw)
            check(f"C1: Bearer pattern catches {raw[:20]}...", "[REDACTED]" in out)

        gh_cases = ["ghp_" + "A" * 36, "gho_" + "B" * 36, "ghu_" + "C" * 36, "ghs_" + "D" * 36, "ghr_" + "E" * 36]
        for tok in gh_cases:
            out = _scrub_secrets(f"here is a token: {tok} end")
            check(f"C1: widened gh[pousr]_ catches {tok[:4]}", tok not in out and "[REDACTED]" in out)

        # C1 false-positive check (per the review's explicit instruction, mirroring
        # this repo's own srm.force-push lesson about blind case-insensitivity).
        fp_probes = [
            "ssh -p 22222",
            "docker run -p 8080:8080",
            "kubectl -p prod-cluster",
        ]
        for probe in fp_probes:
            out = _scrub_secrets(probe)
            check(f"C1 false-positive check: {probe!r} untouched", out == probe, f"got {out!r}")

        # =====================================================================
        # C3 — argv exposure. The stub receives ONLY --task-file <path>; the
        # prompt text itself never appears in argv.
        # =====================================================================
        os.environ["RC_CHEAP_LANE_SCRIPT"] = str(cheap_ok)
        cheap_ok.write_text(
            "#!/usr/bin/env bash\n"
            'printf \'%s\\n\' "$@" > "$0.receivedargv"\n'
            'echo "- ok"\n'
        )
        cheap_ok.chmod(0o755)
        secret_marker = "ARGV-SHOULD-NEVER-CONTAIN-THIS-PROMPT-TEXT"
        transcript_f = _mk_transcript(tdp, "t-f.jsonl", [_asst_rec(secret_marker)])
        digest, method, receipt = extract_digest(str(transcript_f), project_dir=str(default_proj))
        argv_dump = (tdp / "cheap-ok.sh.receivedargv").read_text() if (tdp / "cheap-ok.sh.receivedargv").exists() else ""
        check("C3: --task-file present in argv", "--task-file" in argv_dump)
        check("C3: bare --task NOT used", "\n--task\n" not in ("\n" + argv_dump))
        check("C3: prompt text NEVER appears in argv", secret_marker not in argv_dump)
        (tdp / "cheap-ok.sh.receivedargv").unlink(missing_ok=True)

        # =====================================================================
        # C4 — cheap_lane.agent is honored, not hard-coded to grok.
        # =====================================================================
        agent_proj = _mk_posture(tdp, pii_clean=True, agent="copilot")
        cheap_ok.write_text(
            "#!/usr/bin/env bash\n"
            'printf \'%s\\n\' "$@" > "$0.receivedagent"\n'
            'echo "- ok"\n'
        )
        cheap_ok.chmod(0o755)
        digest, method, receipt = extract_digest(str(transcript_a), project_dir=str(agent_proj))
        agent_argv = (tdp / "cheap-ok.sh.receivedagent").read_text() if (tdp / "cheap-ok.sh.receivedagent").exists() else ""
        check("C4: cheap_lane.agent=copilot is passed through, not hard-coded grok", "copilot" in agent_argv)
        (tdp / "cheap-ok.sh.receivedagent").unlink(missing_ok=True)

        # default (no agent key set) still resolves to grok -- no regression.
        digest, method, receipt = extract_digest(transcript_a.as_posix(), project_dir=str(default_proj))
        default_argv = (tdp / "cheap-ok.sh.receivedagent").read_text() if (tdp / "cheap-ok.sh.receivedagent").exists() else ""
        check("C4: absent cheap_lane.agent still defaults to grok", "grok" in default_argv)
        (tdp / "cheap-ok.sh.receivedagent").unlink(missing_ok=True)

        # =====================================================================
        # egress bounded by max_chars, independent of scrub (defense in depth) --
        # legacy assertion, adapted to the transcript-based API.
        # =====================================================================
        cheap_ok.write_text(
            "#!/usr/bin/env bash\n"
            'while [ $# -gt 0 ]; do if [ "$1" = "--task-file" ]; then wc -c < "$2" > "$0.receivedlen"; fi; shift; done\n'
            'echo "- ok"\n'
        )
        cheap_ok.chmod(0o755)
        huge_rec = [_asst_rec("x" * 50000)]
        transcript_g = _mk_transcript(tdp, "t-g.jsonl", huge_rec)
        extract_digest(str(transcript_g), max_chars=1000, project_dir=str(default_proj))
        receivedlen = tdp / "cheap-ok.sh.receivedlen"
        n = int(receivedlen.read_text().strip()) if receivedlen.exists() else -1
        check("egress bounded by max_chars", 0 < n < 5000, f"sent {n} bytes for a 1000-char bound")
        receivedlen.unlink(missing_ok=True)

        # =====================================================================
        # C6 — digest file is written 0600, not the default 0644.
        # =====================================================================
        out_file = tdp / "digest-out.md"
        _write_digest(out_file, "- an item", "cheap-lane")
        mode = out_file.stat().st_mode & 0o777
        check("C6: digest file written 0600", mode == 0o600, f"got {oct(mode)}")

    if orig_cheap is None:
        os.environ.pop("RC_CHEAP_LANE_SCRIPT", None)
    else:
        os.environ["RC_CHEAP_LANE_SCRIPT"] = orig_cheap
    if orig_claude is None:
        os.environ.pop("RC_CLAUDE_ORCHESTRATE_SCRIPT", None)
    else:
        os.environ["RC_CLAUDE_ORCHESTRATE_SCRIPT"] = orig_claude

    if failures:
        print(f"\nprecompact-digest.py --self-test: {len(failures)} FAILED CHECK(S):")
        for f in failures:
            print(f"  - {f}")
    else:
        print("\nprecompact-digest.py --self-test: all checks passed")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
