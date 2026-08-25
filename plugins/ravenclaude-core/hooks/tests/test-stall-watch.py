#!/usr/bin/env python3
"""test-stall-watch.py — Gate 244 for the stall watchdog.

ONE gate slot, five check groups. Claiming 244-248 for a single script would
inflate the gate count without adding a single independent invocation; Gate 242
already sets the precedent of several checks under one number.

Every check below exists because a specific defect was MEASURED during the FORGE
run that produced this tool, and each carries a must-fail half whose mutant is
PROVEN to flip the result. A must-fail half that cannot flip is vacuous: it
prints green while testing nothing, which is a defect class this repo has hit
before — so an impotent mutant fails the script rather than passing it.

  244a-d  paired fixture backtest           <- scope success signal (was vacuous)
  245a-c  progress-whitelist literals       <- RT-2 (44.3 min masking)
  246a-c  parse_ts is UTC-correct           <- R3 (UTC-vs-local, fails to silence)
  247a-c  ladder advances on RECEIPT        <- RT-4 (silent miss on sink outage)
  248a-c  no committed .plist; payload safe <- C19 oscillation, CE-2 injection

Run standalone:  python3 test-stall-watch.py
Invoked by:      scripts/audit-gates.sh  ->  .github/workflows/validate-marketplace.yml
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRIPTS = os.path.join(REPO, "plugins", "ravenclaude-core", "scripts")
FIXTURES = os.path.join(REPO, "tests", "fixtures", "stall-watchdog")

FAILURES = []
PASSES = []


def gate(name, ok, detail=""):
    (PASSES if ok else FAILURES).append(name)
    sys.stdout.write("  %-6s %s%s\n" % ("PASS" if ok else "FAIL", name,
                                        (" — " + detail) if detail else ""))


def load(mod):
    path = os.path.join(SCRIPTS, mod + ".py")
    spec = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read_skeleton(sid):
    path = os.path.join(FIXTURES, sid + ".skeleton.jsonl")
    with open(path) as fh:
        return [json.loads(l) for l in fh if l.strip()]


def manifest():
    with open(os.path.join(FIXTURES, "manifest.json")) as fh:
        return json.load(fh)


def age_min(records, as_of, progress_only, sw):
    """Age of the newest matching record. progress_only=True mirrors the real
    detector; False is the naive last-any-entry detector we rejected."""
    newest = None
    for rec in records:
        ts = rec.get("ts")
        if not ts:
            continue
        if progress_only and rec.get("type") not in sw.PROGRESS_TYPES:
            continue
        try:
            epoch = sw.parse_ts(ts)
        except ValueError:
            continue
        newest = epoch if newest is None else max(newest, epoch)
    return None if newest is None else (as_of - newest) / 60.0


# ---------------------------------------------------------------------------
# Gate 244 — the paired backtest. The original success criterion ("zero alerts
# for exited sessions") was VACUOUS: both candidate detectors are structurally
# incapable of alerting on an exited session, so it passed on a detector that
# did nothing. A negative control is not a result without its positive twin.
# ---------------------------------------------------------------------------
def gate_244(sw):
    man = manifest()
    as_of = sw.parse_ts(man["captured_utc"].replace("+00:00", "Z"))
    registry = {str(r.get("sessionId"))[:8]: r for r in man.get("registry_snapshot", [])}

    verdicts = {}
    for sid in man["sessions"]:
        recs = read_skeleton(sid)
        reg = registry.get(sid)
        if reg is None:                      # no registry entry -> not live
            verdicts[sid] = False
            continue
        if (reg.get("status") or "") == "idle":
            verdicts[sid] = False
            continue
        a = age_min(recs, as_of, True, sw)
        verdicts[sid] = a is not None and a > sw.STALL_THRESHOLD_MIN

    positives = [s for s, m in man["sessions"].items() if m["label"] == "POSITIVE"]
    negatives = [s for s, m in man["sessions"].items() if m["label"] == "NEGATIVE"]
    pos_ok = all(verdicts.get(s) for s in positives)
    neg_ok = not any(verdicts.get(s) for s in negatives)
    gate("244a positive control fires (%s)" % ",".join(positives), pos_ok,
         "" if pos_ok else "the known stall was NOT flagged — detector is a no-op")
    gate("244b negatives stay silent (%d)" % len(negatives), neg_ok,
         "" if neg_ok else "false positive on %s" % [s for s in negatives if verdicts.get(s)])

    # must-fail: the RT-2 mutant. Inject a RECENT non-progress record into the
    # stalled fixture. The naive last-any detector must now MISS the stall;
    # the real whitelist detector must still catch it. If the mutant does not
    # flip the naive detector, the mutant is impotent and this gate is vacuous.
    sid = positives[0]
    recs = read_skeleton(sid)
    recent = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(as_of - 60))
    mutant = recs + [{"ts": recent, "type": "system", "subtype": "away_summary",
                      "block_kinds": None}]
    naive = age_min(mutant, as_of, False, sw)
    real = age_min(mutant, as_of, True, sw)
    mutant_potent = naive is not None and naive <= sw.STALL_THRESHOLD_MIN
    real_survives = real is not None and real > sw.STALL_THRESHOLD_MIN
    gate("244c must-fail mutant is POTENT (naive detector misses)", mutant_potent,
         "" if mutant_potent else "mutant did not flip the naive detector — gate is VACUOUS")
    gate("244d whitelist detector survives the mutant", real_survives,
         "real=%.1fmin naive=%.1fmin" % (real or -1, naive or -1))


# ---------------------------------------------------------------------------
# Gate 245 — the observable must stay assistant-records-only. RT-2 measured a
# 44.3 minute mask on the real stall when last-any-entry was used.
# ---------------------------------------------------------------------------
def gate_245(sw):
    ok = sw.PROGRESS_TYPES == frozenset({"assistant"})
    gate("245a PROGRESS_TYPES is exactly {assistant}", ok, str(sorted(sw.PROGRESS_TYPES)))
    required = {"user", "queue-operation", "system", "attachment", "last-prompt"}
    missing = required - set(sw.NON_PROGRESS_TYPES)
    gate("245b measured resetters are all excluded", not missing,
         "" if not missing else "missing from exclusion list: %s" % sorted(missing))
    # must-fail: a mutant whitelist that admits `user` must change the verdict
    # on the real fixture, proving the literal is load-bearing and not decorative.
    man = manifest()
    as_of = sw.parse_ts(man["captured_utc"].replace("+00:00", "Z"))
    sid = [s for s, m in man["sessions"].items() if m["label"] == "POSITIVE"][0]
    recs = read_skeleton(sid)
    real = age_min(recs, as_of, True, sw)
    saved = sw.PROGRESS_TYPES
    try:
        sw.PROGRESS_TYPES = frozenset({"assistant", "user"})
        widened = age_min(recs, as_of, True, sw)
    finally:
        sw.PROGRESS_TYPES = saved
    flipped = widened is not None and real is not None and widened < real
    gate("245c must-fail: widening the whitelist changes the answer", flipped,
         "strict=%.1f widened=%.1f" % (real or -1, widened or -1))


# ---------------------------------------------------------------------------
# Gate 246 — parse_ts must be UTC. Plan A's procStart check compared a UTC field
# against local `ps` output and would have mismatched on EVERY session, failing
# toward silence: a detector that never fires while every signal reads green.
# ---------------------------------------------------------------------------
def gate_246(sw):
    got = sw.parse_ts("2026-08-25T14:05:32.599Z")
    expected = 1787666732.0  # 2026-08-25 14:05:32 UTC
    gate("246a parse_ts is UTC-correct", abs(got - expected) < 1.0,
         "got %.0f expected %.0f" % (got, expected))
    # must-fail: the local-time implementation must give a DIFFERENT answer, or
    # this machine is in UTC and the test cannot discriminate — say so loudly
    # rather than pass by accident.
    local = time.mktime(time.strptime("2026-08-25T14:05:32", "%Y-%m-%dT%H:%M:%S"))
    if abs(local - expected) < 1.0:
        gate("246b must-fail discriminates", False,
             "host TZ is UTC — this gate cannot tell the bug from the fix here")
    else:
        gate("246b must-fail: mktime version differs (bug is detectable)", True,
             "delta %.0fs" % abs(local - expected))
    try:
        sw.parse_ts("not-a-timestamp")
        gate("246c rejects malformed timestamps", False, "accepted garbage")
    except ValueError:
        gate("246c rejects malformed timestamps", True)


# ---------------------------------------------------------------------------
# Gate 247 — the ladder must advance on RECEIPT, never on attempt. Advancing on
# attempt means a sink outage leaves state reading "alerted" while the owner
# hears nothing for six hours: the silent miss this tool exists to prevent.
# ---------------------------------------------------------------------------
def gate_247(sw):
    src = open(os.path.join(SCRIPTS, "stall_watch.py")).read()
    body = src.split("def evaluate(")[1].split("\ndef ")[0]
    mutates = '"rung"] = min(' in body or "episode['rung'] =" in body
    gate("247a evaluate() does NOT advance the rung", not mutates,
         "" if not mutates else "evaluate mutates rung — advance is not receipt-gated")
    has_fn = hasattr(sw, "advance_ladder")
    gate("247b advance_ladder() exists as a separate step", has_fn)
    if has_fn:
        state = {"episodes": {"1": {"rung": 0, "last_alert_at": 0.0, "opened_at": 0.0}}}
        sw.advance_ladder(state, [{"pid": 1}], time.time())
        rung = state["episodes"]["1"]["rung"]
        gate("247c advance_ladder actually advances (non-vacuous)", rung == 1,
             "rung=%s" % rung)


# ---------------------------------------------------------------------------
# Gate 248 — C19: a committed .plist is formatter-reachable and a covers[] entry
# on a toolchain-rewritten file oscillates forever. CE-2: a project directory
# name is attacker-influenceable and must never reach an interpolated string.
# ---------------------------------------------------------------------------
def gate_248(sw):
    try:
        tracked = subprocess.run(["git", "-C", REPO, "ls-files", "*.plist"],
                                 capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as exc:
        tracked = "ERROR:%s" % exc
    gate("248a no .plist is committed (it is generated at install)",
         tracked == "", tracked or "none tracked")

    reach = load("stall_reach")
    # Pure metacharacters. The validator keys on these characters, not on any
    # particular command, so this is the same test without writing something
    # that reads like a live instruction.
    hostile = 'a";b$c' + chr(96) + "d"
    try:
        reach.build_message([{"session": "aaaa", "project": hostile, "pid": 1,
                              "silent_min": 30, "masked_min": 1, "compactions": 0}])
        gate("248b payload rejects hostile identifiers", False,
             "build_message accepted quote/semicolon/dollar/backtick")
    except ValueError:
        gate("248b payload rejects hostile identifiers", True)
    # must-fail counterpart: a benign identifier must still be ACCEPTED, or the
    # validator is simply rejecting everything and proves nothing.
    try:
        reach.build_message([{"session": "aaaa", "project": "0" * 16, "pid": 1,
                              "silent_min": 30, "masked_min": 1, "compactions": 0}])
        gate("248c benign identifiers still accepted (validator not blanket-deny)", True)
    except ValueError as exc:
        gate("248c benign identifiers still accepted", False, str(exc))


def main():
    sys.stdout.write("Gates 244-248: stall watchdog\n")
    sw = load("stall_watch")
    for fn in (gate_244, gate_245, gate_246, gate_247, gate_248):
        try:
            fn(sw)
        except Exception as exc:
            gate(fn.__name__, False, "%s: %s" % (type(exc).__name__, exc))
    sys.stdout.write("\n  %d passed, %d failed\n" % (len(PASSES), len(FAILURES)))
    if FAILURES:
        sys.stdout.write("  FAILED: %s\n" % ", ".join(FAILURES))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
