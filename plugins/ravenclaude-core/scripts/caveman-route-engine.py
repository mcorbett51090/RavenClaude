#!/usr/bin/env python3
"""caveman-route-engine.py — P3 of the caveman auto-routing plan (SHADOW only).

Full design: `.ravenclaude/runs/forge/caveman-routing-decision-tree/plan.md`,
section "P3 — Hook body, wired in SHADOW". This is the C2-(c) "bare .py engine
invoked from inside an already-registered .sh wrapper" escape — the sanctioned
counterpart of `compact-anchor.sh` -> `compact-anchor.py`. It is invoked ONLY by
`caveman-route-hook.sh`, never registered as a hook itself.

WHAT THIS DOES (and does not do)
---------------------------------
Reads the hook payload (SessionStart or UserPromptSubmit) on stdin, loads the
incremental cursor/streak state for this session, calls `caveman-route.py`'s
pure `classify()` function directly (imported by file path — no subprocess),
persists the returned cursor/streak, and appends ONE decision line to the
per-session route log.

**SHADOW is what "enabled" means in this phase.** The bash wrapper already
gated on `caveman_routing: shadow|live` before this engine ever runs (the O(1)
short-circuit), so by the time this file executes, the posture is confirmed to
be `shadow` or `live`. Both are treated IDENTICALLY here: decide + record,
**never call the applier**. `live` mode's actual "call caveman-apply-mode.sh"
behavior is NOT wired until a later phase (P7) — see the commented-out
placeholder block near the bottom of `main()`. Nothing above that comment
executes an applier call, in either mode, in this phase.

STATE FILE SHARING WITH THE APPLIER (P2)
-----------------------------------------
Per plan.md, both this engine's cursor/streak state AND `caveman-apply-mode.sh`'s
own entry-snapshot (`user_mode_at_entry` / `legacy_mirror_at_entry` /
`manual_override`) persist to the SAME path:
`.ravenclaude/runs/<session_id>/caveman-route-state.json`. Since P2's applier
(when eventually invoked) does a whole-object overwrite of that file with only
its own five keys, this engine deliberately does a READ-MERGE-WRITE (never a
blind overwrite) so an applier snapshot already on disk is never clobbered by a
router write, and vice versa in the direction this engine controls.

DERIVED VALUES ONLY (C8)
-------------------------
The route-log entry below is built exclusively from `classify()`'s own output
(already a fixed-enum/derived-integer contract per C8 — see
`caveman-route.py`'s own docstring) plus a handful of values this engine itself
computes (elapsed_ms, event, applied=False). No raw transcript/prompt/tool
content is ever read by this file — the classifier owns the transcript read and
already guarantees C8 by construction.

FAIL-OPEN, UNCONDITIONALLY
----------------------------
Every code path in `main()` ends in `return 0`. A malformed payload, an
unreadable/corrupt state file, a classifier exception, or a failed log write
each degrade to "did nothing further this call" — never a crash, never a
non-zero exit. `caveman-route-hook.sh`'s own EXIT trap is the second line of
defense should this file somehow be invoked in a way that raises before
`main()` returns.
"""

from __future__ import annotations  # stock macOS ships Python 3.9

import importlib.util
import json
import os
import sys
import time
from pathlib import Path

_STATE_FILENAME = "caveman-route-state.json"
_LOG_FILENAME = "caveman-route.jsonl"

# The keys this engine owns in the shared state file. Anything else already
# present (the applier's own snapshot keys) is preserved verbatim on every
# read-merge-write.
_ROUTER_STATE_KEYS = ("cursor_byte", "streak", "verdict", "event", "updated_at")

_MAX_SESSION_LEN = 128


def _load_classifier():
    """Import caveman-route.py by file path (a sibling of this script). Never
    a subprocess — the classifier's own `classify()` is the designed pure
    entry point (its own docstring: "Usage: echo ... | caveman-route.py")."""
    path = Path(__file__).resolve().parent / "caveman-route.py"
    spec = importlib.util.spec_from_file_location("rc_caveman_route", str(path))
    if spec is None or spec.loader is None:
        raise ImportError("cannot load caveman-route.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sanitize_session_id(value):
    """Path-safe session-id token, mirroring compact-anchor.py's own
    fallback. A missing/garbage session id -> "unknown" rather than a
    traversal-shaped path."""
    if not isinstance(value, str) or not value:
        return None
    cleaned = "".join(ch for ch in value if ch.isalnum() or ch in "._-")[:_MAX_SESSION_LEN]
    if cleaned in ("", ".", ".."):
        return None
    return cleaned


def _read_state(state_path: Path) -> dict:
    try:
        raw = state_path.read_text(encoding="utf-8")
    except OSError:
        return {}
    try:
        obj = json.loads(raw)
    except ValueError:
        return {}  # corrupt/malformed state -> treated as absent, never raised
    return obj if isinstance(obj, dict) else {}


def _write_state_merged(state_path: Path, updates: dict) -> None:
    """Read-merge-write, atomic. Preserves any keys this engine does not own
    (e.g. the applier's `user_mode_at_entry` snapshot) — see the module
    docstring's "STATE FILE SHARING WITH THE APPLIER" section."""
    state = _read_state(state_path)
    state.update(updates)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_path.with_name(state_path.name + f".tmp-{os.getpid()}")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    tmp.replace(state_path)


def _append_route_log(log_path: Path, entry: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    try:
        os.chmod(log_path, 0o600)
    except OSError:
        pass


def _parse_event_arg(argv) -> str:
    event = "prompt"
    if "--event" in argv:
        i = argv.index("--event")
        if i + 1 < len(argv) and argv[i + 1] in ("prompt", "session"):
            event = argv[i + 1]
    return event


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    event = _parse_event_arg(argv)

    try:
        raw_in = sys.stdin.read()
    except Exception:
        raw_in = ""
    try:
        payload = json.loads(raw_in) if raw_in.strip() else {}
    except ValueError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if not project_dir:
        return 0  # nothing to scope state/log to — no writes, no crash

    session_id = _sanitize_session_id(payload.get("session_id")) or _sanitize_session_id(
        os.environ.get("CLAUDE_SESSION_ID")
    )
    if not session_id:
        return 0  # malformed/absent session id -> no state, no writes

    transcript_path = payload.get("transcript_path")
    if not isinstance(transcript_path, str) or not transcript_path:
        return 0  # malformed payload -> no state corruption, exit 0 (acceptance test d)

    project_root = Path(project_dir)
    run_dir = project_root / ".ravenclaude" / "runs" / session_id
    state_path = run_dir / _STATE_FILENAME
    log_path = run_dir / _LOG_FILENAME

    prior_state = _read_state(state_path)
    cursor_in = prior_state.get("cursor_byte")
    if not isinstance(cursor_in, int) or isinstance(cursor_in, bool):
        cursor_in = None
    prior_verdict = prior_state.get("verdict")
    streak_in = prior_state.get("streak")
    if not isinstance(streak_in, int) or isinstance(streak_in, bool):
        streak_in = None

    try:
        classifier = _load_classifier()
    except Exception:
        return 0  # classifier missing/broken -> fail-open, no crash

    classify_input = {
        "transcript_path": transcript_path,
        "session_id": session_id,
        "cursor_byte": cursor_in,
        "prior_verdict": prior_verdict,
        "streak": streak_in,
    }

    start = time.monotonic()
    try:
        result = classifier.classify(classify_input, project_root=project_root)
    except Exception:
        return 0  # a torn/malformed transcript is the classifier's own job to
        # survive (it already does — see caveman-route.py's torn-line and
        # malformed-json fixtures); this is defense-in-depth only.
    elapsed_ms = int((time.monotonic() - start) * 1000)

    if not isinstance(result, dict):
        return 0

    verdict = result.get("verdict") if result.get("verdict") in ("on", "off", "hold") else "hold"
    why = result.get("why") if isinstance(result.get("why"), str) else "hold:no-data"
    mode = result.get("mode") if result.get("mode") in ("off", "shadow", "live") else "off"
    metrics = result.get("metrics") if isinstance(result.get("metrics"), dict) else {}
    new_cursor = result.get("cursor_byte")
    if not isinstance(new_cursor, int) or isinstance(new_cursor, bool):
        new_cursor = cursor_in if isinstance(cursor_in, int) else 0
    new_streak = result.get("streak")
    if not isinstance(new_streak, int) or isinstance(new_streak, bool):
        new_streak = 0

    # ── persist cursor/streak state (merge — never clobber the applier's own
    #    snapshot keys, since caveman-apply-mode.sh shares this file path) ──
    try:
        _write_state_merged(
            state_path,
            {
                "cursor_byte": new_cursor,
                "streak": new_streak,
                "verdict": verdict,
                "event": event,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )
    except Exception:
        pass  # persistence failure -> still log the decision below; next call
        # simply re-bootstraps rather than incrementally advancing

    applied = False  # ⛔ P3 SHADOW FLOOR — always False in this phase, in
    # either "shadow" or "live" mode. This assignment is deliberately OUTSIDE
    # and AHEAD of the placeholder block below, so even a careless partial
    # edit of that block cannot make `applied` start anything but False.

    # =========================================================================
    # ⛔ P7 PLACEHOLDER — DO NOT UNCOMMENT IN THIS PHASE (P3 is SHADOW ONLY) ⛔
    # =========================================================================
    # This is the ONLY place a future phase (P7) will ever call the applier.
    # In P3, mode "shadow" AND mode "live" both stop here — decide + record,
    # NEVER apply. Uncommenting this block (Gate: P3's self-test proves this
    # exact mutation — strip the "# CAVEMAN_P7:" prefix below — changes the
    # caveman session mode file) without ALSO completing P7's own entry-gate
    # (offline replay correlation + >=10 live shadow sessions, per plan.md)
    # would open the one-way door before it is meant to open.
    #
    # CAVEMAN_P7:if mode == "live" and verdict != prior_verdict:
    # CAVEMAN_P7:    import subprocess
    # CAVEMAN_P7:    apply_script = Path(__file__).resolve().parent / "caveman-apply-mode.sh"
    # CAVEMAN_P7:    subprocess.run(
    # CAVEMAN_P7:        ["bash", str(apply_script), session_id, verdict],
    # CAVEMAN_P7:        env=os.environ,
    # CAVEMAN_P7:        stdout=subprocess.DEVNULL,
    # CAVEMAN_P7:        stderr=subprocess.DEVNULL,
    # CAVEMAN_P7:        timeout=10,
    # CAVEMAN_P7:    )
    # CAVEMAN_P7:    applied = True
    # =========================================================================

    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": event,
        "mode": mode,
        "verdict": verdict,
        "why": why,
        "streak": new_streak,
        "elapsed_ms": elapsed_ms,
        "applied": applied,
        "responses_in_window": metrics.get("responses_in_window"),
        "tool_use_total": metrics.get("tool_use_total"),
        "avg_tool_use_per_response": metrics.get("avg_tool_use_per_response"),
    }
    try:
        _append_route_log(log_path, entry)
    except Exception:
        pass  # log write failure -> silent, never a crash (fail-open)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Belt-and-braces: this hook must never be the reason a turn/session
        # start reports an error. See caveman-route-hook.sh's own EXIT trap
        # for the second layer of the same invariant.
        sys.exit(0)
