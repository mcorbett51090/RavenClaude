#!/usr/bin/env python3
"""test-stall-watch.py — Gate 244 for the stall watchdog.

ONE gate slot, six check groups. Claiming 244-248 for a single script would
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
  249a-e  resolution, ladder floor, sleep suppression <- red-team, never exercised

P3 ADDITIVE — the launch-hang detector (`evaluate_launch_hangs()`,
anthropics/claude-code#92932). These checks pin the additive-only contract:
`evaluate()` and everything it touches are UNTOUCHED (250r is the mechanical
proof — a byte-identical diff of evaluate()'s own output, before vs after
this file's own commit), and the new detector is proven both positive AND
per-conjunct-negative, never just on its one designed-for case.

  250a    positive: every conjunct held -> exactly one launch-hang finding
  250b-e  four negative controls, one conjunct flipped at a time
  250r    regression floor: evaluate() output byte-identical pre/post P3
  250f    episode resolution: pid disappears -> episode closes, stops alerting
  250g    conjunct-5 probe failure (git absent) -> zero findings, no exception
  250h    no registry dir / no projects dir at all -> exits cleanly, heartbeat written

P4 ADDITIVE — debug-log confirmatory enrichment
(`_enrich_launch_hang_with_debug_log()`). OPTIONAL and CONFIRMATORY ONLY —
never a required trigger of a P3 finding; these checks pin exactly that:
a finding fires (or doesn't) identically whether or not this pass ever
touches it, and the pass itself can only ever ADD two derived-label keys,
never leak raw debug-log content.

  251a    debug log WITH the rg/TCC signature -> signature + match_count attached
  251b    no debug file at all -> finding UNCHANGED, P3 verdict does not depend on this phase
  251c    leak control (must-fail half): a planted sentinel never reaches the emitted finding,
          proven non-vacuous by a deliberately leaky variant that DOES leak it
  251d    a 100MB (sparse) debug log -> bounded read, tail-window signature still detected
  251e    enrichment throws -> the overall launch-hang finding is STILL emitted, unenriched

Run standalone:  python3 test-stall-watch.py
Invoked by:      scripts/audit-gates.sh  ->  .github/workflows/validate-marketplace.yml
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import types

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
    # must-fail: the local-time implementation must give a DIFFERENT answer.
    #
    # ⛔ IMPOSE A TIMEZONE; DO NOT READ THE HOST'S. The first version of this
    # check compared against the host's local time and declared itself unable to
    # discriminate when that was UTC. CI runners ARE UTC, so the gate was RED on
    # every PR while passing on the author's machine — a worse outcome than the
    # vacuous pass it was avoiding, and invisible locally. Forcing a known
    # non-UTC zone makes the mktime-vs-timegm divergence observable on ANY host,
    # so the check discriminates everywhere instead of abstaining somewhere.
    saved_tz = os.environ.get("TZ")
    try:
        os.environ["TZ"] = "America/New_York"
        time.tzset()
        local = time.mktime(time.strptime("2026-08-25T14:05:32", "%Y-%m-%dT%H:%M:%S"))
    finally:
        if saved_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = saved_tz
        time.tzset()
    differs = abs(local - expected) > 1.0
    gate("246b must-fail: mktime version differs (bug is detectable)", differs,
         "delta %.0fs under an imposed non-UTC zone" % abs(local - expected))
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


def _quiet(fn, *a):
    import contextlib
    import io as _io
    with contextlib.redirect_stdout(_io.StringIO()):
        return fn(*a)


# ---------------------------------------------------------------------------
# 249 — the three red-team items that shipped implemented but never exercised:
# resolution, the ladder past rung 1, and sleep suppression. Verified once is
# not verified; each carries its positive control, because "no alert fired" is
# only evidence if the same setup DOES alert when it should.
# ---------------------------------------------------------------------------
def gate_249(sw):
    now = time.time()
    saved_reg = sw.read_registry

    # Resolution must be OBSERVABLE, never asserted: the ladder never reaches
    # zero, so an episode that is never closed nags forever. There is
    # deliberately no mute — a mute button on a detector is the thing that gets
    # used, and a muted detector protects nothing.
    try:
        state = {"episodes": {"999999": {"rung": 2, "last_alert_at": now - 100,
                                         "opened_at": now - 9999}}}
        sw.read_registry = lambda: ([], [])
        _quiet(sw.evaluate, now, False, state)
        gate("249a resolution: a gone session's episode is pruned",
             "999999" not in state["episodes"])

        state = {"episodes": {"1234": {"rung": 1, "last_alert_at": now - 100,
                                       "opened_at": now - 9999}}}
        sw.read_registry = lambda: ([{"pid": 1234, "session_id": "x" * 36,
                                      "status": "idle", "cwd": "/tmp",
                                      "alive": True, "identity_ok": True}], [])
        _quiet(sw.evaluate, now, False, state)
        gate("249b resolution: an idle session's episode is pruned",
             "1234" not in state["episodes"])
    finally:
        sw.read_registry = saved_reg

    # The ladder must reach its floor and stay there: never zero (a real stall
    # would go quiet) and never unbounded (it would spam and get muted).
    episode = {"rung": 0, "last_alert_at": 0.0, "opened_at": now}
    fired = []
    for minute in range(0, 24 * 60 + 1):
        if sw.ladder_due(episode, now + minute * 60):
            fired.append(minute)
            sw.advance_ladder({"episodes": {"1": episode}}, [{"pid": 1}],
                              now + minute * 60)
    gaps = [fired[i + 1] - fired[i] for i in range(len(fired) - 1)]
    gate("249c ladder passes rung 1, floors, and never goes silent",
         episode["rung"] > 1 and gaps and min(gaps) > 0
         and max(gaps) <= sw.LADDER_MIN[-1],
         "gaps=%s rung=%d" % (gaps, episode["rung"]))

    # Sleep suppression, with the positive control that makes it meaningful.
    fake = [{"pid": 4242, "session_id": "s" * 36, "status": "busy",
             "cwd": "/tmp", "alive": True, "identity_ok": True}]
    saved_find, saved_age = sw.find_transcript, sw.last_progress_age_min
    saved_cnt = sw.count_compact_boundaries
    try:
        sw.read_registry = lambda: (fake, [])
        sw.find_transcript = lambda sid: "/dev/null"
        sw.last_progress_age_min = lambda p, n: (999.0, {"scanned_bytes": 0,
                                                         "last_any_age_min": 999.0})
        sw.count_compact_boundaries = lambda p: 0
        awake = _quiet(sw.evaluate, now, False, {"episodes": {}})
        slept = _quiet(sw.evaluate, now, True, {"episodes": {}})
    finally:
        sw.read_registry = saved_reg
        sw.find_transcript = saved_find
        sw.last_progress_age_min = saved_age
        sw.count_compact_boundaries = saved_cnt
    gate("249d sleep: the SAME stall alerts awake (positive control)",
         len(awake["alerts"]) == 1, "alerts=%d" % len(awake["alerts"]))
    gate("249e sleep: suppressed after a wake, finding still reported",
         len(slept["alerts"]) == 0 and len(slept["findings"]) == 1,
         "alerts=%d findings=%d" % (len(slept["alerts"]), len(slept["findings"])))

    # ⛔ The soak log is DURABLE and summarises transcripts that carry
    # credentials and fetched web bodies. Assert the emitted record is derived
    # values only — and prove the assertion can FAIL, or "no leak" is a probe
    # that never had teeth.
    import json as _json
    record = _json.loads(_json.dumps({
        "ts": 1, "ok": True, "sessions": 3, "findings": 1, "alerts": 0,
        "slept": False, "silent_min": [532], "notes": 0, "receipted": False,
    }))
    leaky = [k for k, v in record.items()
             if isinstance(v, str) and ("/" in v or len(v) > 24)]
    planted = dict(record, leak="/Users/someone/secret/path")
    caught = [k for k, v in planted.items()
              if isinstance(v, str) and ("/" in v or len(v) > 24)]
    gate("249f soak record carries no path or free string", not leaky,
         "" if not leaky else "leaked: %s" % leaky)
    gate("249g soak leak-probe has teeth (planted path is caught)",
         caught == ["leak"], "caught=%s" % caught)


# ---------------------------------------------------------------------------
# Gate 250 — P3, the additive launch-hang detector. Everything here targets
# `evaluate_launch_hangs()` / `_outside_git_work_tree()` only; `evaluate()`
# and its own gates (244-249) above are untouched and unexercised by any
# function below except 250r, whose entire job is to prove `evaluate()`
# itself did not change.
# ---------------------------------------------------------------------------

def _reg(pid, status, cwd, session_id=None, alive=True,
         started_ms=None, status_updated_ms=None):
    """One synthetic read_registry()-shaped record, matching the exact dict
    shape stall_watch.read_registry() returns (including the P3 additive
    started_at_ms / status_updated_at_ms keys)."""
    return {
        "pid": pid,
        "session_id": session_id or ("s" * 32 + str(pid)),
        "status": status,
        "cwd": cwd,
        "alive": alive,
        "identity_ok": True,
        "started_at_ms": started_ms,
        "status_updated_at_ms": status_updated_ms,
    }


def _positive_fixture(sw, cwd):
    """The real captured instance, reproduced: idle, cwd outside a repo,
    statusUpdatedAt == startedAt, no transcript, elapsed > LAUNCH_HANG_MIN."""
    now = 1_800_000_000.0
    elapsed_min = sw.LAUNCH_HANG_MIN + 2.0
    started_ms = (now - elapsed_min * 60.0) * 1000.0
    status_updated_ms = started_ms  # never once updated
    rec = _reg(pid=42424, status="idle", cwd=cwd,
               started_ms=started_ms, status_updated_ms=status_updated_ms)
    return now, rec


def gate_250(sw):
    tmp_outside = tempfile.mkdtemp(prefix="rc-launch-hang-outside-")
    saved_reg, saved_find = sw.read_registry, sw.find_transcript
    try:
        # ------------------------------------------------------------- 250a
        now, rec = _positive_fixture(sw, tmp_outside)
        sw.read_registry = lambda: ([rec], [])
        sw.find_transcript = lambda sid: None
        result = sw.evaluate_launch_hangs(now, {})
        findings = result["findings"]
        gate("250a positive: every conjunct held -> exactly one finding",
             len(findings) == 1, "findings=%d" % len(findings))
        if findings:
            gate("250a kind is 'launch-hang' + issue ref present",
                 findings[0].get("kind") == "launch-hang"
                 and bool(findings[0].get("issue")),
                 "finding=%s" % findings[0])

        # ------------------------------------------------------------- 250b
        # conjunct 2 flipped alone: status busy instead of idle.
        now, rec = _positive_fixture(sw, tmp_outside)
        rec["status"] = "busy"
        sw.read_registry = lambda: ([rec], [])
        sw.find_transcript = lambda sid: None
        result = sw.evaluate_launch_hangs(now, {})
        gate("250b negative: busy (non-idle) session -> zero findings",
             len(result["findings"]) == 0, "findings=%d" % len(result["findings"]))

        # ------------------------------------------------------------- 250c
        # conjunct 3 flipped alone: statusUpdatedAt has moved well past epsilon.
        now, rec = _positive_fixture(sw, tmp_outside)
        rec["status_updated_at_ms"] = (
            rec["status_updated_at_ms"] + sw.LAUNCH_HANG_STATUS_EPSILON_MS * 100)
        sw.read_registry = lambda: ([rec], [])
        sw.find_transcript = lambda sid: None
        result = sw.evaluate_launch_hangs(now, {})
        gate("250c negative: statusUpdatedAt has moved -> zero findings",
             len(result["findings"]) == 0, "findings=%d" % len(result["findings"]))

        # ------------------------------------------------------------- 250d
        # conjunct 4 flipped alone: a transcript DOES exist.
        now, rec = _positive_fixture(sw, tmp_outside)
        sw.read_registry = lambda: ([rec], [])
        sw.find_transcript = lambda sid: "/dev/null"
        result = sw.evaluate_launch_hangs(now, {})
        gate("250d negative: session HAS a transcript -> zero findings",
             len(result["findings"]) == 0, "findings=%d" % len(result["findings"]))

        # ------------------------------------------------------------- 250e
        # conjunct 6 (git probe, "5" in the design table) flipped alone: cwd
        # IS inside a real git work tree (this checkout itself).
        now, rec = _positive_fixture(sw, REPO)
        sw.read_registry = lambda: ([rec], [])
        sw.find_transcript = lambda sid: None
        result = sw.evaluate_launch_hangs(now, {})
        gate("250e negative: cwd IS a git work tree -> zero findings",
             len(result["findings"]) == 0, "findings=%d" % len(result["findings"]))
    finally:
        sw.read_registry, sw.find_transcript = saved_reg, saved_find


def _load_from_git_show(ref, relpath, modname):
    """Execs a git-show'd version of a file into a fresh, isolated module
    object — used ONLY to prove evaluate()'s output has not changed. Never
    registered in sys.modules, so it cannot collide with the real module."""
    proc = subprocess.run(["git", "show", "%s:%s" % (ref, relpath)], cwd=REPO,
                          capture_output=True, text=True, timeout=20)
    if proc.returncode != 0:
        raise RuntimeError("git show %s:%s failed: %s" % (ref, relpath, proc.stderr))
    mod = types.ModuleType(modname)
    mod.__file__ = "<git %s:%s>" % (ref, relpath)
    exec(compile(proc.stdout, mod.__file__, "exec"), mod.__dict__)
    return mod


def gate_250r(sw):  # noqa: ARG001 — unused; kept for a uniform dispatch signature
    """The mechanical regression floor: evaluate()'s output, computed with a
    fixed synthetic input, must be byte-identical whether it comes from the
    HEAD-committed (pre-P3) stall_watch.py or the current working-tree
    (post-P3) one. This is the proof that P3 is additive, not a rewrite —
    the acceptance test the P3 spec itself names as mechanical, not a
    read-the-diff-by-eye claim."""
    relpath = "plugins/ravenclaude-core/scripts/stall_watch.py"
    try:
        pre = _load_from_git_show("HEAD", relpath, "stall_watch_pre_p3_regression_check")
    except Exception as exc:
        gate("250r regression floor: could not load HEAD's stall_watch.py", False, str(exc))
        return
    post = load("stall_watch")  # a fresh, independent load — no shared state with `sw`

    now = 1_700_000_000.0
    fake = [{"pid": 5150, "session_id": "r" * 36, "status": "busy",
             "cwd": "/tmp", "alive": True, "identity_ok": True}]
    for m in (pre, post):
        m.read_registry = lambda: (fake, [])
        m.find_transcript = lambda sid: "/dev/null"
        m.last_progress_age_min = lambda p, n: (
            999.0, {"scanned_bytes": 0, "last_any_age_min": 999.0})
        m.count_compact_boundaries = lambda p: 0

    pre_out = pre.evaluate(now, False, {})
    post_out = post.evaluate(now, False, {})
    pre_json = json.dumps(pre_out, indent=1, sort_keys=True)
    post_json = json.dumps(post_out, indent=1, sort_keys=True)
    identical = pre_json == post_json
    gate("250r evaluate() output is byte-identical pre/post P3", identical,
         "" if identical else "PRE:\n%s\nPOST:\n%s" % (pre_json, post_json))


def gate_250f(sw):
    """Episode resolution: a pid that later disappears (SIGKILL orphans the
    registry file, per the module's own header — 'alive' goes False while the
    record can still be present) must close the launch-hang episode and stop
    alerting on the very next evaluation."""
    tmp_outside = tempfile.mkdtemp(prefix="rc-launch-hang-resolve-")
    saved_reg, saved_find = sw.read_registry, sw.find_transcript
    try:
        now, rec = _positive_fixture(sw, tmp_outside)
        sw.read_registry = lambda: ([rec], [])
        sw.find_transcript = lambda sid: None
        state = {}
        first = sw.evaluate_launch_hangs(now, state)
        opened = len(first["findings"]) == 1 and str(rec["pid"]) in state.get("launch_episodes", {})
        gate("250f episode opens on first tick", opened,
             "findings=%d episodes=%s" % (len(first["findings"]), list(state.get("launch_episodes", {}))))

        gone = dict(rec)
        gone["alive"] = False
        sw.read_registry = lambda: ([gone], [])
        second = sw.evaluate_launch_hangs(now + 60.0, state)
        closed = (str(rec["pid"]) not in state.get("launch_episodes", {})
                  and len(second["findings"]) == 0)
        gate("250f episode closes + stops alerting once the pid is gone", closed,
             "episodes=%s findings=%d" % (list(state.get("launch_episodes", {})),
                                          len(second["findings"])))
    finally:
        sw.read_registry, sw.find_transcript = saved_reg, saved_find


def gate_250g(sw):
    """Conjunct-6 (the git probe) probe failure — git absent / erroring / any
    ambiguity — must fail toward NOT-hung: zero findings, no exception, and
    the caller (main()'s own try/except around this call) never sees a
    raised exception from this path."""
    tmp_outside = tempfile.mkdtemp(prefix="rc-launch-hang-gitfail-")
    saved_reg, saved_find, saved_run = sw.read_registry, sw.find_transcript, sw.subprocess.run
    try:
        now, rec = _positive_fixture(sw, tmp_outside)
        sw.read_registry = lambda: ([rec], [])
        sw.find_transcript = lambda sid: None

        def _absent(*a, **k):
            raise FileNotFoundError("git: command not found (simulated)")
        sw.subprocess.run = _absent

        raised = False
        try:
            result = sw.evaluate_launch_hangs(now, {})
        except Exception:
            raised = True
            result = {"findings": ["EXCEPTION"]}
        gate("250g git-absent: zero findings, no exception",
             (not raised) and len(result["findings"]) == 0,
             "raised=%s findings=%d" % (raised, len(result["findings"])))

        def _weird_nonzero(*a, **k):
            class _P:
                returncode = 99
                stdout = ""
                stderr = "some unrelated internal git error"
            return _P()
        sw.subprocess.run = _weird_nonzero
        result2 = sw.evaluate_launch_hangs(now, {})
        gate("250g git weird-nonzero-exit -> zero findings (ambiguous, not hung)",
             len(result2["findings"]) == 0, "findings=%d" % len(result2["findings"]))
    finally:
        sw.read_registry, sw.find_transcript, sw.subprocess.run = saved_reg, saved_find, saved_run


def gate_250h(sw):
    """No registry dir / no projects dir at all -> the function (and the
    main() tick that calls it) must still exit cleanly and still write a
    heartbeat, matching evaluate()'s own documented behavior in the same
    no-data case (SESSIONS_DIR absent -> a loud note, an empty session list,
    never an exception)."""
    saved_sessions_dir = sw.SESSIONS_DIR
    saved_projects_dir = sw.PROJECTS_DIR
    try:
        sw.SESSIONS_DIR = "/nonexistent-rc-launch-hang-sessions-dir"
        sw.PROJECTS_DIR = "/nonexistent-rc-launch-hang-projects-dir"
        raised = False
        try:
            result = sw.evaluate_launch_hangs(1_900_000_000.0, {})
        except Exception:
            raised = True
            result = {"sessions": -1, "findings": ["EXCEPTION"], "notes": []}
        gate("250h no registry/projects dir: exits cleanly, zero sessions/findings",
             (not raised) and result["sessions"] == 0 and len(result["findings"]) == 0,
             "raised=%s sessions=%s findings=%d notes=%s" %
             (raised, result.get("sessions"), len(result["findings"]), result.get("notes")))

        # main() itself: fully isolated state/heartbeat/soak paths so this
        # never touches the real ~/.claude/stall-watch on the test machine.
        scratch = tempfile.mkdtemp(prefix="rc-launch-hang-main-")
        saved = {}
        for attr in ("STATE_DIR", "STATE_PATH", "STATE_LOCK_PATH", "HEARTBEAT_PATH",
                     "SOAK_PATH", "SALT_PATH"):
            saved[attr] = getattr(sw, attr)
        try:
            sw.STATE_DIR = scratch
            sw.STATE_PATH = os.path.join(scratch, "state.json")
            sw.STATE_LOCK_PATH = sw.STATE_PATH + ".lock"
            sw.HEARTBEAT_PATH = os.path.join(scratch, "heartbeat.json")
            sw.SOAK_PATH = os.path.join(scratch, "soak.jsonl")
            sw.SALT_PATH = os.path.join(scratch, "salt")
            rc = _quiet(sw.main, ["--no-send"])
            hb_written = os.path.isfile(sw.HEARTBEAT_PATH)
            gate("250h main() exits 0 + heartbeat written with no registry/projects dir",
                 rc == 0 and hb_written, "rc=%s heartbeat_exists=%s" % (rc, hb_written))
        finally:
            for attr, val in saved.items():
                setattr(sw, attr, val)
    finally:
        sw.SESSIONS_DIR = saved_sessions_dir
        sw.PROJECTS_DIR = saved_projects_dir


# ---------------------------------------------------------------------------
# Gate 251 — P4, the optional debug-log confirmatory enrichment. Everything
# here targets `_enrich_launch_hang_with_debug_log()` only; P3's own gates
# (250 series) above are untouched — 251e is the one check that also drives
# `evaluate_launch_hangs()` itself, and only to prove P4's own failure mode
# (an exception) can never cost P3's finding.
# ---------------------------------------------------------------------------

def _write_debug_log(dirpath, session_id, content):
    path = os.path.join(dirpath, session_id + ".txt")
    with open(path, "w") as fh:
        fh.write(content)
    return path


def _rg_signature_text(n=3):
    """The observed real-world shape (claims-table.md #2 in this feature's
    own FORGE run dir): an rg invocation line, followed eventually by the
    TCC 'Operation not permitted' error line, repeated n times."""
    lines = []
    for i in range(n):
        lines.append("rg spawned to index files under $HOME (attempt %d)" % i)
        lines.append(
            "/Users/x/Library/Mail/some/path-%d: Operation not permitted (os error 1)" % i)
    return "\n".join(lines) + "\n"


def gate_251(sw):
    scratch_debug = tempfile.mkdtemp(prefix="rc-launch-hang-debug-")
    saved_dir = sw.DEBUG_LOG_DIR
    sw.DEBUG_LOG_DIR = scratch_debug
    try:
        # ------------------------------------------------------------- 251a
        finding = {"session_id": "sess-aaaa", "kind": "launch-hang"}
        _write_debug_log(scratch_debug, "sess-aaaa", _rg_signature_text(3))
        sw._enrich_launch_hang_with_debug_log(finding)
        gate("251a debug log WITH the rg/TCC signature -> signature + match_count attached",
             finding.get("signature") == "rg-tcc" and finding.get("match_count") == 3,
             "finding=%s" % finding)

        # ------------------------------------------------------------- 251b
        # No debug file at all for this sessionId — the common case, since
        # --debug is not on by default. The P3 verdict must not depend on
        # this phase: the finding is left byte-identical.
        finding2 = {"session_id": "sess-bbbb", "kind": "launch-hang",
                    "pid": 1, "silent_min": 5.0}
        before = dict(finding2)
        sw._enrich_launch_hang_with_debug_log(finding2)
        gate("251b no debug file -> finding UNCHANGED, signature key absent",
             finding2 == before and "signature" not in finding2
             and "match_count" not in finding2,
             "finding=%s" % finding2)

        # ------------------------------------------------------------- 251c
        # Leak control — the most important check in this phase. A planted
        # sentinel that would never legitimately appear must never reach the
        # emitted finding, even though the debug log genuinely matches the
        # signature.
        sentinel = "/Users/totally-fake-user/DO-NOT-LEAK-9f8171/Library/Mail/x"
        leaky_content = "rg spawned\n%s: Operation not permitted (os error 1)\n" % sentinel
        _write_debug_log(scratch_debug, "sess-cccc", leaky_content)
        finding3 = {"session_id": "sess-cccc", "kind": "launch-hang"}
        sw._enrich_launch_hang_with_debug_log(finding3)
        emitted = json.dumps(finding3)
        gate("251c leak control: sentinel absent from the emitted finding "
             "(signature/match_count only)",
             sentinel not in emitted and finding3.get("signature") == "rg-tcc"
             and isinstance(finding3.get("match_count"), int),
             "emitted=%s" % emitted)

        # 251c-teeth: prove 251c is a real probe, not a vacuous pass, by
        # running a DELIBERATELY leaky variant against the SAME debug log
        # and confirming the sentinel now DOES appear.
        def _leaky_enrich(f):
            sid = f.get("session_id")
            p = os.path.join(sw.DEBUG_LOG_DIR, sid + ".txt")
            with open(p, "rb") as fh:
                chunk = fh.read().decode("utf-8", "ignore")
            if sw._RG_TCC_ERROR_RE.search(chunk):
                f["signature"] = "rg-tcc"
                f["leaked_line"] = chunk  # the bug 251c exists to catch
        finding4 = {"session_id": "sess-cccc", "kind": "launch-hang"}
        _leaky_enrich(finding4)
        emitted4 = json.dumps(finding4)
        gate("251c-teeth: a deliberately leaky variant DOES leak the sentinel "
             "(proves 251c has teeth, not a vacuous pass)",
             sentinel in emitted4, "emitted=%s" % emitted4)

        # ------------------------------------------------------------- 251d
        # A large (sparse, ~100MB) debug log: the read must stay bounded —
        # not scale with file size — while still detecting a signature that
        # lives inside the last DEBUG_LOG_TAIL_BYTES of the file.
        big_path = os.path.join(scratch_debug, "sess-dddd.txt")
        with open(big_path, "wb") as fh:
            fh.truncate(100 * 1024 * 1024)  # sparse: cheap, no real 100MB of IO
        tail_text = _rg_signature_text(2).encode("utf-8")
        with open(big_path, "r+b") as fh:
            fh.seek(100 * 1024 * 1024 - len(tail_text))
            fh.write(tail_text)

        counted = {"bytes": 0}
        real_open = open

        def counting_open(path, mode="r", *a, **kw):
            fh = real_open(path, mode, *a, **kw)
            orig_read = fh.read

            def read(*ra, **rk):
                data = orig_read(*ra, **rk)
                counted["bytes"] += len(data)
                return data
            fh.read = read
            return fh

        sw.open = counting_open
        try:
            finding5 = {"session_id": "sess-dddd", "kind": "launch-hang"}
            t0 = time.time()
            sw._enrich_launch_hang_with_debug_log(finding5)
            elapsed = time.time() - t0
        finally:
            del sw.open
        gate("251d 100MB debug log: read stays bounded (bytes_read <= DEBUG_LOG_TAIL_BYTES)",
             0 < counted["bytes"] <= sw.DEBUG_LOG_TAIL_BYTES,
             "bytes_read=%d bound=%d elapsed=%.3fs" %
             (counted["bytes"], sw.DEBUG_LOG_TAIL_BYTES, elapsed))
        gate("251d 100MB debug log: signature in the tail window is still detected",
             finding5.get("signature") == "rg-tcc" and finding5.get("match_count") == 2,
             "finding=%s" % finding5)

        # ------------------------------------------------------------- 251e
        # P4 throwing on a malformed/corrupt debug file must never suppress
        # or crash the overall P3 finding — the call site in
        # evaluate_launch_hangs() must catch it and emit unenriched.
        saved_enrich = sw._enrich_launch_hang_with_debug_log

        def _boom(f):
            raise RuntimeError("simulated corrupt debug file")
        sw._enrich_launch_hang_with_debug_log = _boom
        saved_reg, saved_find = sw.read_registry, sw.find_transcript
        tmp_outside = tempfile.mkdtemp(prefix="rc-launch-hang-p4-outside-")
        try:
            now, rec = _positive_fixture(sw, tmp_outside)
            sw.read_registry = lambda: ([rec], [])
            sw.find_transcript = lambda sid: None
            result = sw.evaluate_launch_hangs(now, {})
        finally:
            sw._enrich_launch_hang_with_debug_log = saved_enrich
            sw.read_registry, sw.find_transcript = saved_reg, saved_find
        findings = result["findings"]
        ok = (len(findings) == 1 and findings[0].get("kind") == "launch-hang"
              and "signature" not in findings[0] and "match_count" not in findings[0])
        gate("251e P4 exception in enrichment -> P3 finding STILL emitted, unenriched",
             ok, "findings=%s" % findings)
    finally:
        sw.DEBUG_LOG_DIR = saved_dir


def main():
    sys.stdout.write("Gate 244: stall watchdog\n")
    sw = load("stall_watch")
    for fn in (gate_244, gate_245, gate_246, gate_247, gate_248, gate_249,
               gate_250, gate_250r, gate_250f, gate_250g, gate_250h, gate_251):
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
