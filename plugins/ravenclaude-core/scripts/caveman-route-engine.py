#!/usr/bin/env python3
"""caveman-route-engine.py — P3+P4+P5 of the caveman auto-routing plan (SHADOW only).

Full design: `.ravenclaude/runs/forge/caveman-routing-decision-tree/plan.md`,
sections "P3 — Hook body, wired in SHADOW", "P4 — SessionStart re-arm and
the reset race", and "P5 — Observability + offline replay calibration". This
is the C2-(c) "bare .py engine invoked from inside an
already-registered .sh wrapper" escape — the sanctioned counterpart of
`compact-anchor.sh` -> `compact-anchor.py`. It is invoked ONLY by
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
`<scope_dir>/.ravenclaude/runs/<session_id>/caveman-route-state.json` (see "STATE
SCOPING" below for `<scope_dir>`). Since P2's applier (when eventually invoked)
does a whole-object overwrite of that file with only its own five keys, this
engine deliberately does a READ-MERGE-WRITE (never a blind overwrite) so an
applier snapshot already on disk is never clobbered by a router write, and vice
versa in the direction this engine controls.

STATE SCOPING (P4) — cwd, not just session_id
-----------------------------------------------
`_resolve_scope_dir()` bases the run dir on the trusted payload's own `cwd`
(falling back to `CLAUDE_PROJECT_DIR`, then the process cwd), mirroring
`runaway-brake.sh`'s own `rc-state-key` convention. `CLAUDE_PROJECT_DIR` is
resolved once at session start and does not vary across sibling worktrees
sharing one `session_id` — so two agents in two worktrees under one session
must not share this file, or one worktree's routing hysteresis leaks into the
other's. A payload with no `cwd` (e.g. this engine's own P3 self-test
fixtures) degrades byte-identically to the pre-P4 behavior.

SESSIONSTART RE-ARM — reset vs preserve (P4)
-----------------------------------------------
Caveman itself (`caveman-activate.js`) re-derives `getDefaultMode()` only on
`RESET_SOURCES = {startup, clear}`; `compact`/`resume`/`fork` read the stored
mode. This engine mirrors that split for its OWN cursor/streak/verdict: on
`startup`/`clear` (SessionStart only — `event == "session"`), whatever is on
disk is discarded and `cursor_in`/`prior_verdict`/`streak_in` are forced to
`None`, driving `classify()`'s own bootstrap path (verdict forced "off",
regardless of window content — the safe direction). Every other source
(`resume`/`fork`/`compact`/absent) — and every `UserPromptSubmit` call, which
carries no `source` field at all — preserves whatever is stored, exactly as
before. See `_RESET_SOURCES` below for the full rationale; the route-log
entry records both the raw `source` and the derived `reset` boolean.

P5 — OBSERVABILITY (transition-only emission + flap tracking)
-----------------------------------------------------------------
Every route-log entry now also carries `tool_uses_in_window` and
`flap_count` (plan.md's P5 schema). `flap_count` is a CUMULATIVE,
session-scoped counter of real on<->off flips (never counting a flip
through "hold" as zero — see main()'s "P5 observability" block). On a real
TRANSITION (verdict is "on"/"off" and differs from this session's own
prior-call verdict — NEVER on "hold", per the v0.273.0 lesson that emitting
the allow-path buries the denies) this engine prints exactly one
`SIGNAL <verdict-token>` line to stdout; the BASH caller
(`caveman-route-hook.sh`) is the sole writer into `hook-events.jsonl`,
mirroring `parallelism-detector.py`'s own "print a signal, let the shell own
the emit" convention. The token is drawn from the plan's fixed enum (C8) —
see the block right before `return 0` in `main()` for the full mapping and
which five of the seven tokens are reserved for P7 (unreachable here because
the applier is never invoked in this phase).

DERIVED VALUES ONLY (C8)
-------------------------
The route-log entry below is built exclusively from `classify()`'s own output
(already a fixed-enum/derived-integer contract per C8 — see
`caveman-route.py`'s own docstring) plus a handful of values this engine itself
computes (elapsed_ms, event, applied=False) or copies verbatim from the trusted
hook payload's own bounded enum field (`source`, one of
`startup|resume|clear|fork|compact|None` per Claude Code's own SessionStart
contract) plus a boolean this engine derives from it (`reset`). No raw
transcript/prompt/tool content is ever read by this file — the classifier owns
the transcript read and already guarantees C8 by construction.

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
# read-merge-write. `flap_count`/`last_definite_verdict` are P5 additions —
# see "P5 observability" in main() for what they track and why.
_ROUTER_STATE_KEYS = (
    "cursor_byte",
    "streak",
    "verdict",
    "event",
    "updated_at",
    "flap_count",
    "last_definite_verdict",
)

_MAX_SESSION_LEN = 128

# P4 (plan.md "SessionStart re-arm and the reset race") — mirrors caveman's
# own `RESET_SOURCES = {startup, clear}` (caveman-activate.js). On these two
# `SessionStart` sources caveman itself re-derives `getDefaultMode()` from
# scratch, discarding whatever mode it had stored; the router's OWN
# cursor/streak/verdict must be discarded in lockstep, or a stale hysteresis
# value could recommend flipping caveman away from the user's just-reset
# default on the very next classification — silently overriding a `/clear`.
# `resume`/`fork`/`compact` (and any other or absent `source`, including a
# fabricated one) all PRESERVE — caveman itself reads the stored mode on
# those sources, so the router keeps its own state too, or the two go out of
# sync and the router spends a full enable-streak re-earning a state caveman
# already holds. This only applies to `event == "session"` (SessionStart);
# `event == "prompt"` (UserPromptSubmit) carries no `source` field at all and
# always preserves.
_RESET_SOURCES = ("startup", "clear")

# Every `source` value Claude Code's own SessionStart contract is documented to
# send (the `startup|resume|clear|fork` matcher this hook is registered under,
# plus `compact`, which this plugin registers no hook for but which the wider
# codebase — compact-anchor.sh — already treats as real). A value outside
# this set (a malformed/fabricated payload) is logged as `None`, matching the
# fixed-enum discipline of every other DERIVED VALUES ONLY field in this file
# (C8) — it never disables the reset/preserve decision, which is keyed off
# `_RESET_SOURCES` membership regardless of what gets logged.
_KNOWN_SOURCES = ("startup", "resume", "clear", "fork", "compact")


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


def _resolve_scope_dir(payload: dict, project_dir: str) -> Path:
    """Base directory for this call's state file + route log.

    P4 (plan.md "State scoping"): matches `runaway-brake.sh`'s own
    `rc-state-key` convention — `"${cwd}/.ravenclaude/runs/..." + session_id`
    — because `CLAUDE_PROJECT_DIR` is resolved ONCE at session start and does
    NOT vary across sibling worktrees sharing one `session_id`; the trusted
    hook payload's own `cwd` field is the per-worktree component that makes
    the scoping correct (confirmed present on SessionStart's own payload "on
    every host observed" per `worktree-guard.sh`'s own comment, and on
    UserPromptSubmit for the hosts observed to send it).

    Falls back to `project_dir` (`CLAUDE_PROJECT_DIR` — the pre-P4 behavior,
    preserved byte-for-byte for any payload with no `cwd`, e.g. this
    engine's own P3 self-test fixtures) and finally to the process cwd,
    mirroring `runaway-brake.sh`'s own `[ -z "$cwd" ] && cwd="$PWD"`.
    """
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd:
        return Path(cwd)
    if project_dir:
        return Path(project_dir)
    return Path(os.getcwd())


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

    project_root = _resolve_scope_dir(payload, project_dir)
    run_dir = project_root / ".ravenclaude" / "runs" / session_id
    state_path = run_dir / _STATE_FILENAME
    log_path = run_dir / _LOG_FILENAME

    prior_state = _read_state(state_path)

    # `source` is only ever meaningful on a SessionStart ("session") event —
    # UserPromptSubmit ("prompt") carries no such field, and always preserves.
    # Anything outside the known enum (a malformed/fabricated payload) is
    # normalized to None rather than logged verbatim — C8 (derived values
    # only). This never disables reset/preserve, which is keyed off
    # `_RESET_SOURCES` membership on the RAW value, so a fabricated source
    # this engine has never heard of still safely PRESERVES (the same
    # outcome as `compact`/`resume`/`fork`) rather than accidentally
    # resetting on an unrecognized string.
    raw_source = payload.get("source") if event == "session" else None
    is_reset = isinstance(raw_source, str) and raw_source in _RESET_SOURCES
    source = raw_source if isinstance(raw_source, str) and raw_source in _KNOWN_SOURCES else None

    if is_reset:
        # ── RESET (startup|clear) — discard whatever is on disk and
        # re-derive from scratch, exactly like a brand-new session's
        # first-ever call: cursor_byte=None drives classify()'s own
        # bootstrap path, which forces verdict "off" regardless of window
        # content (the safe direction) — matching caveman's own
        # getDefaultMode() re-derivation on these two sources.
        cursor_in = None
        prior_verdict = None
        streak_in = None
    else:
        # ── PRESERVE (resume|fork|compact|any other/absent source, and
        # every UserPromptSubmit call) — read whatever this session already
        # has, exactly as P3 always did.
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

    # ── P5 observability: flap tracking + transition detection ─────────────
    # `flap_count` (plan.md P5 schema, R7) is a CUMULATIVE, session-scoped
    # counter of real on<->off flips, tracked against the last DEFINITE
    # (non-"hold") verdict this session ever produced — never against the
    # immediately-prior call's raw verdict, which may itself have been
    # "hold" and would otherwise silently swallow a flip that happened
    # "through" a hold in between (on -> hold -> off must still count as
    # one flip, not zero). `prior_state.get("verdict")` (the raw value from
    # the LAST call, hold included) is what decides EMIT-a-transition-event
    # below — that is a different question ("did anything change since the
    # last call") from flap counting ("has the routing decision itself
    # oscillated").
    prior_definite = prior_state.get("last_definite_verdict")
    prior_definite = prior_definite if prior_definite in ("on", "off") else None
    flap_count = prior_state.get("flap_count")
    flap_count = flap_count if isinstance(flap_count, int) and not isinstance(flap_count, bool) else 0
    last_definite_verdict = prior_definite
    if verdict in ("on", "off"):
        if prior_definite is not None and prior_definite != verdict:
            flap_count += 1
        last_definite_verdict = verdict

    # A TRANSITION is a call whose verdict is a real routing decision ("on"
    # or "off" — NEVER "hold", per plan.md P5: "never on hold — the plan
    # cites a real past incident (v0.273.0) where emitting the allow-path
    # buried the denies") AND differs from what THIS call's own prior state
    # held (including a prior "hold" or no-prior-state-at-all — the
    # session's first real decision is itself a transition worth recording).
    prior_raw_verdict = prior_state.get("verdict")
    is_transition = verdict in ("on", "off") and verdict != prior_raw_verdict

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
                "flap_count": flap_count,
                "last_definite_verdict": last_definite_verdict,
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
        "source": source,
        "reset": is_reset,
        "mode": mode,
        "verdict": verdict,
        "why": why,
        "tool_uses_in_window": metrics.get("tool_use_total"),
        "responses_in_window": metrics.get("responses_in_window"),
        "streak": new_streak,
        "elapsed_ms": elapsed_ms,
        "flap_count": flap_count,
        "applied": applied,
        "avg_tool_use_per_response": metrics.get("avg_tool_use_per_response"),
    }
    try:
        _append_route_log(log_path, entry)
    except Exception:
        pass  # log write failure -> silent, never a crash (fail-open)

    # ── P5 observability: emit exactly ONE fixed-enum SIGNAL line on a real
    # transition, never on "hold" (see is_transition above). The BASH caller
    # (caveman-route-hook.sh) is the sole writer into hook-events.jsonl —
    # mirroring parallelism-detector.py's own "this module only PRINTS a
    # SIGNAL line; the bash hook owns the emit" convention, so the substrate
    # keeps exactly one writer. C8: the token is a member of a FIXED enum,
    # never free text — `_verdict_token()` returns None for any case this
    # engine cannot itself produce, which is a deliberate fail-closed default
    # (no token -> no SIGNAL line -> no event), not an omission.
    #
    # Reachable in THIS phase (P3/P5, shadow-only, applier never called):
    #   caveman-route-shadow-on / caveman-route-shadow-off  (mode == "shadow")
    #   caveman-route-on        / caveman-route-off          (mode == "live" —
    #     the classifier's decision is real even though nothing applies it
    #     yet; P7 wires the actual write, this token already exists so P7's
    #     own event stream is not a new vocabulary)
    # Reserved for P7 (the applier's own outcomes — not reachable here
    # because the applier is never invoked in this phase):
    #   caveman-route-noop-no-caveman   (applier: caveman not installed)
    #   caveman-route-manual-override   (applier: manual-override latch)
    #   caveman-route-readback-mismatch (applier: post-write readback failed)
    if is_transition:
        token = None
        if mode == "shadow":
            token = "caveman-route-shadow-on" if verdict == "on" else "caveman-route-shadow-off"
        elif mode == "live":
            token = "caveman-route-on" if verdict == "on" else "caveman-route-off"
        if token:
            try:
                sys.stdout.write("SIGNAL %s\n" % token)
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Belt-and-braces: this hook must never be the reason a turn/session
        # start reports an error. See caveman-route-hook.sh's own EXIT trap
        # for the second layer of the same invariant.
        sys.exit(0)
