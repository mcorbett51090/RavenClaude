#!/usr/bin/env python3
"""test-stall-watch-identity.py — the stall watchdog's PID-reuse guard.

proc_identity_ok() used to return bool(ps output), i.e. "this pid exists",
and nothing read the result, so after a SIGKILL a reused pid kept a dead
session's registry entry alive and the alert ladder escalated against an
unrelated process (repo-review 2026-10-19, 1005-P2-8). It now compares the
process's `ps -o etime=` with now - startedAt/1000, and evaluate() and the
launch-hang pass treat identity_ok False as not alive.

Every negative carries its positive control (the same setup DOES alert when
identity holds or is unknown), and each fix is re-run as an in-memory mutant
that must fail.

Run standalone: python3 test-stall-watch-identity.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "scripts", "stall_watch.py")

_fails: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print("  %s %s%s" % ("ok  " if cond else "FAIL", name, "" if cond else " — " + detail))
    if not cond:
        _fails.append(name)


def _load(src: str, name: str):
    d = tempfile.mkdtemp()
    p = os.path.join(d, name + ".py")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(src)
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _quiet(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a)


def _findings_for(sw, identity_ok) -> list:
    """evaluate() on one busy session whose transcript has been silent 999 min."""
    rec = {
        "pid": 4242,
        "session_id": "s" * 36,
        "status": "busy",
        "cwd": "/tmp",
        "alive": True,
        "identity_ok": identity_ok,
    }
    saved = (
        sw.read_registry,
        sw.find_transcript,
        sw.last_progress_age_min,
        sw.count_compact_boundaries,
    )
    try:
        sw.read_registry = lambda: ([rec], [])
        sw.find_transcript = lambda sid: "/dev/null"
        sw.last_progress_age_min = lambda p, n: (
            999.0,
            {"scanned_bytes": 0, "last_any_age_min": 999.0},
        )
        sw.count_compact_boundaries = lambda p: 0
        return _quiet(sw.evaluate, time.time(), False, {"episodes": {}})["findings"]
    finally:
        (
            sw.read_registry,
            sw.find_transcript,
            sw.last_progress_age_min,
            sw.count_compact_boundaries,
        ) = saved


def _identity_checks(sw) -> list[str]:
    """Return the names of identity assertions that fail on module `sw`."""
    bad = []
    now = time.time()
    me = os.getpid()
    # This test process started moments ago. A registry claiming the session
    # started 3 h ago is a different, younger process on a reused pid.
    if sw.proc_identity_ok(me, (now - 3 * 3600) * 1000, now) is not False:
        bad.append("reused pid (3 h recorded start, fresh process) -> False")
    if sw.proc_identity_ok(me, (now - 5) * 1000, now) is not True:
        bad.append("matching start (5 s ago) -> True")
    if _findings_for(sw, False):
        bad.append("identity_ok False -> no stall finding")
    return bad


def main() -> int:
    with open(SRC, encoding="utf-8") as fh:
        src = fh.read()
    sw = _load(src, "stall_watch_identity_real")

    print("== etime parsing ==")
    check("mm:ss", sw._parse_etime("05:07") == 307)
    check("hh:mm:ss", sw._parse_etime("1:02:03") == 3723)
    check("dd-hh:mm:ss", sw._parse_etime(" 2-01:02:03\n") == 2 * 86400 + 3723)
    check("garbage -> None", sw._parse_etime("abc") is None and sw._parse_etime("") is None)

    print("== proc_identity_ok ==")
    now = time.time()
    me = os.getpid()
    check(
        "reused pid: fresh process, 3 h recorded start -> False",
        sw.proc_identity_ok(me, (now - 3 * 3600) * 1000, now) is False,
    )
    check(
        "positive control: recorded start 5 s ago -> True",
        sw.proc_identity_ok(me, (now - 5) * 1000, now) is True,
    )
    check(
        "unknown start -> None (never suppresses)",
        sw.proc_identity_ok(me, None, now) is None
        and sw.proc_identity_ok(me, "bogus", now) is None,
    )
    check(
        "start in the future (clock skew) -> None",
        sw.proc_identity_ok(me, (now + 600) * 1000, now) is None,
    )

    print("== read_registry wires startedAt into identity_ok ==")
    with tempfile.TemporaryDirectory() as td:
        reg = {
            "pid": me,
            "sessionId": "r" * 36,
            "status": "busy",
            "cwd": "/tmp",
            "startedAt": int((now - 3 * 3600) * 1000),
        }
        with open(os.path.join(td, "%d.json" % me), "w", encoding="utf-8") as fh:
            json.dump(reg, fh)
        saved_dir = sw.SESSIONS_DIR
        try:
            sw.SESSIONS_DIR = td
            sessions, _ = sw.read_registry()
        finally:
            sw.SESSIONS_DIR = saved_dir
    check(
        "a live pid with a 3 h-old recorded start reads identity_ok False",
        len(sessions) == 1 and sessions[0]["identity_ok"] is False,
        str(sessions),
    )

    print("== evaluate() treats a reused pid as not alive ==")
    check("identity_ok False -> no stall finding", _findings_for(sw, False) == [])
    check(
        "positive control: identity_ok True -> a stall finding", len(_findings_for(sw, True)) == 1
    )
    check("identity_ok None (unknown) -> still a finding", len(_findings_for(sw, None)) == 1)

    print("== teeth ==")
    mutants = [
        (
            "identity = pid exists",
            "    return etime + IDENTITY_TOLERANCE_SEC >= expected\n",
            "    return True\n",
        ),
        (
            "evaluate ignores identity",
            '    return bool(sess.get("alive")) and sess.get("identity_ok") is not False\n',
            '    return bool(sess.get("alive"))\n',
        ),
    ]
    for label, old, new in mutants:
        if old not in src:
            check("teeth %s: mutation anchor present" % label, False, "update this test")
            continue
        mut = _load(src.replace(old, new, 1), "stall_watch_identity_mut")
        check("teeth: the '%s' mutant is caught" % label, bool(_identity_checks(mut)))

    if _fails:
        print("FAIL: test-stall-watch-identity.py (%d failing)" % len(_fails))
        return 1
    print("PASS: test-stall-watch-identity.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
