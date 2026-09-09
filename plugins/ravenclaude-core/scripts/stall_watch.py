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
import fcntl
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
# Advisory cross-process lock guarding the whole load_state -> evaluate ->
# save_state cycle in main(). The only guard against overlap used to be an
# UNENFORCED assumption that launchd serializes ticks (see TICK_INTERVAL_SEC
# below) — an assumption this script's own manual-invocation CLI flags
# (--json / --no-send) directly contradict: a human running
# `python3 stall_watch.py --json` by hand while a scheduled tick is also
# mid-flight is plausible given the timeout budget sits close to the tick
# interval. Without a lock, both processes read the same starting `episodes`
# dict, independently compute ladder state, and race on the final
# save_state() write — the process that renames last wins and silently
# discards the other's ladder advancement (can cause a double-alert or
# revive a closed episode). The lock is held across the soak/heartbeat
# writes too, so _trim_soak()'s identical read-whole-file/rewrite/rename
# cycle serializes against the same window instead of racing
# append_soak() from a concurrent process.
STATE_LOCK_PATH = STATE_PATH + ".lock"
HEARTBEAT_PATH = os.path.join(STATE_DIR, "heartbeat.json")
# ⛔ THE HEARTBEAT IS NOT A SOAK: it is overwritten every tick, so after days it
# holds one snapshot. C17's open question is whether the detector GENERALIZES
# beyond the 4 frozen fixtures, and a single snapshot cannot answer that. The
# soak log is the append-only series. Capped by bytes, because a log that fills
# a disk is a tool that gets deleted.
SOAK_PATH = os.path.join(STATE_DIR, "soak.jsonl")
SOAK_MAX_BYTES = 2 * 1024 * 1024
SOAK_KEEP_LINES = 5000
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


def _acquire_state_lock():
    """Blocking advisory flock on STATE_LOCK_PATH (see its comment above).

    Blocking, not LOCK_NB: a losing process should wait its turn and run its
    tick, not silently skip it. TICK_SELF_TIMEOUT_SEC's SIGALRM still bounds
    the wait — PEP 475 means a signal handler that raises (as _alarm does)
    propagates out of a blocked syscall instead of the syscall being
    auto-retried, so a wedged lock holder still surfaces as TickTimeout
    rather than hanging this process forever.

    Returns an open file handle the caller must close() (which releases the
    flock) once the guarded section is done. If flock() itself raises
    (including via the SIGALRM interruption above), the handle is closed
    before re-raising so no fd is leaked on the error path.
    """
    _ensure_state_dir()
    fh = open(STATE_LOCK_PATH, "a+")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
    except BaseException:
        fh.close()
        raise
    return fh


def _release_state_lock(fh):
    if fh is None:
        return
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    except Exception:
        pass
    finally:
        fh.close()


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
            # ADDITIVE (P3, launch-hang detector): raw epoch-millisecond fields
            # the general evaluate() path never needed. Carried through here —
            # rather than a second directory scan — so the launch-hang pass
            # reuses this same read, exactly like every other consumer of
            # read_registry(). Extra keys are inert to evaluate().
            "started_at_ms": rec.get("startedAt"),
            "status_updated_at_ms": rec.get("statusUpdatedAt"),
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


def append_soak(payload: dict):
    """One derived line per tick, so the soak ACCUMULATES instead of evaporating.

    ⛔ DERIVED VALUES ONLY — the same invariant as the alert payload: counts,
    rounded integers, booleans. No session id, no path, no transcript content,
    no command text. This file is durable and the transcripts it summarises carry
    credentials and fetched web bodies, so nothing that could contain either is
    written here. `silent_min` is rounded to whole minutes, which is all a
    generalization question needs.
    """
    _ensure_state_dir()
    try:
        findings = payload.get("findings") or []
        line = json.dumps({
            "ts": int(payload.get("ts") or time.time()),
            "ok": bool(payload.get("ok")),
            "sessions": int(payload.get("sessions") or 0),
            "findings": len(findings),
            "alerts": len(payload.get("alerts") or []),
            "slept": bool(payload.get("slept")),
            "silent_min": sorted(int(round(float(f.get("silent_min") or 0)))
                                 for f in findings),
            "notes": len(payload.get("notes") or []),
            "receipted": bool((payload.get("reach") or {}).get("any_accepted")),
        }, sort_keys=True)
        with open(SOAK_PATH, "a") as fh:
            fh.write(line + "\n")
        _trim_soak()
    except Exception:
        # A soak record is evidence, never a precondition. Losing one must never
        # cost a tick.
        pass


def _trim_soak():
    try:
        if os.path.getsize(SOAK_PATH) < SOAK_MAX_BYTES:
            return
        with open(SOAK_PATH) as fh:
            lines = fh.readlines()
        tmp = SOAK_PATH + ".tmp"
        with open(tmp, "w") as fh:
            fh.writelines(lines[-SOAK_KEEP_LINES:])
        os.rename(tmp, SOAK_PATH)
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


# =============================================================================
# ADDITIVE — P3: launch-hang detector (anthropics/claude-code#92932)
#
# `evaluate()` above, and everything it touches (`advance_ladder`,
# `ladder_due`, `LADDER_MIN`, `STALL_THRESHOLD_MIN`), is UNCHANGED by this
# section. A session launched with cwd outside any git work tree can hang
# indefinitely before ever reaching a first turn — a confirmed upstream bug.
# `evaluate()` structurally cannot see it: it skips `status == "idle"` before
# it would ever check for a missing transcript, and its `live_now` resolution
# set excludes idle sessions, so an episode that got through anyway would be
# auto-resolved as "session-gone-or-idle" on the very next tick. This is
# therefore a SEPARATE classification pass with its own episode namespace
# (`state["launch_episodes"]`, disjoint from `state["episodes"]`) — reusing
# `read_registry`, `find_transcript`, `project_key`, the state lock,
# `write_heartbeat`, `append_soak`, and the escalation ladder (`LADDER_MIN`,
# `ladder_due`, `advance_ladder`) via the plumbing below. Deleting this whole
# block plus its one call site in `main()` restores exactly today's
# behavior — that is the "additive, two-way-door" contract this section is
# built to satisfy.
# =============================================================================

# Bounds a normal cold start. The real captured instance this detector was
# built from was already 12+ minutes in when observed; 3.0 minutes gives wide
# margin over ordinary launch latency while still catching the failure long
# before a user would otherwise notice only by chance.
LAUNCH_HANG_MIN = 3.0

# The measured real instance showed `statusUpdatedAt == updatedAt ==
# startedAt + 195ms` — a status write that happens once, at launch, and never
# again. A healthy session bumps `statusUpdatedAt` on a ~17-minute cadence
# (see STALL_THRESHOLD_MIN's header above), so any epsilon comfortably above
# ordinary launch jitter and comfortably below that cadence discriminates
# correctly; 2 full seconds leaves a wide margin on both sides.
LAUNCH_HANG_STATUS_EPSILON_MS = 2000.0

# Bounds the ONE conjunct in this detector that shells out. Checked LAST in
# the loop below, after every cheaper conjunct already holds, so a session
# that isn't otherwise a launch-hang candidate never pays the subprocess cost.
GIT_PROBE_TIMEOUT_SEC = 3

LAUNCH_HANG_ISSUE_REF = "anthropics/claude-code#92932"


def _outside_git_work_tree(cwd) -> bool:
    """True only when git POSITIVELY reports `cwd` is outside any work tree
    (the actual #92932 precondition). Any ambiguity — git absent, a deleted
    cwd, a timeout, an unexpected non-zero exit — returns False: FAIL TOWARD
    NOT-HUNG, never toward a false alarm. A detector that fires on its own
    broken probe is noise, and noise gets the detector disabled.

    `git -C <cwd> rev-parse --is-inside-work-tree` prints "true"/exit 0
    inside a work tree; outside any repo it exits non-zero with "fatal: not
    a git repository" on stderr — that non-zero IS the expected, positive
    signal this function exists to read, not a probe failure.

    ⛔ `-C` is a top-level git option, not a `rev-parse` option — it MUST
    precede the subcommand (`git -C <path> rev-parse ...`), never follow it
    (`git rev-parse -C <path> ...` is a documented-looking but broken form:
    verified live — it exits 128 with "option '--is-inside-work-tree' must
    come before non-option arguments" instead of ever probing `cwd` at all).
    """
    if not cwd or not os.path.isdir(cwd):
        return False
    try:
        proc = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=GIT_PROBE_TIMEOUT_SEC,
        )
    except Exception:
        return False
    if proc.returncode == 0:
        return (proc.stdout or "").strip() != "true"
    if "not a git repository" in (proc.stderr or ""):
        return True
    return False  # an unexpected non-zero — ambiguous, so NOT-hung


def evaluate_launch_hangs(now: float, state: dict) -> dict:
    """The additive launch-hang classification pass. See the module banner
    above for why this cannot be folded into `evaluate()`.

    All six conjuncts below must hold, cheapest first, the one subprocess
    call last:
      1. alive (pid check)
      2. status == "idle"
      3. statusUpdatedAt <= startedAt + epsilon (never once updated)
      4. no transcript for the session's sessionId
      5. now - startedAt > LAUNCH_HANG_MIN (bounds a normal cold start)
      6. cwd is not a git work tree (the actual #92932 precondition; last,
         since it is the only conjunct that shells out)
    """
    sessions, notes = read_registry()
    episodes = state.setdefault("launch_episodes", {})
    findings = []

    # ⛔ RESOLUTION MUST BE OBSERVABLE, NEVER ASSERTED — same discipline as
    # evaluate(), but NOT evaluate()'s own `live_now` set (that one excludes
    # idle sessions and would erase every launch episode on the next tick).
    # This detector's own resolution rule: the process is gone, OR a
    # transcript now exists, OR statusUpdatedAt has moved past its initial
    # value. All three are directly observable from read_registry() +
    # find_transcript(), never inferred.
    still_open = set()
    for sess in sessions:
        if not sess["alive"]:
            continue
        if find_transcript(sess["session_id"] or ""):
            continue
        started_ms = sess.get("started_at_ms")
        status_updated_ms = sess.get("status_updated_at_ms")
        if started_ms is None or status_updated_ms is None:
            continue
        try:
            moved = abs(float(status_updated_ms) - float(started_ms)) > LAUNCH_HANG_STATUS_EPSILON_MS
        except (TypeError, ValueError):
            continue
        if moved:
            continue
        still_open.add(str(sess["pid"]))
    for gone in [k for k in list(episodes) if k not in still_open]:
        episodes.pop(gone, None)
        notes.append("launch_episode_resolved:%s" % gone)

    for sess in sessions:
        if not sess["alive"]:                                      # conjunct 1
            continue
        if sess["status"] != "idle":                                # conjunct 2
            continue
        started_ms = sess.get("started_at_ms")
        status_updated_ms = sess.get("status_updated_at_ms")
        if started_ms is None or status_updated_ms is None:
            continue
        try:
            started_ms = float(started_ms)
            status_updated_ms = float(status_updated_ms)
        except (TypeError, ValueError):
            continue
        if abs(status_updated_ms - started_ms) > LAUNCH_HANG_STATUS_EPSILON_MS:  # conjunct 3
            continue
        path = find_transcript(sess["session_id"] or "")            # conjunct 4
        if path:
            continue
        elapsed_min = (now - started_ms / 1000.0) / 60.0
        if elapsed_min <= LAUNCH_HANG_MIN:                           # conjunct 5 (cheap)
            continue
        if not _outside_git_work_tree(sess["cwd"]):                  # conjunct 6 (shells out — LAST)
            continue
        findings.append({
            "pid": sess["pid"],
            "session": str(sess["session_id"])[:8],
            # ADDITIVE (P4): the FULL sessionId, not just the 8-char display
            # prefix above — needed to locate `~/.claude/debug/<sessionId>.txt`
            # below. Not itself a leak: it is the same value already exposed
            # (truncated) in "session", and it is registry-sourced, not
            # debug-log content — the P4 leak invariant governs the LOG's
            # content, not the session identifier P3 already carries.
            "session_id": sess["session_id"],
            "project": project_key(sess["cwd"]),
            "status": sess["status"],
            "silent_min": round(elapsed_min, 1),
            "kind": "launch-hang",
            "issue": LAUNCH_HANG_ISSUE_REF,
        })

    # =========================================================================
    # ADDITIVE — P4: optional debug-log confirmatory enrichment (see the block
    # below, right after this function). Runs strictly AFTER every finding
    # above is already final — it can only ever ADD `signature`/`match_count`
    # to a finding that already fired; it is never consulted by, and can never
    # suppress, any of the six conjuncts above. Each finding gets its own
    # try/except so a single corrupt/unreadable debug log can never cost the
    # OTHER findings in this same tick, or the tick itself, their result —
    # matching this module's own P3-around-general-path fail-open discipline
    # in main() around this whole function's call site.
    # =========================================================================
    for finding in findings:
        try:
            _enrich_launch_hang_with_debug_log(finding)
        except Exception:
            pass  # unenriched is exactly what P3 alone would have produced

    alerts = []
    for finding in findings:
        key = str(finding["pid"])
        episodes.setdefault(key, {"rung": 0, "last_alert_at": 0.0, "opened_at": now})
        if ladder_due(episodes[key], now):
            alerts.append(finding)

    state["launch_episodes"] = episodes
    return {"sessions": len(sessions), "findings": findings,
            "alerts": alerts, "notes": notes}


# =============================================================================
# ADDITIVE — P4: debug-log confirmatory enrichment (optional, narrow,
# non-load-bearing). Read the module banner's "Where the panels agreed" #3
# before touching anything here: the debug-log rg/TCC signature is
# OPTIONAL/CONFIRMATORY ONLY, never a required trigger — this is a
# load-bearing design constraint, not a suggestion. Everything below runs
# strictly AFTER `evaluate_launch_hangs()` above has already decided a
# session is a launch-hang; it can only ever ENRICH an already-fired finding,
# never create one, never suppress one, and never change which sessions get
# flagged. Deleting this whole block plus its one call site above restores
# exactly P3's behavior — the same additive, two-way-door contract P3 itself
# satisfies against `evaluate()`.
# =============================================================================

# `~/.claude/debug/<sessionId>.txt` is only ever populated when the user
# happened to launch with `--debug` — NOT the default (§0 of the plan; both
# FORGE panels independently measured that most live sessions have no debug
# log at all). Its absence is therefore the common case, not an error path.
DEBUG_LOG_DIR = os.path.join(HOME, ".claude", "debug")

# Reuses the SAME bound as the transcript tail read above (TAIL_BYTES) rather
# than inventing a second scale — a debug log is not expected to be
# materially larger than a transcript, and this keeps the read genuinely
# bounded (does not scale with file size) regardless of how large the file
# on disk claims to be.
DEBUG_LOG_TAIL_BYTES = TAIL_BYTES

RG_TCC_SIGNATURE = "rg-tcc"

# The observed real-world shape (this repo's own `--debug` capture that
# produced the filed issue, anthropics/claude-code#92932 — see
# claims-table.md #2 in this feature's own FORGE run dir): an unscoped `rg`
# file-index scan hits a macOS TCC-protected path (`.Trash`, `Library/Mail`,
# `Photos Library.photoslibrary`, `Library/Messages`, ...) and each hit ends
# the same way — "Operation not permitted (os error 1)". Two independently
# loose regexes rather than one line-shaped pattern: the exact interleaving
# of the `rg` invocation and its error output was never captured verbatim in
# this repo's own research trail, so requiring both substrings on the SAME
# line would risk a false NEGATIVE against a log shape this detector has
# never actually seen firsthand.
_RG_INVOCATION_RE = re.compile(r"\brg\b|ripgrep", re.IGNORECASE)
_RG_TCC_ERROR_RE = re.compile(r"Operation not permitted(?: \(os error 1\))?")

# ⛔ observed against Claude Code 2.1.263, 2026-09-08 — re-verify the rg/TCC
# log signature against a fresh --debug capture on any Claude Code version
# bump; a format change here degrades ONLY this optional signal, never the
# P3 base detection.
def _enrich_launch_hang_with_debug_log(finding: dict) -> None:
    """OPTIONAL, confirmatory-ONLY enrichment of an ALREADY-FIRED P3
    'launch-hang' finding. Mutates `finding` in place; returns None always.

    Only ever ADDS `signature`/`match_count` to a finding that already
    exists — never a precondition of one firing, never able to remove or
    alter anything P3 already decided.

    No debug file for this session's sessionId -> does nothing, leaves
    `finding` byte-identical to what P3 alone produced. This is the COMMON
    case (`--debug` is not on by default), not an error path.

    ⛔ DERIVED LABELS ONLY, hard leak-control invariant: on a match this
    attaches the literal string "rg-tcc" plus an integer match count —
    NEVER a matched line, a file path from the log, or any other raw
    excerpt. Mirrors the same discipline `capability-orientation.sh` /
    `watch-run-state.sh` hold for a payload that is understood to reach a
    notification sink (and, in some paths, a model): a debug log carries
    absolute paths and command output that must never leak through.

    Bounded read: only the last DEBUG_LOG_TAIL_BYTES of the file are ever
    read (via seek, not a full read), so the cost of this function does not
    scale with how large the debug log is on disk.

    Any exception raised here (unreadable file, permission error, malformed
    content) is caught by the CALL SITE in `evaluate_launch_hangs()`, not
    here — this function is deliberately left free to raise on an
    unexpected OS error rather than swallowing it internally, so the one
    fail-open boundary this module relies on stays in exactly one place
    (matching this module's own `main()` discipline of one try/except per
    additive pass, not one nested inside another).
    """
    session_id = finding.get("session_id")
    if not session_id:
        return
    # os.path.basename: defense in depth against a sessionId that somehow
    # carries a path separator. session_id is registry-sourced (trusted),
    # but this detector's own contract is to fail toward doing nothing on
    # any ambiguity, never toward trusting an unusual value.
    path = os.path.join(DEBUG_LOG_DIR, os.path.basename(str(session_id)) + ".txt")
    if not os.path.isfile(path):
        return  # the common case
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        fh.seek(max(0, size - DEBUG_LOG_TAIL_BYTES))
        chunk = fh.read().decode("utf-8", "ignore")
    if not _RG_INVOCATION_RE.search(chunk):
        return
    count = len(_RG_TCC_ERROR_RE.findall(chunk))
    if count <= 0:
        return
    finding["signature"] = RG_TCC_SIGNATURE
    finding["match_count"] = count


def main(argv: list[str]) -> int:
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(TICK_SELF_TIMEOUT_SEC)
    now = time.time()
    result = {"ok": False, "ts": now}
    lock_fh = None
    try:
        # Serialize the whole tick — load, evaluate, save, and the soak/
        # heartbeat writes — against any concurrent invocation (manual or
        # launchd). See STATE_LOCK_PATH's comment for why this is
        # load-bearing and not just belt-and-suspenders.
        lock_fh = _acquire_state_lock()
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

        # =====================================================================
        # ADDITIVE — P3 call site. One call, own try/except so a failure in the
        # launch-hang pass can never cost the general stall path its heartbeat/
        # soak write (FAIL-OPEN). See the module banner above `LAUNCH_HANG_MIN`
        # for why this is a separate pass rather than a change to evaluate().
        # =====================================================================
        try:
            launch_result = evaluate_launch_hangs(now, state)
            result["launch_findings"] = launch_result["findings"]
            result["launch_notes"] = launch_result.get("notes", [])
            if launch_result["alerts"] and "--no-send" not in argv:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                import stall_reach
                launch_reach = stall_reach.dispatch(launch_result["alerts"])
                result["launch_reach"] = launch_reach
                # Reuses advance_ladder() itself (not a reimplementation) via a
                # thin wrapper dict — advance_ladder() does
                # `state.setdefault("episodes", {})`, and `launch_episodes` is
                # the SAME dict object already stored at
                # state["launch_episodes"], so mutating it through the wrapper
                # mutates the real object in place. This keeps the launch-hang
                # episode namespace disjoint from state["episodes"] without
                # touching advance_ladder()'s own source.
                launch_episodes = state.setdefault("launch_episodes", {})
                wrapper = {"episodes": launch_episodes}
                if launch_reach.get("any_accepted"):
                    advance_ladder(wrapper, launch_result["alerts"], now)
                elif launch_reach.get("configured_sinks", 0) == 0:
                    result["launch_notes"].append("no_sink_configured")
                    advance_ladder(wrapper, launch_result["alerts"], now)
        except Exception as exc:
            result.setdefault("launch_notes", []).append(
                "launch_hang_pass_error:%s:%s" % (type(exc).__name__, exc))

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
        # Both run on success, no-op AND caught error alike. "Did it run" must
        # never depend on "did it alert", and the soak series must not have holes
        # exactly where the interesting ticks are. Still inside the lock's
        # critical section (released last) so append_soak's _trim_soak
        # read-rewrite-rename cycle stays serialized against a concurrent
        # process too.
        write_heartbeat(result)
        append_soak(result)
        _release_state_lock(lock_fh)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
