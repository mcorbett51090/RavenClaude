#!/usr/bin/env python3
"""thing-denial-kb.py — the Thing's denial knowledge base (Muninn, the memory-raven).

When the command-review / decision-review tribunal ("the Thing") DENIES a command
or DEFERS/refuses a decision, it already writes a Sága audit record under
``.ravenclaude/runs/thing/`` (``decisions/*.json`` for decision-review;
``*.json`` for command-review). Those raw records answer *what* was blocked — they
do not tell the next session *why it keeps happening* or *how to get unblocked*.

This tool turns those raw denials into a small, durable, per-repo knowledge base an
agent can consult to **quickly identify the issue and solve it**:

  sync     Read the Sága denial/defer records and materialise each distinct denial
           SHAPE into the KB (dedup by a stable signature), enriched with a known
           resolution from the shipped resolutions map. Hot-path-safe: it only
           READS the existing logs — it never touches the tribunal's live emit path.
  recall   Print the known denial shapes + their resolutions (agent-facing digest).
  resolve  Teach the KB: attach a resolution an agent discovered to a signature, so
           the next session that hits the same denial is handed the fix immediately.
  record   Add one denial event straight from JSON on stdin (direct/in-band capture).

Design contract (matches the repo's hook conventions):
  * stdlib only, no network, py39-compatible;
  * FAIL-SAFE: any internal/runtime error is swallowed and the process still exits 0,
    so a hook that calls this can never break a session (the one non-zero exit is an
    argparse USAGE error — a missing/invalid subcommand exits 2 — which the hooks
    never trigger because they always pass a fixed, valid subcommand);
  * SILENT no-op when the Thing is not in use / no denials exist (never noisy).

The runtime KB lives under ``.ravenclaude/runs/thing/`` (already gitignored). The
seed resolutions map ships in the plugin (``knowledge/thing-denial-resolutions.json``)
and is the committed, cross-consumer knowledge; learned resolutions stay local.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

# ── Path resolution ────────────────────────────────────────────────────────────
# The seed resolutions map ships beside this script: scripts/ -> ../knowledge/.
_SEED_RESOLUTIONS = (
    Path(__file__).resolve().parent.parent / "knowledge" / "thing-denial-resolutions.json"
)


def _project_root(explicit: str | None) -> Path:
    """Consumer project root: --root, else $CLAUDE_PROJECT_DIR, else cwd."""
    if explicit:
        return Path(explicit).resolve()
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(env).resolve() if env else Path.cwd().resolve()


def _thing_dir(root: Path) -> Path:
    return root / ".ravenclaude" / "runs" / "thing"


def _kb_path(root: Path) -> Path:
    return _thing_dir(root) / "denial-kb.jsonl"


def _cursor_path(root: Path) -> Path:
    return _thing_dir(root) / "denial-kb-cursor.json"


def _learned_path(root: Path) -> Path:
    return _thing_dir(root) / "denial-learned.json"


# ── Small IO helpers (all soft — a bad file is treated as absent) ───────────────
def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


# Secret-shaped patterns — a Python port of hooks/_scrub.sh `_secret_patterns`
# (ERE). SOURCE OF TRUTH is hooks/_scrub.sh / scripts/thing-seat.sh /
# knowledge/concerns-catalog.md — keep this list in sync with those. sample +
# reasoning are scrubbed BEFORE they are stored or emitted, so a denied
# `curl … Bearer …` never lands in the KB on disk or in the recall digest (the
# substrate-wide secret-scrub invariant, v0.110.0 / v0.113.1).
_SECRET_RES = [
    re.compile(p)
    for p in (
        r"AKIA[0-9A-Z]{12,}",
        r"sk-(?:ant-)?[A-Za-z0-9-]{20,}",
        r"sk_live_[A-Za-z0-9]{24,}",
        r"rk_live_[A-Za-z0-9]{24,}",
        r"ghp_[A-Za-z0-9]{30,}",
        r"github_pat_[A-Za-z0-9_]{20,}",
        r"glpat-[A-Za-z0-9_-]{15,}",
        r"xox[baprs]-[A-Za-z0-9-]{10,}",
        r"AIza[0-9A-Za-z_-]{30,}",
        r"npm_[A-Za-z0-9]{30,}",
        r"hf_[A-Za-z0-9]{30,}",
        r"AccountKey=[A-Za-z0-9+/=]{20,}",
        r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"--password[=\s]\S+",
        r"--token[=\s]\S+",
        r"(?:https?|postgres(?:ql)?|mysql|mongodb|redis|amqp|smtp)s?://"
        r"[A-Za-z0-9._-]{2,}:[A-Za-z0-9._%+-]{4,}@",
    )
]
# The short `-p<value>` flag keeps its leading boundary; only the value redacts.
_SECRET_P_FLAG = re.compile(r"(^|\s)-p[^\s\d]\S{15,}")


def _scrub_secrets(text: str) -> str:
    """Redact secret-shaped tokens (mirrors hooks/_scrub.sh). Fail-safe toward
    redaction: on any error, return a wholesale-redacted marker rather than risk
    leaking the input."""
    if not text:
        return text
    try:
        out = _SECRET_P_FLAG.sub(lambda m: m.group(1) + "[REDACTED]", text)
        for rx in _SECRET_RES:
            out = rx.sub("[REDACTED]", out)
        return out
    except Exception:
        return "[REDACTED]"


def _clip(text: str, n: int = 200) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


def _sig(source: str, key: str) -> str:
    return hashlib.sha1(f"{source}|{key}".encode()).hexdigest()[:12]


# ── Event extraction: raw Sága record -> normalised denial event ────────────────
def _reason_class(rec: dict) -> str:
    """Group decision-review defers/refusals by *why*, not by the (unique) question."""
    if rec.get("high_blast"):
        return "high-blast-defer"
    reason = (rec.get("reasoning") or "").lower()
    if "injection" in reason:
        return "injection-defer"
    if "abstain" in reason or "low confidence" in reason or "low-confidence" in reason:
        return "low-confidence-defer"
    if "split" in reason:
        return "split-defer"
    if (rec.get("final_verdict") or "") == "no":
        return "policy-no"
    return "policy-defer"


def _event_from_decision(rec: dict) -> dict | None:
    verdict = (rec.get("final_verdict") or "").lower()
    # A "yes" did not block the agent; only no/defer are "denials" worth learning.
    if verdict not in ("no", "defer"):
        return None
    rclass = _reason_class(rec)
    return {
        "source": "decision-review",
        "category": rclass,
        "verdict": verdict,
        "key": rclass,
        "sample": _clip(_scrub_secrets(rec.get("question", ""))),
        "reasoning": _clip(_scrub_secrets(rec.get("reasoning", "")), 300),
        "timestamp": rec.get("timestamp", ""),
    }


def _event_from_command(rec: dict) -> dict | None:
    verdict = (rec.get("final_verdict") or "").lower()
    if verdict != "deny":
        return None
    category = rec.get("category") or rec.get("tool_name") or "command"
    ti = rec.get("tool_input") or rec.get("saga_tool_input") or {}
    cmd = ti.get("command", "") if isinstance(ti, dict) else ""
    concerns = rec.get("concerns_cited") or []
    # Scrub BEFORE deriving the head so a secret can't leak into the (hashed) key.
    scrubbed_cmd = _scrub_secrets(cmd)
    head = " ".join((scrubbed_cmd or category).split()[:6])
    reasoning = ", ".join(concerns) if concerns else _scrub_secrets(rec.get("reasoning", ""))
    return {
        "source": "command-review",
        "category": category,
        "verdict": verdict,
        "key": f"{category}:{head}",
        "sample": _clip(scrubbed_cmd or category),
        "reasoning": _clip(reasoning, 300),
        "timestamp": rec.get("timestamp", ""),
    }


def _iter_source_records(root: Path):
    """Yield (filepath, kind, record) for every Sága denial log, newest last."""
    tdir = _thing_dir(root)
    decisions = tdir / "decisions"
    if decisions.is_dir():
        for f in sorted(decisions.glob("*.json")):
            rec = _read_json(f, None)
            if isinstance(rec, dict):
                yield f, "decision", rec
    if tdir.is_dir():
        for f in sorted(tdir.glob("*.json")):
            # command-review records sit at the thing/ root; skip our own KB sidecars.
            if f.name in ("denial-kb-cursor.json", "denial-learned.json"):
                continue
            rec = _read_json(f, None)
            if isinstance(rec, dict):
                yield f, "command", rec


# ── Resolution matching ─────────────────────────────────────────────────────────
def _load_rules() -> list:
    data = _read_json(_SEED_RESOLUTIONS, {})
    rules = data.get("rules", []) if isinstance(data, dict) else []
    return rules if isinstance(rules, list) else []


def _match_resolution(event: dict, rules: list) -> tuple[str | None, str | None, str | None]:
    """First matching rule wins -> (resolution, doc, rule_id). None if unmatched."""
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        m = rule.get("match", {})
        if m.get("source") and m["source"] != event["source"]:
            continue
        if m.get("verdict") and m["verdict"] != event["verdict"]:
            continue
        cat = m.get("category")
        if cat and not re.search(cat, str(event.get("category", "")), re.I):
            continue
        pat = m.get("pattern")
        if pat and not re.search(
            pat, f"{event.get('sample', '')} {event.get('reasoning', '')}", re.I
        ):
            continue
        return rule.get("resolution"), rule.get("doc"), rule.get("id")
    return None, None, None


# ── sync ────────────────────────────────────────────────────────────────────────
def cmd_sync(root: Path) -> int:
    tdir = _thing_dir(root)
    if not tdir.is_dir():
        return 0  # the Thing has never run here — nothing to learn, stay silent.

    cursor = _read_json(_cursor_path(root), {}) or {}
    processed = set(cursor.get("processed", []))
    learned = _read_json(_learned_path(root), {}) or {}
    rules = _load_rules()

    # Load the current materialised KB keyed by signature.
    kb: dict[str, dict] = {}
    kb_file = _kb_path(root)
    if kb_file.is_file():
        for line in kb_file.read_text(encoding="utf-8").splitlines():
            row = _read_json_line(line)
            if row and row.get("signature"):
                kb[row["signature"]] = row

    new_events = 0
    for filepath, kind, rec in _iter_source_records(root):
        token = str(filepath)
        if token in processed:
            continue
        processed.add(token)
        event = _event_from_decision(rec) if kind == "decision" else _event_from_command(rec)
        if not event:
            continue
        new_events += 1
        sig = _sig(event["source"], event["key"])
        entry = kb.get(sig)
        if entry is None:
            resolution, doc, rule_id = _match_resolution(event, rules)
            learned_hit = learned.get(sig)
            entry = {
                "signature": sig,
                "source": event["source"],
                "category": event["category"],
                "verdict": event["verdict"],
                "first_seen": event["timestamp"],
                "last_seen": event["timestamp"],
                "count": 0,
                "sample": event["sample"],
                "reasoning": event["reasoning"],
                "resolution": (learned_hit or {}).get("resolution") or resolution,
                "resolution_source": "learned" if learned_hit else ("seed" if resolution else None),
                "doc": (learned_hit or {}).get("doc") or doc,
                "rule_id": rule_id,
            }
            kb[sig] = entry
        entry["count"] += 1
        if event["timestamp"] and event["timestamp"] >= entry.get("last_seen", ""):
            entry["last_seen"] = event["timestamp"]
            entry["sample"] = event["sample"]

    _write_kb(root, kb)
    cursor["processed"] = sorted(processed)
    _atomic_write(_cursor_path(root), json.dumps(cursor, indent=1))
    if new_events:
        unresolved = sum(1 for e in kb.values() if not e.get("resolution"))
        print(
            f"thing-denial-kb: +{new_events} denial event(s); "
            f"{len(kb)} shape(s) known, {unresolved} without a resolution.",
            file=sys.stderr,
        )
    return 0


def _read_json_line(line: str):
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return None


def _write_kb(root: Path, kb: dict) -> None:
    rows = sorted(kb.values(), key=lambda e: e.get("last_seen", ""), reverse=True)
    body = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
    _atomic_write(_kb_path(root), body + ("\n" if body else ""))


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Per-PROCESS temp name: on SessionStart this marketplace has BOTH the plugin
    # and the dev-mirror wiring active, so two `sync` runs can fire concurrently;
    # a shared ".tmp" would race the write+swap and could publish a torn file.
    tmp = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
    except Exception:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


# ── recall ──────────────────────────────────────────────────────────────────────
def cmd_recall(root: Path, limit: int, unresolved_only: bool, as_json: bool) -> int:
    kb_file = _kb_path(root)
    rows = []
    if kb_file.is_file():
        for line in kb_file.read_text(encoding="utf-8").splitlines():
            row = _read_json_line(line)
            if row:
                rows.append(row)
    if unresolved_only:
        rows = [r for r in rows if not r.get("resolution")]
    rows = rows[: max(0, limit)] if limit else rows

    if as_json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0
    if not rows:
        return 0  # silent when empty — safe for a SessionStart hook.

    lines = ["Thing-denial knowledge base — known blocks the tribunal has raised here:"]
    for r in rows:
        # DERIVED LABELS ONLY in the human-readable digest (source / category /
        # count / signature + the TRUSTED resolution) — the `sample` is a raw
        # denied command/question and is NEVER emitted here, matching the repo's
        # derived-labels-only invariant (capability-orientation.sh / watch-run-
        # state.sh / Gate 19): this text is injected into session context by the
        # SessionStart recall hook, so a hostile sample must not ride along. The
        # (secret-scrubbed) sample is available on demand via `recall --json` only.
        tag = f"[{r.get('source')}/{r.get('category')}] ×{r.get('count', 1)}"
        lines.append(f"\n• {tag}  (sig {r.get('signature')})")
        if r.get("resolution"):
            src = r.get("resolution_source") or "seed"
            lines.append(f"    ✅ resolution ({src}): {r['resolution']}")
            if r.get("doc"):
                lines.append(f"    ↪ see: {r['doc']}")
        else:
            lines.append(
                "    ⚠ no known resolution yet — once you get past this block, teach the KB:\n"
                f"       thing-denial-kb.py resolve --signature {r.get('signature')} "
                '--resolution "<how you solved it>"'
            )
    print("\n".join(lines))
    return 0


# ── resolve ──────────────────────────────────────────────────────────────────────
def cmd_resolve(root: Path, signature: str, resolution: str, doc: str | None) -> int:
    learned = _read_json(_learned_path(root), {}) or {}
    learned[signature] = {"resolution": resolution, "doc": doc}
    _atomic_write(_learned_path(root), json.dumps(learned, indent=1, ensure_ascii=False))
    # Fold it straight into the materialised KB so `recall` reflects it now.
    kb_file = _kb_path(root)
    if kb_file.is_file():
        kb: dict[str, dict] = {}
        for line in kb_file.read_text(encoding="utf-8").splitlines():
            row = _read_json_line(line)
            if row and row.get("signature"):
                kb[row["signature"]] = row
        if signature in kb:
            kb[signature]["resolution"] = resolution
            kb[signature]["resolution_source"] = "learned"
            kb[signature]["doc"] = doc
            _write_kb(root, kb)
    print(f"thing-denial-kb: learned a resolution for {signature}.", file=sys.stderr)
    return 0


# ── record (direct/in-band capture) ──────────────────────────────────────────────
def cmd_record(root: Path) -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return 0
    if not isinstance(payload, dict) or not payload.get("source"):
        return 0
    event = {
        "source": str(payload.get("source")),
        "category": str(payload.get("category", "command")),
        "verdict": str(payload.get("verdict", "deny")),
        "key": str(payload.get("key") or payload.get("category") or "command"),
        "sample": _clip(_scrub_secrets(str(payload.get("sample", "")))),
        "reasoning": _clip(_scrub_secrets(str(payload.get("reasoning", ""))), 300),
        "timestamp": str(payload.get("timestamp", "")),
    }
    rules = _load_rules()
    learned = _read_json(_learned_path(root), {}) or {}
    kb: dict[str, dict] = {}
    kb_file = _kb_path(root)
    if kb_file.is_file():
        for line in kb_file.read_text(encoding="utf-8").splitlines():
            row = _read_json_line(line)
            if row and row.get("signature"):
                kb[row["signature"]] = row
    sig = _sig(event["source"], event["key"])
    entry = kb.get(sig)
    if entry is None:
        resolution, doc, rule_id = _match_resolution(event, rules)
        learned_hit = learned.get(sig)
        entry = {
            "signature": sig,
            "source": event["source"],
            "category": event["category"],
            "verdict": event["verdict"],
            "first_seen": event["timestamp"],
            "last_seen": event["timestamp"],
            "count": 0,
            "sample": event["sample"],
            "reasoning": event["reasoning"],
            "resolution": (learned_hit or {}).get("resolution") or resolution,
            "resolution_source": "learned" if learned_hit else ("seed" if resolution else None),
            "doc": (learned_hit or {}).get("doc") or doc,
            "rule_id": rule_id,
        }
        kb[sig] = entry
    entry["count"] += 1
    entry["last_seen"] = event["timestamp"] or entry.get("last_seen", "")
    _write_kb(root, kb)
    # Echo the resolution so a caller can surface it in-band at denial time.
    if entry.get("resolution"):
        print(entry["resolution"])
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--root", help="Project root (default: $CLAUDE_PROJECT_DIR or cwd).")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sync", help="Materialise new tribunal denials into the KB.")
    rc = sub.add_parser("recall", help="Print known denials + resolutions.")
    rc.add_argument("--limit", type=int, default=0, help="Max shapes to print (0 = all).")
    rc.add_argument("--unresolved", action="store_true", help="Only shapes lacking a resolution.")
    rc.add_argument("--json", action="store_true", help="Emit raw JSON.")
    rs = sub.add_parser("resolve", help="Teach the KB a resolution for a signature.")
    rs.add_argument("--signature", required=True)
    rs.add_argument("--resolution", required=True)
    rs.add_argument("--doc", default=None)
    sub.add_parser("record", help="Add one denial event from JSON on stdin.")
    args = p.parse_args()

    root = _project_root(args.root)
    if args.cmd == "sync":
        return cmd_sync(root)
    if args.cmd == "recall":
        return cmd_recall(root, args.limit, args.unresolved, args.json)
    if args.cmd == "resolve":
        return cmd_resolve(root, args.signature, args.resolution, args.doc)
    if args.cmd == "record":
        return cmd_record(root)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # fail-safe: never break a hook or a session.
        print(f"thing-denial-kb: soft error ({exc.__class__.__name__}): {exc}", file=sys.stderr)
        sys.exit(0)
