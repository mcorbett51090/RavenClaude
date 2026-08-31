#!/usr/bin/env python3
"""parallelism-detector.py — measure when independent work ran SERIALLY.

Parallelism defaults to MAXIMUM (v0.273.0), but a default is a wish and a
directive is a wish written down. Neither is measurable, and NEITHER CAN BE
ENFORCED: a hook can stop an action, it cannot compel one. So the third leg is
observation — this module counts what actually happened and hands the number
back, and it deliberately NEVER blocks anything.

THE SIGNAL, and its honest limits.

  Claude Code fires `SubagentStart` per dispatched subagent. Batched dispatches
  (several Agent tool calls in ONE assistant message — the behavior the default
  asks for) arrive as a burst of starts within a second or two of each other.
  Serialized dispatches arrive one at a time, each after the previous finished.

  So a BATCH is defined as: starts separated by <= BATCH_WINDOW_S seconds. A
  batch of size 1 is a SINGLE. Two singles that open within COHESION_S of each
  other are a SERIAL RUN — two independent-looking units of work that one
  message could plausibly have carried.

  ⛔ What this CANNOT know, stated because a metric whose limits are unstated
  gets over-trusted:
    * It cannot know the work was actually INDEPENDENT. Two singles separated
      by a genuine data dependency look identical to two that were needlessly
      serialized. The count is a PROMPT TO LOOK, never a verdict.
    * There is no SubagentStop event wired here, so a "batch" is inferred from
      start-time proximity alone, not from overlap. A slow burst of genuinely
      parallel dispatches could read as singles.
    * A session with no subagents at all reports zero batches, which is not the
      same as perfect parallelism. The reader must not read absence as success.

  Both limits are surfaced verbatim in the read-mode output so the banner cannot
  quietly launder a heuristic into a claim.

WHERE IT WRITES.

  Counters:  .ravenclaude/runs/<session>/parallelism-observations.json
  Events:    .ravenclaude/runs/<session>/hook-events.jsonl, via the caller's
             `_emit_hook_event` (this module only PRINTS a SIGNAL line; the
             bash hook owns the emit so the substrate keeps exactly one writer).

FAIL-SAFE: every path exits 0 and prints nothing on error. Telemetry must never
break the dispatch it is measuring.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

SCHEMA_VERSION = 1

# Starts within this many seconds of each other are ONE batch (one message's
# worth of fan-out). 5s is generous for a burst of tool calls in a single
# assistant turn and far below any plausible sequential turnaround.
BATCH_WINDOW_S = 5
# Two SINGLE batches opening within this window are a serial run. 180s is one
# short back-and-forth; beyond it the two units are probably genuinely separate
# turns of work and calling them "serial" would be noise.
COHESION_S = 180
# Cap the emitted events per session. The counters carry the full tally; the
# event substrate only needs enough to make the pattern visible in Heimdall.
MAX_SIGNALS = 3

_MAX_STATE_BYTES = 256 * 1024


def _session_id(payload: dict) -> str:
    raw = os.environ.get("CLAUDE_SESSION_ID") or payload.get("session_id") or ""
    safe = re.sub(r"[^A-Za-z0-9._-]", "", str(raw))[:128]
    return safe or "unknown"


def find_project_root(start: Path) -> Path:
    try:
        cur = start.resolve()
    except OSError:
        return start
    for cand in (cur, *cur.parents):
        if (cand / ".ravenclaude").is_dir() or (cand / ".git").exists():
            return cand
    return cur


def obs_path(root: Path, session: str) -> Path:
    return root / ".ravenclaude" / "runs" / session / "parallelism-observations.json"


def _read_json(path: Path) -> dict:
    try:
        if not path.is_file() or path.stat().st_size > _MAX_STATE_BYTES:
            return {}
        obj = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return {}
    return obj if isinstance(obj, dict) else {}


def _write_json(path: Path, obj: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(obj, separators=(",", ":")) + "\n", encoding="utf-8")
        tmp.replace(path)
    except OSError:
        pass


def _fresh() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "agents": 0,
        "batches": 0,
        "singles": 0,
        "parallel_batches": 0,
        "max_batch": 0,
        "serial_runs": 0,
        "signals": 0,
        "open_size": 0,
        "open_start": 0,
        "last_start": 0,
        "last_closed_size": 0,
        "last_closed_ts": 0,
    }


def _close_open(st: dict, now: int) -> str | None:
    """Close the currently-open batch. Returns a signal token or None."""
    size = int(st.get("open_size") or 0)
    if size <= 0:
        return None
    st["batches"] = int(st.get("batches") or 0) + 1
    if size == 1:
        st["singles"] = int(st.get("singles") or 0) + 1
    else:
        st["parallel_batches"] = int(st.get("parallel_batches") or 0) + 1
    if size > int(st.get("max_batch") or 0):
        st["max_batch"] = size

    signal = None
    prev_size = int(st.get("last_closed_size") or 0)
    prev_ts = int(st.get("last_closed_ts") or 0)
    if size == 1 and prev_size == 1 and prev_ts and (now - prev_ts) <= COHESION_S:
        st["serial_runs"] = int(st.get("serial_runs") or 0) + 1
        if int(st.get("signals") or 0) < MAX_SIGNALS:
            st["signals"] = int(st.get("signals") or 0) + 1
            signal = "serial-dispatch"

    st["last_closed_size"] = size
    st["last_closed_ts"] = now
    st["open_size"] = 0
    st["open_start"] = 0
    return signal


def observe(root: Path, session: str, now: int) -> str | None:
    st = _read_json(obs_path(root, session)) or _fresh()
    for k, v in _fresh().items():
        st.setdefault(k, v)

    st["agents"] = int(st.get("agents") or 0) + 1
    last = int(st.get("last_start") or 0)
    signal = None
    if st.get("open_size") and last and (now - last) <= BATCH_WINDOW_S:
        st["open_size"] = int(st["open_size"]) + 1
    else:
        signal = _close_open(st, now)
        st["open_size"] = 1
        st["open_start"] = now
    st["last_start"] = now
    _write_json(obs_path(root, session), st)
    return signal


def summarize(root: Path, session: str | None = None, max_sessions: int = 8) -> dict:
    """Aggregate observations across recent run dirs (derived counts only)."""
    runs = root / ".ravenclaude" / "runs"
    files: list[Path] = []
    if session:
        p = obs_path(root, session)
        if p.is_file():
            files.append(p)
    else:
        try:
            cands = [d / "parallelism-observations.json" for d in runs.iterdir() if d.is_dir()]
            cands = [c for c in cands if c.is_file()]
            cands.sort(key=lambda c: c.stat().st_mtime, reverse=True)
            files = cands[:max_sessions]
        except OSError:
            files = []

    total = {"agents": 0, "batches": 0, "singles": 0, "parallel_batches": 0,
             "max_batch": 0, "serial_runs": 0, "sessions": 0}
    for f in files:
        st = _read_json(f)
        if not st:
            continue
        total["sessions"] += 1
        for k in ("agents", "batches", "singles", "parallel_batches", "serial_runs"):
            try:
                total[k] += int(st.get(k) or 0)
            except (TypeError, ValueError):
                pass
        # An open batch has not been counted into `batches` yet; count it so a
        # read taken mid-session does not under-report the work that just ran.
        try:
            if int(st.get("open_size") or 0) > 0:
                total["batches"] += 1
                if int(st["open_size"]) == 1:
                    total["singles"] += 1
                else:
                    total["parallel_batches"] += 1
            total["max_batch"] = max(total["max_batch"], int(st.get("max_batch") or 0),
                                     int(st.get("open_size") or 0))
        except (TypeError, ValueError):
            pass

    batches = total["batches"]
    total["serial_ratio"] = round(total["singles"] / batches, 2) if batches else None
    total["limits"] = (
        "start-time proximity only; a single dispatch may be a genuine data "
        "dependency, and zero batches is 'no subagents ran', not 'perfectly parallel'"
    )
    return total


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
    ap = argparse.ArgumentParser(description="Serial-dispatch detector")
    ap.add_argument("--mode", choices=("observe", "read"), default="read")
    ap.add_argument("--project-root", help="Project root (tests)")
    ap.add_argument("--session", help="Session id (tests)")
    ap.add_argument("--now", type=int, help="Epoch seconds override (tests)")
    args = ap.parse_args(argv)

    payload = _load_payload() if args.mode == "observe" else {}
    root = Path(args.project_root) if args.project_root else find_project_root(
        Path(payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
    )
    session = args.session or _session_id(payload)
    now = args.now if args.now is not None else int(time.time())

    if args.mode == "observe":
        signal = observe(root, session, now)
        if signal:
            # The bash caller turns this into ONE _emit_hook_event line. Keeping
            # the emit in one place means the substrate has exactly one writer.
            sys.stdout.write("SIGNAL %s\n" % signal)
        return 0

    json.dump(summarize(root, args.session), sys.stdout, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
