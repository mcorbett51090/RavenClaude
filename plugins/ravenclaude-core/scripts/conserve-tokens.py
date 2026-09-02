#!/usr/bin/env python3
"""conserve-tokens.py — resolve the conserve-tokens exception to maximum parallelism.

Parallelism defaults to MAXIMUM (v0.273.0): an absent `parallelism:` block means
"fan independent work out as wide as the work allows". This module owns the one
exception, and it has THREE triggers with a fixed precedence:

    1. SESSION PHRASE   (per-session, either direction, HIGHEST)
       A phrase in the user's own prompt -- "conserve tokens" engages it,
       "maximum parallelism" / "stop conserving" releases it. An explicit human
       instruction in the live session beats standing configuration in both
       directions, so the release phrase is as load-bearing as the engage
       phrase: without it the only exit from a phrase-engaged session would be
       editing a config file mid-conversation.

    2. POSTURE SWITCH   (persistent)
       `conserve_tokens: true` in .ravenclaude/comfort-posture.yaml, written by
       the dashboard's Pipeline tab. Engages only -- there is deliberately no
       `conserve_tokens: false`-means-never, because that would let a stale
       config silently suppress trigger 3 (real budget pressure) and the whole
       point of 3 is that it fires when nobody is watching.

    3. CONTEXT PRESSURE (automatic)
       Live usage at or over `conserve_tokens_auto_pct` percent of the context
       window (default 80; 0 disables). The measurement is NOT re-implemented
       here -- it is delegated to scripts/context-usage-meter.py, the single
       source of live-usage truth this repo already ships (and which
       handoff-nudge.py already consumes). A second, divergent meter is exactly
       the drift this reuse exists to prevent.

  Resolution:  engaged = phrase_override  if a phrase fired this session
                       else (posture_switch or context_pressure)

WHAT "ENGAGED" MEANS, in one sentence, so no fourth mode has to be documented:
the `parallelism:` posture is read as `enabled: false` -- sequential, one worker
at a time -- until the exception releases.

HONEST LIMIT (this is a behavioral commitment, not a control): nothing here can
compel the agent to batch work, and nothing here blocks a dispatch. A hook can
stop an action; it cannot make one happen. The teeth are the directive (the
SessionStart banner), the skill text spawn-team reads, and the DETECTOR
(parallelism-detector.py) that measures when independent work ran serially.

FAIL-SAFE: every path exits 0. A missing posture, an unreadable session dir, a
malformed payload, an absent context meter -- all resolve to "not engaged" and
print nothing. This module can never break the prompt it rides on.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path

SCHEMA_VERSION = 1

# Cap the posture read. Mirrors the _CONFIG_SCAN_CAP discipline in
# context-usage-meter.py: a hostile cloned repo must not be able to make a
# per-prompt hook scan an unbounded file.
_POSTURE_MAX_BYTES = 256 * 1024
# Cap the prompt scan. Phrase detection is a fixed-substring search over a
# lowercased prefix; an enormous pasted payload must not turn a per-prompt hook
# into a latency problem.
_PROMPT_SCAN_CHARS = 20000

_CONSERVE_RE = re.compile(
    r"^[ \t]*conserve_tokens[ \t]*:[ \t]*(true|false|on|off|yes|no)\b",
    re.IGNORECASE | re.MULTILINE,
)
_AUTO_PCT_RE = re.compile(
    r"^[ \t]*conserve_tokens_auto_pct[ \t]*:[ \t]*(\d{1,3})\b",
    re.MULTILINE,
)
# The parallelism block, read only well enough to report the posture in the
# banner. The authoritative consumer is spawn-team; this is a derived label.
_PARALLELISM_BLOCK_RE = re.compile(r"^[ \t]*parallelism[ \t]*:[ \t]*(\S+)?[ \t]*$", re.MULTILINE)
_PL_ENABLED_RE = re.compile(r"^[ \t]+enabled[ \t]*:[ \t]*(true|false)\b", re.IGNORECASE | re.MULTILINE)
_PL_WORKERS_RE = re.compile(r"^[ \t]+max_workers[ \t]*:[ \t]*(unlimited|\d{1,4})\b", re.MULTILINE)

CONSERVE_AUTO_PCT_DEFAULT = 80

# Fixed phrase vocabularies. Deliberately SHORT and specific: a broad list
# ("budget", "cheap", "tokens") would engage conserve mode on prompts that were
# merely discussing cost, and a mode that engages when nobody asked is worse
# than one that occasionally misses -- the miss costs tokens, the false positive
# costs the parallelism the owner asked for by default.
RELEASE_PHRASES = (
    "stop conserving",
    "conserve off",
    "maximum parallelism",
    "max parallelism",
    "full parallelism",
    "fan out fully",
)
ENGAGE_PHRASES = (
    "conserve tokens",
    "conserve context",
    "token conservation",
    "save tokens",
    "minimize tokens",
    "minimise tokens",
    "low token mode",
)


def _read_text(path: Path, cap: int) -> str:
    try:
        if not path.is_file():
            return ""
        if path.stat().st_size > cap:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _truthy(word: str) -> bool:
    return word.lower() in {"true", "on", "yes"}


def read_posture(root: Path) -> dict:
    """Derived posture facts only. Never returns raw config text."""
    out = {
        "conserve_tokens": False,
        "auto_pct": CONSERVE_AUTO_PCT_DEFAULT,
        "parallelism": "max",
        "max_workers": None,
    }
    raw = _read_text(root / ".ravenclaude" / "comfort-posture.yaml", _POSTURE_MAX_BYTES)
    if not raw:
        return out
    m = _CONSERVE_RE.search(raw)
    if m:
        out["conserve_tokens"] = _truthy(m.group(1))
    m = _AUTO_PCT_RE.search(raw)
    if m:
        val = int(m.group(1))
        if 0 <= val <= 100:
            out["auto_pct"] = val
    blk = _PARALLELISM_BLOCK_RE.search(raw)
    if blk:
        scalar = (blk.group(1) or "").lower()
        if scalar in {"off", "false", "no"}:
            out["parallelism"] = "sequential"
        elif scalar in {"on", "true", "yes"}:
            out["parallelism"] = "max"
        else:
            # Mapping form: read the two keys that follow, within the block.
            tail = raw[blk.end() : blk.end() + 4096]
            enabled = _PL_ENABLED_RE.search(tail)
            workers = _PL_WORKERS_RE.search(tail)
            if enabled and enabled.group(1).lower() == "false":
                out["parallelism"] = "sequential"
            elif workers and workers.group(1) != "unlimited":
                out["parallelism"] = "capped"
                out["max_workers"] = int(workers.group(1))
            else:
                out["parallelism"] = "max"
    return out


def find_project_root(start: Path) -> Path:
    try:
        cur = start.resolve()
    except OSError:
        return start
    for cand in (cur, *cur.parents):
        if (cand / ".ravenclaude").is_dir() or (cand / ".git").exists():
            return cand
    return cur


def _session_id(payload: dict) -> str:
    raw = os.environ.get("CLAUDE_SESSION_ID") or payload.get("session_id") or ""
    # Sanitize to a path-safe token: the value lands in a directory name.
    safe = re.sub(r"[^A-Za-z0-9._-]", "", str(raw))[:128]
    return safe or "unknown"


def state_path(root: Path, session: str) -> Path:
    return root / ".ravenclaude" / "runs" / session / "conserve-tokens.json"


def read_state(path: Path) -> dict:
    raw = _read_text(path, 64 * 1024)
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
    except ValueError:
        return {}
    return obj if isinstance(obj, dict) else {}


def write_state(path: Path, state: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state, separators=(",", ":")) + "\n", encoding="utf-8")
        tmp.replace(path)
    except OSError:
        pass


def detect_phrase(prompt: str) -> str | None:
    """Return "release" | "engage" | None. Release is evaluated FIRST so an
    explicit release wins over an incidental engage substring in the same turn."""
    if not prompt:
        return None
    hay = prompt[:_PROMPT_SCAN_CHARS].lower()
    for p in RELEASE_PHRASES:
        if p in hay:
            return "release"
    for p in ENGAGE_PHRASES:
        if p in hay:
            return "engage"
    return None


def _meter_module():
    """Load context-usage-meter.py — the ONE live-usage source. Never re-derive."""
    here = Path(__file__).resolve().parent
    target = here / "context-usage-meter.py"
    if not target.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("_rc_ctx_meter", target)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def context_percent(payload: dict, root: Path) -> float | None:
    """Live context usage as a percent, or None when it cannot be measured.

    None is NOT zero. An unmeasurable window means the automatic trigger stays
    silent — never that the session is comfortably empty. Reporting an unknown
    as 0% would make trigger 3 fail toward "keep spending", which is the wrong
    direction for a budget guard.
    """
    mod = _meter_module()
    if mod is None:
        return None
    try:
        session = mod.session_dir_from_env(payload)
        posture = mod.read_posture(root)
        result = mod.measure(
            session,
            posture.get("window"),
            posture.get("threshold"),
            None,
            claude_payload=payload,
        )
    except Exception:
        return None
    if not isinstance(result, dict) or result.get("status") != "ok":
        return None
    pct = result.get("percent")
    return float(pct) if isinstance(pct, (int, float)) else None


def resolve(payload: dict, root: Path, session: str, prompt: str | None) -> dict:
    """Apply the documented precedence and persist the session half."""
    posture = read_posture(root)
    sp = state_path(root, session)
    state = read_state(sp)
    prev_engaged = bool(state.get("engaged"))
    phrase = state.get("phrase") if state.get("phrase") in {"engage", "release"} else None

    if prompt is not None:
        found = detect_phrase(prompt)
        if found is not None:
            phrase = found

    pct = context_percent(payload, root) if prompt is not None else state.get("percent")
    auto_pct = posture["auto_pct"]
    pressure = bool(auto_pct and isinstance(pct, (int, float)) and pct >= auto_pct)

    # ── Precedence ───────────────────────────────────────────────────────────
    if phrase == "release":
        engaged, source = False, "phrase-release"
    elif phrase == "engage":
        engaged, source = True, "phrase"
    elif posture["conserve_tokens"]:
        engaged, source = True, "posture"
    elif pressure:
        engaged, source = True, "context-pressure"
    else:
        engaged, source = False, "none"

    out = {
        "schema_version": SCHEMA_VERSION,
        "engaged": engaged,
        "source": source,
        "phrase": phrase,
        "posture": posture["conserve_tokens"],
        "auto_pct": auto_pct,
        "percent": pct,
        "parallelism": posture["parallelism"],
        "max_workers": posture["max_workers"],
        "changed": engaged != prev_engaged or not state,
        "ts": int(time.time()),
    }
    if prompt is not None:
        write_state(sp, out)
    return out


def _load_payload() -> dict:
    try:
        if sys.stdin.isatty():
            return {}
        raw = sys.stdin.read()
    except Exception:
        return {}
    if not raw.strip():
        return {}
    try:
        obj = json.loads(raw)
    except ValueError:
        return {}
    return obj if isinstance(obj, dict) else {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Conserve-tokens exception resolver")
    ap.add_argument("--mode", choices=("prompt", "read"), default="read")
    ap.add_argument("--project-root", help="Project root (tests)")
    ap.add_argument("--session", help="Session id (tests)")
    ap.add_argument("--prompt", help="Prompt text (tests; normally read from stdin payload)")
    ap.add_argument("--json", action="store_true", help="Emit the full resolution as JSON")
    args = ap.parse_args(argv)

    payload = _load_payload()
    root = Path(args.project_root) if args.project_root else find_project_root(
        Path(payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
    )
    session = args.session or _session_id(payload)

    prompt = None
    if args.mode == "prompt":
        prompt = args.prompt if args.prompt is not None else str(payload.get("prompt") or "")

    res = resolve(payload, root, session, prompt)

    if args.json:
        json.dump(res, sys.stdout, separators=(",", ":"))
        sys.stdout.write("\n")
        return 0

    # prompt mode prints a ONE-LINE directive, and only on a state TRANSITION.
    # A line on every turn would be a per-prompt tax on the context window this
    # feature exists to protect, and repetition trains the reader to skip it.
    if args.mode == "prompt" and res["changed"]:
        if res["engaged"]:
            sys.stdout.write(
                "[ravenclaude] CONSERVE TOKENS engaged (%s). Work sequentially: one "
                "subagent at a time, prefer in-thread work over dispatch, and skip "
                "optional verification fan-out. Say \"maximum parallelism\" to release.\n"
                % res["source"]
            )
        else:
            sys.stdout.write(
                "[ravenclaude] CONSERVE TOKENS released. Default parallelism is "
                "MAXIMUM again: batch every independent step into one message.\n"
            )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # FAIL-SAFE: this rides a UserPromptSubmit hook. It must never be the
        # reason a prompt fails.
        sys.exit(0)
