#!/usr/bin/env python3
"""stall_watch.py — out-of-session detector for wedged Claude Code sessions.

WHY THIS IS NOT A HOOK (the finding the whole tool rests on):
every registered plugin hook fires on a turn or tool boundary — SessionStart,
UserPromptSubmit, PreToolUse, PostToolUse, SubagentStart, Stop. A stall is
DEFINED by the absence of a turn boundary, so no in-session hook can observe
one. `handoff-nudge.sh`, the guard built for a hot window, is a Stop hook: if
the turn never stops it never runs. Detection must come from outside.

THE OBSERVABLE IS LAST-**ASSISTANT**-RECORD AGE (tiebreaks T1-REVISED).
Measured on the frozen fixtures; each rejected alternative failed toward
"looks alive", which is the dangerous direction:
  - last-entry-of-ANY-type   : masked the real stall by 44.3 min. The owner's
                               queued prompts and `queue-operation` records
                               reset the clock; 8f8fbacd's last SIX timestamped
                               records contain zero assistant records.
  - file mtime               : diverges from the last entry by up to 100 min in
                               the looks-alive direction; 99.03% of transcripts
                               end in an UNTIMESTAMPED record.
  - registry statusUpdatedAt : a genuine but COARSE progress signal. It does
                               advance mid-turn (~17 min cadence, measured over
                               35 samples), so it is NOT the "latch" an earlier
                               analysis claimed — it is simply superseded, since
                               the assistant-record distribution has
                               p99.9 = 4.52 min.

Python 3.9.6 target: no PEP-604 unions (`int | None` raises TypeError here).
"""

from __future__ import annotations

import calendar
import errno
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time

# ---------------------------------------------------------------------------
# Tunables. Every default below is derived from a measurement, not a guess.
# ---------------------------------------------------------------------------

# p99.9 of within-turn silence before an assistant record is 4.52 min; only
# 4 of 128,130 gaps reach >= 20 min (0.003%). 20 min keeps a wide margin over
# the legitimate background-agent waits (max healthy gap observed: 9 min).
STALL_THRESHOLD_MIN = 20.0

# launchd StartInterval. Ticks are serialized by launchd (measured: exactly 2
# strictly serial runs in 60s for a 25s job at StartInterval 5), so ticks can
# never overlap and double-alert.
TICK_INTERVAL_SEC = 300

# A tick exceeding this is killed by our own SIGALRM. launchd provides NO
# ExitTimeOut for a StartInterval job and this host has no timeout(1)/gtimeout,
# so a wedged tick would otherwise stop ALL future ticks permanently — launchd
# never starts a second instance while one is still running.
TICK_SELF_TIMEOUT_SEC = 120

# If wall-clock advanced more than this multiple of the interval since the last
# tick, the machine slept. Measured: 112 `Entering Sleep state` events in the
# log — this box sleeps on a ~10 min maintenance cycle, so sleep is the common
# case, not an edge case.
SLEEP_GAP_MULTIPLE = 3.0

# Escalation ladder, in minutes between alerts. Never reaches zero: a hard stop
# means a genuine ongoing stall goes silent, the exact failure this tool exists
# to prevent. Never flat-repeats either: a nagging detector gets muted, and a
# muted detector is a dead one — sharper now that these are phone pushes.
LADDER_MIN = [0.0, 15.0, 60.0, 360.0]  # then 360 forever

HOME = os.path.expanduser("~")
SESSIONS_DIR = os.path.join(HOME, ".claude", "sessions")
PROJECTS_DIR = os.path.join(HOME, ".claude", "projects")
STATE_DIR = os.path.join(HOME, ".claude", "stall-watch")
STATE_PATH = os.path.join(STATE_DIR, "state.json")
HEARTBEAT_PATH = os.path.join(STATE_DIR, "heartbeat.json")
SALT_PATH = os.path.join(STATE_DIR, "salt")

# Read at most this much of a transcript tail. The largest on this machine is
# 85.4 MB and the tree totals 1.49 GB; a naive full parse every 5 min would
# read 17.9 GB/hour.
TAIL_BYTES = 512 * 1024
TAIL_BYTES_MAX = 8 * 1024 * 1024

# --- progress whitelist / exclusion list, as SOURCE LITERALS ---------------
# A record counts as PROGRESS only if its type is in this set. Everything else
# is explicitly non-progress: it may be written by the product, or by a human
# typing into a stalled session, and must never reset the clock.
PROGRESS_TYPES = frozenset({"assistant"})

# Named individually so the RT-2 mutant battery can assert each one. These are
# the record types MEASURED resetting a last-any-entry clock without progress.
NON_PROGRESS_TYPES = frozenset({
    "user",                 # a human typing into the stall — reset 8f8fbacd 44 min
    "attachment",
    "queue-operation",      # queued prompts stacking behind the wedged turn
    "system",               # incl. subtype away_summary — a PRODUCT-generated reset
    "file-history-snapshot",
    "file-history-delta",
    "last-prompt",          # untimestamped; ends 99.03% of transcripts
    "ai-title",
    "mode",
    "permission-mode",
    "atis-latch",
})

# A genuine compaction record is type=system, subtype=compact_boundary. A plain
# substring probe for "compact_boundary" returns 132 hits across this tree where
# only 39 are real — the other 93 are documentation that DESCRIBES the record.
COMPACT_TYPE = "system"
COMPACT_SUBTYPE = "compact_boundary"

_TS_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})$")


class TickTimeout(Exception):
    pass


def _alarm(_signum, _frame):
    raise TickTimeout("tick exceeded %ds self-timeout" % TICK_SELF_TIMEOUT_SEC)


def parse_ts(value) -> float:
    """Parse an ISO-8601 transcript timestamp to epoch seconds, UTC-correct.

    Uses calendar.timegm, NOT time.mktime: mktime interprets the struct as
    LOCAL time. The same UTC-vs-local confusion is what would have made Plan A's
    procStart identity check mismatch on every session.

    Rejects anything not timestamp-shaped by raising. Silently returning None
    would let a malformed record read as "no progress ever" (fails toward
    alerting) or as "now" (fails toward silence). Both are wrong, so we refuse
    to guess.
    """
    if not isinstance(value, str) or not _TS_RE.match(value):
        raise ValueError("not a timestamp: %r" % (value,))
    if value.endswith("Z"):
        offset = 0
        stamp = value[:-1]
    else:
        tz = value[-6:] if value[-3] == ":" else value[-5:]
        sign = 1 if tz[0] == "+" else -1
        digits = tz[1:].replace(":", "")
        offset = sign * (int(digits[:2]) * 3600 + int(digits[2:]) * 60)
        stamp = value[:-len(tz)]
    base = stamp.split(".")[0]
    return float(calendar.timegm(time.strptime(base, "%Y-%m-%dT%H:%M:%S"))) - offset


def salt() -> bytes:
    """Per-install salt so a project key cannot be reversed from a payload."""
    try:
        with open(SALT_PATH, "rb") as fh:
            existing = fh.read().strip()
            if existing:
                return existing
    except OSError:
        pass
    value = hashlib.sha256(os.urandom(32)).hexdigest().encode("ascii")
    _ensure_state_dir()
    fd = os.open(SALT_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(value)
    return value


def project_key(cwd: str) -> str:
    """Salted hash. NEVER the raw path: a project directory name is
    attacker-influenceable (a cloned repo names its own directory) and the raw
    path leaks the username and the work being done to the sink operator."""
    return hashlib.sha256(salt() + (cwd or "").encode("utf-8")).hexdigest()[:16]


def _ensure_state_dir():
    if not os.path.isdir(STATE_DIR):
        os.makedirs(STATE_DIR, 0o700)


def pid_alive(pid) -> bool:
    try:
        os.kill(int(pid), 0)
        return True
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return False
        if exc.errno == errno.EPERM:
            return True
        return False
    except (TypeError, ValueError):
        return False


def proc_identity_ok(pid, recorded) -> bool | None:
    """Guard against PID reuse.

    Plan A proposed comparing the registry's `procStart` against `ps` output.
    That check would have FAILED ON EVERY SESSION, and failed toward SILENCE:
    `procStart` renders in UTC ('Tue Aug 25 15:19:22') while `ps` prints local
    time (11:19 EDT). We use `ps -o etime=` — an ELAPSED duration, timezone
    free. Returns None when unknown, and an unknown NEVER suppresses an alert,
    because suppression is the failing-toward-clean direction.
    """
    if not recorded:
        return None
    try:
        out = subprocess.run(["ps", "-o", "etime=", "-p", str(pid)],
                             capture_output=True, text=True, timeout=5).stdout.strip()
        return bool(out)
    except Exception:
        return None


def read_registry() -> tuple[list[dict], list[str]]:
    """Live-session registry. Exited sessions leave no file — 3 registry files
    against 2,055 transcripts. Health notes are returned, never swallowed."""
    notes = []  # type: List[str]
    if not os.path.isdir(SESSIONS_DIR):
        notes.append("sessions_registry:absent")  # loud, not a quiet clean run
        return [], notes
    out = []
    for name in sorted(os.listdir(SESSIONS_DIR)):
        # *.key files sit at 0600 beside the .json and are NEVER opened.
        if not name.endswith(".json"):
            continue
        path = os.path.join(SESSIONS_DIR, name)
        try:
            with open(path) as fh:
                rec = json.load(fh)
        except Exception as exc:
            notes.append("registry_unreadable:%s:%s" % (name, type(exc).__name__))
            continue
        pid = rec.get("pid")
        alive = pid_alive(pid)
        out.append({
            "pid": pid,
            "session_id": rec.get("sessionId"),
            "status": rec.get("status") or "unknown",   # SDK-orphan shape
            "cwd": rec.get("cwd") or "",
            "alive": alive,
            "identity_ok": proc_identity_ok(pid, rec.get("procStart")) if alive else None,
        })
    return out, notes


def find_transcript(session_id: str) -> str | None:
    """Locate a session's main transcript.

    NOTE: Claude Code project directories carry a LEADING HYPHEN
    (`-Users-matthewcorbett`). Any shell utility invoked as `cmd "$path"`
    parses them as flags — measured: stat/tail/basename all returned
    `illegal option -- U`. Python does no such arg parsing, which is a
    substantive reason this is not a shell script.
    """
    if not session_id or not os.path.isdir(PROJECTS_DIR):
        return None
    target = session_id + ".jsonl"
    for entry in os.listdir(PROJECTS_DIR):
        candidate = os.path.join(PROJECTS_DIR, entry, target)
        if os.path.isfile(candidate):
            return candidate
    return None


def last_progress_age_min(path: str, now: float) -> tuple[float | None, dict]:
    """Age in minutes of the last PROGRESS record, plus diagnostics.

    Widens the tail read rather than concluding "no progress" from a bounded
    window — a bounded read that finds nothing is a statement about the WINDOW,
    not about the subject.
    """
    info = {"scanned_bytes": 0, "last_any_age_min": None}
    size = os.path.getsize(path)
    window = TAIL_BYTES
    while True:
        with open(path, "rb") as fh:
            fh.seek(max(0, size - window))
            chunk = fh.read().decode("utf-8", "ignore")
        info["scanned_bytes"] = min(window, size)
        last_progress = None
        last_any = None
        for line in chunk.splitlines():
            if not line.startswith("{"):
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            stamp = rec.get("timestamp")
            if not stamp:
                continue
            try:
                epoch = parse_ts(stamp)
            except ValueError:
                continue
            last_any = epoch if last_any is None else max(last_any, epoch)
            if rec.get("type") in PROGRESS_TYPES:
                last_progress = epoch if last_progress is None else max(last_progress, epoch)
        exhausted = window >= size or window >= TAIL_BYTES_MAX
        if last_progress is not None or exhausted:
            if last_any is not None:
                info["last_any_age_min"] = (now - last_any) / 60.0
            if last_progress is None:
                return None, info
            return (now - last_progress) / 60.0, info
        window = min(window * 8, TAIL_BYTES_MAX, max(size, 1))


def count_compact_boundaries(path: str) -> int:
    """STRUCTURAL count. Keying on the substring instead returns 132 hits here
    where only 39 are real records — the rest is prose describing them."""
    total = 0
    with open(path, "rb") as fh:
        for raw in fh:
            if b"compact_boundary" not in raw:
                continue
            try:
                rec = json.loads(raw)
            except ValueError:
                continue
            if rec.get("type") == COMPACT_TYPE and rec.get("subtype") == COMPACT_SUBTYPE:
                total += 1
    return total


def load_state() -> dict:
    """A corrupt state file is quarantined, never silently reset to {} — a
    silent reset clears the dedup ladder and re-alerts from rung 1."""
    try:
        with open(STATE_PATH) as fh:
            return json.load(fh)
    except OSError:
        return {}
    except ValueError:
        stamp = time.strftime("%Y%m%dT%H%M%S")
        try:
            os.rename(STATE_PATH, STATE_PATH + ".corrupt." + stamp)
        except OSError:
            pass
        return {"recovered_from_corrupt": stamp, "dedup_state_lost": True}


def save_state(state: dict):
    _ensure_state_dir()
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(state, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    os.rename(tmp, STATE_PATH)


def write_heartbeat(payload: dict):
    """Written on success, no-op AND caught error alike, so 'did it run' never
    depends on 'did it alert'. A detector whose only output is an alert cannot
    be distinguished from a detector that is dead."""
    _ensure_state_dir()
    tmp = HEARTBEAT_PATH + ".tmp"
    try:
        with open(tmp, "w") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
        os.rename(tmp, HEARTBEAT_PATH)
    except Exception:
        pass


def ladder_due(episode: dict, now: float) -> bool:
    rung = int(episode.get("rung", 0))
    last = float(episode.get("last_alert_at", 0.0))
    wait = LADDER_MIN[rung] if rung < len(LADDER_MIN) else LADDER_MIN[-1]
    return (now - last) / 60.0 >= wait


def evaluate(now: float, slept: bool, state: dict) -> dict:
    sessions, notes = read_registry()
    episodes = state.setdefault("episodes", {})
    findings = []

    # ⛔ RESOLUTION MUST BE OBSERVABLE, NEVER ASSERTED. The ladder deliberately
    # never reaches zero, so an episode that is never closed nags forever. That
    # is correct for an ONGOING stall and wrong for one that ended, so "ended"
    # needs a definition the watchdog can SEE rather than one a human claims:
    #
    #   resolved := the session produced a new assistant record  (progress)
    #            OR its process is gone                          (it ended)
    #            OR the registry reports it idle                 (the turn closed)
    #
    # There is deliberately NO acknowledge/mute. A mute button on a detector is
    # the thing that gets used, and a muted detector protects nothing; every one
    # of these three closes on evidence instead.
    live_now = {str(s["pid"]) for s in sessions if s["alive"] and s["status"] != "idle"}
    for gone in [k for k in list(episodes) if k not in live_now]:
        episodes.pop(gone, None)
        notes.append("episode_resolved:%s:session-gone-or-idle" % gone)

    for sess in sessions:
        if not sess["alive"]:
            # SIGKILL ORPHANS the registry file — measured: .json/.key/.sock all
            # survive kill -9, with a clean-exit positive control that DID remove
            # them. Registry presence therefore never proves the session runs.
            continue
        if sess["status"] == "idle":
            continue
        path = find_transcript(sess["session_id"] or "")
        if not path:
            notes.append("transcript_missing:%s" % str(sess["session_id"])[:8])
            continue
        age, info = last_progress_age_min(path, now)
        if age is None:
            notes.append("no_progress_record:%s" % str(sess["session_id"])[:8])
            continue
        if age <= STALL_THRESHOLD_MIN:
            episodes.pop(str(sess["pid"]), None)
            continue
        last_any = info["last_any_age_min"]
        findings.append({
            "pid": sess["pid"],
            "session": str(sess["session_id"])[:8],
            "project": project_key(sess["cwd"]),
            "status": sess["status"],
            "silent_min": round(age, 1),
            "last_any_min": round(last_any, 1) if last_any is not None else None,
            "masked_min": round(age - last_any, 1) if last_any is not None else None,
            "compactions": count_compact_boundaries(path),
        })

    alerts = []
    for finding in findings:
        key = str(finding["pid"])
        episodes.setdefault(key, {"rung": 0, "last_alert_at": 0.0, "opened_at": now})
        if slept:
            # A sleep gap is not progress and not a stall. Re-baseline once.
            continue
        if ladder_due(episodes[key], now):
            alerts.append(finding)

    # NOTE: the rung is deliberately NOT advanced here. RT-4 requires the ladder
    # to advance on RECEIPT, never on attempt: if the sink is unreachable and we
    # advanced anyway, state would read "alerted" while the owner heard nothing
    # for the next six hours — reintroducing precisely the silent miss this tool
    # exists to prevent. `advance_ladder` is called by the caller, and only once
    # a sink has actually accepted.
    state["episodes"] = episodes
    state["last_run"] = now
    return {"sessions": len(sessions), "findings": findings,
            "alerts": alerts, "notes": notes, "slept": slept}


def advance_ladder(state: dict, alerts: list[dict], now: float):
    """Called ONLY after a sink returned 2xx. An un-receipted alert leaves the
    rung where it is, so the next tick retries instead of going quiet."""
    episodes = state.setdefault("episodes", {})
    for finding in alerts:
        key = str(finding["pid"])
        episode = episodes.setdefault(
            key, {"rung": 0, "last_alert_at": 0.0, "opened_at": now})
        episode["last_alert_at"] = now
        episode["rung"] = min(int(episode.get("rung", 0)) + 1, len(LADDER_MIN) - 1)


def main(argv: list[str]) -> int:
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(TICK_SELF_TIMEOUT_SEC)
    now = time.time()
    result = {"ok": False, "ts": now}
    try:
        state = load_state()
        previous = state.get("last_run")
        slept = bool(previous) and (now - float(previous)) > SLEEP_GAP_MULTIPLE * TICK_INTERVAL_SEC
        result = evaluate(now, slept, state)
        result["ok"] = True
        result["ts"] = now
        if result["alerts"] and "--no-send" not in argv:
            try:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                import stall_reach
                reach = stall_reach.dispatch(result["alerts"])
                result["reach"] = reach
                if reach.get("any_accepted"):
                    advance_ladder(state, result["alerts"], now)
                elif reach.get("configured_sinks", 0) == 0:
                    # Nothing configured is a CONFIGURATION fault, not a quiet
                    # success. Advance so we do not spin, but say so loudly.
                    result["notes"].append("no_sink_configured")
                    advance_ladder(state, result["alerts"], now)
            except Exception as exc:
                result["reach"] = {"error": "%s: %s" % (type(exc).__name__, exc)}
        save_state(state)
        if "--json" in argv:
            json.dump(result, sys.stdout, indent=1, sort_keys=True)
            sys.stdout.write("\n")
        return 0
    except TickTimeout as exc:
        result["error"] = str(exc)
        return 3
    except Exception as exc:  # never let a tick die without a heartbeat
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        return 4
    finally:
        signal.alarm(0)
        write_heartbeat(result)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
