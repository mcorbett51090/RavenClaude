#!/usr/bin/env python3
"""terminal-watcher.py — ring a terminal's bell when an agent process goes idle
after responding, so a VS Code tab shows 🔔 (and chimes) the moment it needs you.

How it works (all mechanics verified locally on Linux 6.8, 2026-07-09):
  - Each watched process's cumulative bytes-written is read from `/proc/<pid>/io`
    (the `wchar:` field). A positive delta between polls means "actively writing"
    (streaming a response); a run of zero-deltas after activity means "gone quiet".
  - The process's controlling terminal is resolved from `/proc/<pid>/fd/{0,1,2}`,
    which symlink to `/dev/pts/N` for an interactive process.
  - When a process that WAS active goes quiet for IDLE_THRESHOLD seconds, a single
    BEL byte (`\\a`) is written to its PTY slave. VS Code (the PTY master) shows the
    tab bell + plays the configured audio cue.

Design notes / bug history (the 5 fixes that made this actually work, plus one more):
  B1  active-bytes are ACCUMULATED across polls, not compared per-tick. Streaming
      arrives as many small chunks; no single 0.5s tick clears MIN_ACTIVE_BYTES, so
      a per-tick threshold meant the bell NEVER rang. (P0)
  B2  double-bell: several processes (shell wrapper + real binary) share one PTS.
      Dedup at intake by PTY, AND — the stronger guarantee — make the ring decision
      once per PTS in the main loop, so even an intake race (PTY not yet resolved
      when two PIDs are first seen) can't double-ring. (P0)
  B3/B4  live in the shell wrapper (functions not aliases; start-guard). See SKILL.md.
  B5  PTY is re-resolved every tick until non-None: a process may not have opened its
      terminal at first detection, and a once-only lookup would strand it forever.
  Baseline: the FIRST observation of a PID only establishes the wchar baseline (no
      delta), so historical bytes aren't counted as one giant burst → no spurious
      startup bell.

Config is overridable by environment variable (see below) so it works for any pair
of agent commands, not just copilot/claude.
"""

from __future__ import annotations

import os
import signal
import sys
import time
from pathlib import Path

# ── Config (env-overridable) ─────────────────────────────────────────────────
# Comma-separated process names (matched against /proc/<pid>/comm, i.e. the
# executable basename) to watch. Default covers the common agent CLIs.
WATCH_COMMANDS = [
    c.strip()
    for c in os.environ.get("TERMINAL_WATCHER_COMMANDS", "copilot,claude").split(",")
    if c.strip()
]
POLL_INTERVAL = float(os.environ.get("TERMINAL_WATCHER_POLL", "0.5"))  # seconds
IDLE_THRESHOLD = float(os.environ.get("TERMINAL_WATCHER_IDLE", "3.0"))  # seconds quiet → ring
MIN_ACTIVE_BYTES = int(os.environ.get("TERMINAL_WATCHER_MIN_BYTES", "500"))  # cumulative
# How long a sub-threshold burst must stay quiet before we forget it (Bug 3). Kept
# well ABOVE IDLE_THRESHOLD so a real response with a normal mid-stream pause (a tool
# call, a network wait) still accumulates and rings — only genuinely-stale partial
# activity after a long idle is discarded. Missing a real bell is worse than a rare
# spurious one for this tool, so this errs toward keeping accumulation.
RESET_THRESHOLD = float(os.environ.get("TERMINAL_WATCHER_RESET", "30.0"))  # seconds
PIDFILE = Path(os.environ.get("TERMINAL_WATCHER_PIDFILE", "/tmp/terminal-watcher.pid"))


def log(msg: str) -> None:
    """One line to stdout; the shell wrapper redirects stdout to the log file."""
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ── /proc readers ────────────────────────────────────────────────────────────
def read_wchar(pid: int) -> int | None:
    """Cumulative bytes written by the process, or None if unreadable/gone."""
    try:
        with open(f"/proc/{pid}/io") as f:
            for line in f:
                if line.startswith("wchar:"):
                    return int(line.split(":", 1)[1])
    except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError, OSError):
        return None
    return None


def get_pty(pid: int) -> str | None:
    """Resolve the process's controlling PTY (/dev/pts/N) via its std fds, or None."""
    for fd in ("0", "1", "2"):
        try:
            target = os.readlink(f"/proc/{pid}/fd/{fd}")
        except OSError:
            continue
        if target.startswith("/dev/pts/"):
            return target
    return None


def proc_comm(pid: int) -> str | None:
    """Executable basename from /proc/<pid>/comm (never the full cmdline — that would
    match the watcher's own `python3 … terminal-watcher.py` invocation)."""
    try:
        return Path(f"/proc/{pid}/comm").read_text().strip()
    except (FileNotFoundError, ProcessLookupError, PermissionError, OSError):
        return None


def discover_pids() -> list[int]:
    """PIDs whose comm matches a watched command, excluding this watcher process."""
    me = os.getpid()
    found = []
    try:
        entries = os.listdir("/proc")
    except OSError:
        return found
    for name in entries:
        if not name.isdigit():
            continue
        pid = int(name)
        if pid == me:
            continue
        if proc_comm(pid) in WATCH_COMMANDS:
            found.append(pid)
    return found


def ring_bell(pty: str) -> bool:
    """Write a single BEL byte to the PTY slave. Returns True on success."""
    try:
        fd = os.open(pty, os.O_WRONLY | os.O_NOCTTY)
    except OSError:
        return False
    try:
        os.write(fd, b"\a")
        return True
    except OSError:
        return False
    finally:
        os.close(fd)


# ── Per-process state ────────────────────────────────────────────────────────
class ProcState:
    __slots__ = (
        "pid",
        "pty",
        "last_wchar",
        "active_bytes_total",
        "was_active",
        "last_write_time",
        "wants_ring",
    )

    def __init__(self, pid: int, pty: str | None) -> None:
        self.pid = pid
        self.pty = pty
        self.last_wchar: int | None = None  # None until baseline established
        self.active_bytes_total = 0
        self.was_active = False
        self.last_write_time = 0.0
        self.wants_ring = False

    def tick(self, now: float) -> None:
        """Update write/idle bookkeeping. Sets self.wants_ring; does NOT ring
        (ringing is decided per-PTY in the main loop to prevent double-bells)."""
        self.wants_ring = False

        # B5: keep trying to resolve the PTY until we have one.
        if self.pty is None:
            self.pty = get_pty(self.pid)

        wchar = read_wchar(self.pid)
        if wchar is None:
            return  # transient read failure or exiting process — skip this tick

        # Establish baseline on first observation (no delta → no startup burst).
        if self.last_wchar is None:
            self.last_wchar = wchar
            return

        delta = wchar - self.last_wchar
        self.last_wchar = wchar
        if delta < 0:
            delta = 0  # counter shouldn't go backwards for a live pid; be defensive

        if delta > 0:
            # Actively writing — B1: accumulate across ticks.
            self.active_bytes_total += delta
            self.last_write_time = now
            if self.active_bytes_total >= MIN_ACTIVE_BYTES:
                self.was_active = True
            return

        # Quiet this tick.
        idle_elapsed = now - self.last_write_time
        if self.was_active:
            # Ring once if we stayed quiet long enough. Requires a resolved PTY;
            # otherwise keep wanting until B5 resolves it.
            if self.pty and idle_elapsed >= IDLE_THRESHOLD:
                self.wants_ring = True
        elif self.active_bytes_total > 0 and idle_elapsed >= RESET_THRESHOLD:
            # A sub-threshold burst quiet for a LONG time (>= RESET_THRESHOLD, not
            # merely IDLE_THRESHOLD) is stale partial activity — forget it so separate
            # bursts far apart can't accumulate and spuriously cross MIN_ACTIVE_BYTES
            # (Bug 3). Using RESET_THRESHOLD (not IDLE_THRESHOLD) preserves a real
            # response streamed with a normal mid-stream pause, which must still ring.
            self.active_bytes_total = 0

    def on_rang(self) -> None:
        """Reset for the next response cycle after a bell fired for this PTY."""
        self.was_active = False
        self.active_bytes_total = 0
        self.wants_ring = False


# ── Pidfile / single-instance guard ──────────────────────────────────────────
# The pidfile stores "<pid>\n<starttime>\n". The starttime (field 22 of
# /proc/<pid>/stat, in clock ticks since boot) is an identity token that defeats
# PID reuse: a stale pidfile whose PID was recycled for an unrelated process has a
# different starttime, so we never treat it as alive and never SIGTERM it (Bug 2).
def proc_starttime(pid: int) -> str | None:
    """Field 22 of /proc/<pid>/stat (process start time), or None."""
    try:
        data = Path(f"/proc/{pid}/stat").read_text()
    except (FileNotFoundError, ProcessLookupError, PermissionError, OSError):
        return None
    # comm (field 2) is parenthesized and may contain spaces/parens — split after
    # the LAST ')'. The first token after it is field 3 (state), so field 22 is
    # index 19 in that remainder.
    rparen = data.rfind(")")
    if rparen == -1:
        return None
    fields = data[rparen + 2 :].split()
    return fields[19] if len(fields) > 19 else None


def _read_pidfile() -> tuple[int | None, str | None]:
    try:
        parts = PIDFILE.read_text().split()
        return int(parts[0]), (parts[1] if len(parts) > 1 else None)
    except (FileNotFoundError, ValueError, IndexError, OSError):
        return None, None


def running_pid() -> int | None:
    """The PID in the pidfile if that exact process instance is alive, else None.
    Clears a stale/mismatched pidfile as a side effect."""
    pid, recorded_start = _read_pidfile()
    if pid is None:
        return None
    try:
        os.kill(pid, 0)  # signal 0 = existence check only
    except (ProcessLookupError, PermissionError, OSError):
        PIDFILE.unlink(missing_ok=True)
        return None
    # PID is alive — but is it OUR watcher, or a reused PID? Compare start times.
    if recorded_start is not None and proc_starttime(pid) != recorded_start:
        PIDFILE.unlink(missing_ok=True)
        return None
    return pid


def is_running() -> bool:
    return running_pid() is not None


def acquire_pidfile() -> bool:
    """Atomically claim the pidfile (O_CREAT|O_EXCL). Returns False if a live
    watcher already holds it. Removes and retakes a stale pidfile. (Bug 1 —
    replaces the racy is_running()-then-write TOCTOU.)"""
    content = f"{os.getpid()}\n{proc_starttime(os.getpid()) or ''}\n".encode()
    for _ in range(3):
        try:
            fd = os.open(PIDFILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            if running_pid() is not None:
                return False  # a live watcher holds it
            # running_pid() already unlinked a stale-but-parseable file; the only file
            # that survives here is an EMPTY one (a failed os.write left it). Clear it —
            # but ONLY if it is still empty, so we never clobber a competitor watcher's
            # freshly-written (non-empty) pidfile that appeared in the race window.
            try:
                if PIDFILE.stat().st_size == 0:
                    PIDFILE.unlink(missing_ok=True)
            except FileNotFoundError:
                pass  # already gone — just retry the exclusive create
            except OSError:
                return False
            continue
        except OSError:
            return False
        try:
            os.write(fd, content)
        except OSError:
            os.close(fd)
            PIDFILE.unlink(missing_ok=True)  # don't leave an empty file that wedges restart
            return False
        os.close(fd)
        return True
    return False


def cleanup_pidfile() -> None:
    """Remove the pidfile only if it still points at us (don't clobber a successor)."""
    try:
        pid, _ = _read_pidfile()
        if pid == os.getpid():
            PIDFILE.unlink(missing_ok=True)
    except OSError:
        pass


# ── Main loop ────────────────────────────────────────────────────────────────
def watch() -> None:
    states: dict[int, ProcState] = {}
    log(
        f"watcher started (pid={os.getpid()}) commands={WATCH_COMMANDS} "
        f"poll={POLL_INTERVAL}s idle={IDLE_THRESHOLD}s min_bytes={MIN_ACTIVE_BYTES}"
    )
    while True:
        # A transient error in one poll must never kill the long-lived daemon;
        # log it (best-effort) and carry on next tick.
        try:
            now = time.monotonic()
            live = set(discover_pids())

            # Drop states for processes that have exited.
            for pid in [p for p in states if p not in live]:
                del states[pid]

            # Add new processes, deduping by PTY at intake (B2, first line of defense).
            tracked_ptys = {s.pty for s in states.values() if s.pty}
            for pid in live:
                if pid in states:
                    continue
                pty = get_pty(pid)
                if pty and pty in tracked_ptys:
                    continue  # another process on this PTY is already tracked
                states[pid] = ProcState(pid, pty)
                if pty:
                    tracked_ptys.add(pty)
                log(f"tracking {pid} pty={pty}")

            # Tick everyone (updates state, sets wants_ring).
            for st in states.values():
                st.tick(now)

            # Ring at most once per PTY (B2, decisive line of defense: survives the
            # intake race where two PIDs on one PTY were added before PTY resolved).
            rung: set[str] = set()
            for st in states.values():
                if st.wants_ring and st.pty and st.pty not in rung:
                    if ring_bell(st.pty):
                        rung.add(st.pty)
                        log(f"bell -> {st.pty} (pid={st.pid})")
            # Reset ALL states sharing a rung PTY (same terminal, same response cycle).
            if rung:
                for st in states.values():
                    if st.pty in rung:
                        st.on_rang()
        except Exception as e:  # noqa: BLE001 — a daemon must outlive a bad poll
            try:
                log(f"poll error (continuing): {e!r}")
            except Exception:
                pass

        time.sleep(POLL_INTERVAL)


def main() -> int:
    if "--is-running" in sys.argv:
        # Exit 0 if a watcher is already running, else 1 — the shell wrapper's guard.
        return 0 if is_running() else 1
    if "--stop" in sys.argv:
        pid = running_pid()
        if pid is None:
            print("no watcher running")
            return 1
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"stopped watcher pid={pid}")
            return 0
        except OSError as e:
            print(f"could not stop pid={pid}: {e}")
            return 1

    # Atomic claim — no is_running()-then-write race (Bug 1).
    if not acquire_pidfile():
        print(
            f"watcher already running (pid={running_pid()}); refusing to start a second",
            file=sys.stderr,
        )
        return 1

    # Clean the pidfile on any orderly exit or fatal signal.
    import atexit

    atexit.register(cleanup_pidfile)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    try:
        watch()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
