#!/usr/bin/env python3
"""check-evaluate.py — bidirectional audit gate for P2 of the Convergence Engine:
the OBJECTIVE-GATES-FIRST evaluator (skills/refine-to-rubric/scripts/evaluate.py).

The DEFAULT run proves the plan's hardest invariant:
  - a BROKEN artifact (a red objective hard gate) spends ZERO judge calls:
    evaluate() returns judge_needed=false → the loop short-circuits to refine;
  - a CLEAN artifact (all hard gates green, judge dims remain) returns
    judge_needed=true → the judge runs AFTER the objective gates;
  - an objective evaluator that ERRORS (exit 2 / cannot run) is treated as RED +
    blocking — an objective gate never fails open;
  - a signal with no bound command is NOT a silent pass — it becomes a judge dim;
  - objective dimension scores are populated (1.0 green / 0.0 red).

A real "judge call" is modeled by a counter incremented ONLY when judge_needed is
true — so the count is the loop's actual behavior, not an assertion about it.

BIDIRECTIONAL TEETH (--must-fail-judge-first): replace the loop's ordering with
the mutant that JUDGES FIRST (ignores judge_needed) and assert a broken artifact
THEN spends a judge call — proving the objective-first ordering is what saves it.
Exit 0 iff the leak (>=1 judge call on a broken artifact) is observed.

Stdlib-only. Exit 0 = all assertions held. Exit 1 = a failure / teeth absent.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL_PATH = os.path.join(
    REPO_ROOT, "plugins", "ravenclaude-core", "skills", "refine-to-rubric",
    "scripts", "evaluate.py",
)


def _load_eval():
    spec = importlib.util.spec_from_file_location("evaluate", EVAL_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _Fail(Exception):
    pass


def _check(cond, msg):
    if not cond:
        raise _Fail(msg)
    print(f"  ✓ {msg}")


# A rubric with one objective hard gate + one judge dimension.
def _rubric():
    return {
        "schema_version": "1.0.0",
        "artifact_kind": "code",
        "dimensions": [
            {"id": "tests-pass", "title": "Tests pass", "weight": 50,
             "source": "library", "verified": True, "hard_gate": True,
             "objective_signal": "lint-cmd"},
            {"id": "correctness", "title": "Correctness", "weight": 50,
             "source": "library", "verified": True, "hard_gate": False,
             "objective_signal": ""},
        ],
    }


def _runner_factory(exit_code):
    """A _runner stub mapping the bound signal's 'exit code' to (green, errored)
    without spawning a subprocess. Counts how many objective evaluators ran."""
    calls = {"n": 0}

    def runner(argv, timeout_s):
        if not argv:
            return (None, False)
        calls["n"] += 1
        if exit_code == 0:
            return (True, False)
        if exit_code == 1:
            return (False, False)
        return (False, True)  # exit 2+ → red + errored

    return runner, calls


def _loop_once(ev, rubric, signals, runner, judge_first=False):
    """Model one evaluate→(maybe)judge step. Returns the number of judge calls
    spent. In the CORRECT ordering the judge runs only when judge_needed is true.
    The judge_first mutant runs the judge regardless of judge_needed."""
    env = ev.evaluate(rubric, signals, _runner=runner)
    judge_calls = 0
    if judge_first:
        judge_calls += 1            # mutant: judges before/ignoring the gate verdict
    elif env["judge_needed"]:
        judge_calls += 1            # correct: judge only after objective gates pass
    return env, judge_calls


def run_default(ev):
    signals = {"lint-cmd": ["true"]}  # argv presence is what matters; runner is stubbed

    # broken artifact (red hard gate) → judge_needed false → 0 judge calls
    runner, calls = _runner_factory(exit_code=1)
    env, judge_calls = _loop_once(ev, _rubric(), signals, runner)
    _check(env["judge_needed"] is False, "broken artifact (red hard gate) → judge_needed=false")
    _check(judge_calls == 0, "broken artifact spends ZERO judge calls (short-circuit to refine)")
    _check(env["red_hard_gates"] == ["tests-pass"], "the red hard gate is named")
    _check(env["scores"].get("tests-pass") == 0.0, "red objective gate scores 0.0")
    _check(env["next_action"] == "refine", "broken artifact next_action = refine")
    _check(calls["n"] == 1, "the objective evaluator ran (1 subprocess)")

    # clean artifact (green hard gate, judge dim remains) → judge_needed true → 1 judge call
    runner, calls = _runner_factory(exit_code=0)
    env, judge_calls = _loop_once(ev, _rubric(), signals, runner)
    _check(env["judge_needed"] is True, "clean artifact (green hard gate + judge dim) → judge_needed=true")
    _check(judge_calls == 1, "clean artifact runs the judge AFTER the objective gate")
    _check(env["scores"].get("tests-pass") == 1.0, "green objective gate scores 1.0")
    _check("correctness" in env["judge_dimensions"], "the judge dimension is enumerated")
    _check(env["next_action"] == "judge", "clean artifact next_action = judge")

    # objective evaluator ERROR (exit 2) → red + blocking, errored recorded, 0 judge calls
    runner, calls = _runner_factory(exit_code=2)
    env, judge_calls = _loop_once(ev, _rubric(), signals, runner)
    _check(env["judge_needed"] is False, "objective evaluator error (exit 2) → judge_needed=false (never fail open)")
    _check("tests-pass" in env["objective_errors"], "the errored objective gate is recorded")
    _check(judge_calls == 0, "an evaluator error spends ZERO judge calls")

    # no command bound for a signal → judge dim, NOT a silent pass
    runner, _ = _runner_factory(exit_code=0)
    env, _jc = _loop_once(ev, _rubric(), {}, runner)  # empty signals map
    _check("tests-pass" not in env["hard_gates"],
           "an unbound objective signal is not silently marked a passing hard gate")

    # all judge dims, no hard gates green-or-red → still judge (no objective gate to block)
    judge_only = {
        "schema_version": "1.0.0", "artifact_kind": "prose",
        "dimensions": [{"id": "answers", "title": "Answers", "weight": 100,
                        "source": "library", "verified": True, "hard_gate": False,
                        "objective_signal": ""}],
    }
    runner, _ = _runner_factory(exit_code=0)
    env, judge_calls = _loop_once(ev, judge_only, signals, runner)
    _check(env["judge_needed"] is True and judge_calls == 1,
           "a purely judge-graded rubric proceeds to the judge")

    return True


def run_must_fail_judge_first(ev):
    """The judge-before-gates mutant: a broken artifact (red hard gate) is judged
    anyway (>=1 judge call). If the mutant leaks, the objective-first ordering is
    the real protection (teeth) → exit 0."""
    signals = {"lint-cmd": ["true"]}

    # sanity: correct ordering spends 0 judge calls on a broken artifact
    runner, _ = _runner_factory(exit_code=1)
    _env, judge_calls = _loop_once(ev, _rubric(), signals, runner, judge_first=False)
    if judge_calls != 0:
        print("  ✗ correct ordering already spent a judge call on a broken artifact — broken", file=sys.stderr)
        return False

    # mutant: judge first → a broken artifact spends a judge call
    runner, _ = _runner_factory(exit_code=1)
    _env, judge_calls = _loop_once(ev, _rubric(), signals, runner, judge_first=True)
    if judge_calls >= 1:
        print("  ✓ mutant (judge-before-gates) WRONGLY spends a judge call on a broken artifact — gate has teeth")
        return True
    print(f"  ✗ mutant did not spend a judge call (n={judge_calls}) — teeth not demonstrated", file=sys.stderr)
    return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--must-fail-judge-first", action="store_true")
    args = ap.parse_args(argv)

    ev = _load_eval()
    try:
        if args.must_fail_judge_first:
            ok = run_must_fail_judge_first(ev)
        else:
            ok = run_default(ev)
    except _Fail as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
