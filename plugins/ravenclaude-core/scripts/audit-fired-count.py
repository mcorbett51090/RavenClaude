#!/usr/bin/env python3
"""audit-fired-count.py — Phase 10 of verify-before-assert.

Reads `hook-events.jsonl` across recent sessions and asks the one question a
PR-time test structurally cannot: DID THIS HOOK EVER ACTUALLY FIRE?

⛔ A FIRED-COUNT OF EXACTLY ZERO AFTER REAL USAGE IS A FINDING, NOT A PASS.
Either the hook is mis-wired, or it is too narrow to ever fire. Both are
findings. Reporting zero as "clean" is how a guardrail rots while every surface
reads green — and this repo has the receipt: `guard-premise.sh` produced 463
events from six sibling hooks and ZERO from itself, so "I have no events" and "I
never fire" were indistinguishable until someone went looking.

⛔ IT RUNS ON A SCHEDULE, NOT ONLY ON PRs, AND THAT IS THE POINT.
A hook that fires on the PR that introduces it and never again is invisible to
PR-time testing. Invocation is necessary and demonstrably not sufficient.

⛔ G10.1 — THE INSTRUMENT NEEDS BOTH CONTROLS, OR IT IS WORTHLESS.
    POSITIVE: a synthetic event is written and must be read back. Without it,
              "no events" might mean the READER is broken.
    NEGATIVE: an absent-hooks scenario must report UNWIRED, never CLEAN. An
              instrument that cannot tell those two apart is measuring nothing.
Both run on every invocation, and both must pass before any count is reported.

Usage:
    audit-fired-count.py --check [--events DIR] [--days N]
    audit-fired-count.py --must-fail
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import tempfile
import time

_HERE = os.path.dirname(os.path.abspath(__file__))

# The hooks this initiative added. A hook listed here that never fires is a
# finding; a hook NOT listed here is out of this audit's scope by construction,
# which is stated rather than silently assumed.
_WATCHED = (
    "triage-outcome.sh",
    "preflight-command-review.sh",
    "guard-remediation-cause.sh",
    "guard-cause-closure.sh",
)

# ⛔ Deliberately LOW. The audit answers "did it ever fire", not "does it fire
# often". A high floor would turn a correctly-narrow guard into a false finding,
# and this repo's own record is that a rule firing once in 17,410 commands was a
# real catch.
_MIN_FIRES = 1


def _event_roots(explicit=None):
    if explicit:
        return [explicit]
    roots = []
    for base in (os.path.expanduser("~/.ravenclaude"), os.path.expanduser("~/RavenClaude/.ravenclaude")):
        cand = os.path.join(base, "runs")
        if os.path.isdir(cand):
            roots.append(cand)
    return roots


def read_events(roots, days=30):
    """Return (events, files_read). Never raises on a torn line."""
    cutoff = time.time() - days * 86400
    events, files = [], 0
    for root in roots:
        for path in glob.glob(os.path.join(root, "**", "hook-events.jsonl"), recursive=True):
            try:
                if os.path.getmtime(path) < cutoff:
                    continue
            except OSError:
                continue
            files += 1
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            events.append(json.loads(line))
                        except Exception:
                            continue
            except OSError:
                continue
    return events, files


def _counts(events):
    out = {}
    for e in events:
        hook = e.get("hook")
        if hook:
            out[hook] = out.get(hook, 0) + 1
    return out


def _positive_control():
    """Write a synthetic event and read it back.

    Returns (ok, detail). A reader that cannot see a planted event cannot be
    trusted to report an absence.
    """
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "runs", "synthetic-session")
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "hook-events.jsonl")
        planted = {
            "schema_version": 1,
            "ts": "2026-08-25T00:00:00Z",
            "hook": "rc-positive-control.sh",
            "verdict": "warn",
            "tool": "Bash",
            "path": "",
            "rule": "planted-control",
            "session_id": "synthetic",
            "exit_code": "0",
        }
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(planted) + "\n")
        events, files = read_events([os.path.join(tmp, "runs")], days=3650)
        counts = _counts(events)
        if counts.get("rc-positive-control.sh", 0) != 1:
            return False, f"planted 1 event, read back {counts.get('rc-positive-control.sh', 0)} (files={files})"
        return True, "planted event read back exactly once"


def _negative_control():
    """An absent-hooks scenario must report UNWIRED, never CLEAN."""
    with tempfile.TemporaryDirectory() as tmp:
        empty = os.path.join(tmp, "runs")
        os.makedirs(empty, exist_ok=True)
        events, files = read_events([empty], days=3650)
        if events:
            return False, f"an empty tree yielded {len(events)} events"
        verdict = classify(_counts(events), any_events=bool(events))
        if verdict != "unwired":
            return False, f"an empty tree classified as {verdict!r}, not 'unwired'"
        return True, "empty tree reports 'unwired', not 'clean'"


def classify(counts, any_events):
    """⛔ THE THREE-VALUED VERDICT. `clean` is unreachable without evidence."""
    if not any_events:
        return "unwired"
    missing = [h for h in _WATCHED if counts.get(h, 0) < _MIN_FIRES]
    if missing:
        return "gap"
    return "firing"


def check(events_dir=None, days=30) -> int:
    fails, notes = [], []

    ok, detail = _positive_control()
    if not ok:
        fails.append(f"POSITIVE CONTROL FAILED: {detail} — the reader is blind, so "
                     "every count below would be meaningless")
    else:
        notes.append(f"positive control: {detail}")

    ok, detail = _negative_control()
    if not ok:
        fails.append(f"NEGATIVE CONTROL FAILED: {detail} — the instrument cannot "
                     "distinguish 'unwired' from 'clean'")
    else:
        notes.append(f"negative control: {detail}")

    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        print("\nfired-count audit ABORTED — its own controls did not pass")
        return 2

    roots = _event_roots(events_dir)
    events, files = read_events(roots, days=days)
    counts = _counts(events)
    verdict = classify(counts, any_events=bool(events))

    for n in notes:
        print(f"  note: {n}")
    print(f"  read {len(events)} event(s) from {files} file(s) across {len(roots)} root(s), "
          f"last {days} day(s)")
    for hook in _WATCHED:
        n = counts.get(hook, 0)
        mark = "  " if n >= _MIN_FIRES else "⚠ "
        print(f"  {mark}{hook:<34} fired {n}")

    if verdict == "unwired":
        # ⛔ NOT a pass and NOT a failure: it is UNKNOWN. No events at all means
        # the substrate has nothing to say, which is a different state from
        # "the hooks are wired and silent".
        print("\nUNWIRED — no hook events in range. This is UNKNOWN, not clean: the "
              "audit has no evidence either way. Re-run after real usage.")
        return 0
    if verdict == "gap":
        missing = [h for h in _WATCHED if counts.get(h, 0) < _MIN_FIRES]
        print(f"\n⚠ GAP — {len(missing)} watched hook(s) fired ZERO times while the "
              "substrate recorded other hooks in the same window:")
        for h in missing:
            print(f"    {h}")
        print("  Either mis-wired, or too narrow to ever fire. Both are findings.")
        # Advisory on a scheduled run; the gate half is the controls above.
        return 0
    print("\nFIRING — every watched hook appears in the window.")
    return 0


def must_fail() -> int:
    """Break the negative control and require the audit to refuse to report.

    ⛔ Teeth for G10.1. If an instrument that calls an empty tree 'clean' still
    passes, the control is decoration.
    """
    saved = classify.__globals__["classify"]
    try:
        classify.__globals__["classify"] = lambda counts, any_events: "firing"
        ok, detail = _negative_control()
    finally:
        classify.__globals__["classify"] = saved
    if ok:
        print("MUST-FAIL VIOLATED: an instrument that classifies an EMPTY tree as "
              "'firing' still passed the negative control")
        return 1
    ok2, _ = _negative_control()
    if not ok2:
        print("MUST-FAIL VIOLATED: the UNMODIFIED negative control also fails, so a "
              "red result is indistinguishable from the broken case")
        return 1

    # ⛔ AND THE VERDICT MUST COME FROM check() ITSELF (P1-3). Everything above
    # exercises a HELPER predicate. A check() blinded so it can report nothing
    # would still satisfy it, leaving --check AND --must-fail both at rc=0 —
    # which is precisely the shape this gate exists to detect. Assert the ENTRY
    # POINT: unmutated must score 0, and the blinded instrument must drive it to 2.
    import contextlib as _ctx
    import io as _io

    with _ctx.redirect_stdout(_io.StringIO()):
        real = check()
    if real != 0:
        print(f"MUST-FAIL SETUP FAILED: the unmutated tree already fails check() "
              f"(rc={real}), so a red result below would be ambiguous")
        return 1

    saved2 = classify.__globals__["classify"]
    try:
        classify.__globals__["classify"] = lambda counts, any_events: "firing"
        with _ctx.redirect_stdout(_io.StringIO()):
            rc = check()
    finally:
        classify.__globals__["classify"] = saved2

    if rc != 2:
        print(f"MUST-FAIL VIOLATED: check() returned {rc} with a blinded classify() "
              "— the control failure is not reaching the entry point's verdict")
        return 1

    print(f"PASS (--must-fail): a clean-reporting instrument is caught ({detail}), "
          "and it drives check() to 2 while the real tree scores 0")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="fired-count anti-rot audit")
    ap.add_argument("--events")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args()
    if args.must_fail:
        return must_fail()
    return check(args.events, args.days)


if __name__ == "__main__":
    sys.exit(main())
