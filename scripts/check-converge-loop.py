#!/usr/bin/env python3
"""check-converge-loop.py — bidirectional audit gate for P3 of the Convergence
Engine: the full loop (loop.py) + the constrained report + the cross-model judge
contract (judge.sh).

The DEFAULT run proves an END-TO-END flawed→fixed fixture:
  - the loop converges within the iteration cap on a fixture that starts broken
    (a red objective hard gate), then gets fixed and refined to a plateau;
  - while the hard gate is red, ZERO judge calls are spent (objective-first), and
    the judge runs only after the gate goes green;
  - the loop emits the BEST iteration, not the last (a deliberate regression on
    the final iteration must not win);
  - the constrained report renders and contains NO over-claim word ("perfect"
    et al.); render_report() actively rejects a banned word;
  - the cross-model judge (judge.sh) refuses to self-grade (author==judge → exit
    5), trips the secret-egress backstop before transmitting, and honors the
    JUDGE_MOCK_VERDICT test hook (so this gate never calls claude).

BIDIRECTIONAL TEETH (--must-fail-keepbest): replace keep_best with "last wins"
and assert the loop THEN emits the regressed final iteration — proving keep-best
is what protects the output. Exit 0 iff the regression leaks (gate has teeth).

Stdlib-only. Exit 0 = all held. Exit 1 = a failure / teeth absent.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(
    REPO_ROOT, "plugins", "ravenclaude-core", "skills", "refine-to-rubric"
)
SCRIPTS = os.path.join(SKILL_DIR, "scripts")
JUDGE_SH = os.path.join(SCRIPTS, "judge.sh")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _Fail(Exception):
    pass


def _check(cond, msg):
    if not cond:
        raise _Fail(msg)
    print(f"  ✓ {msg}")


# An e2e rubric: one objective hard gate + one judge dimension.
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


class _Fixture:
    """A flawed→fixed→refined artifact trajectory, fully deterministic.

    Iteration 0: hard gate RED (broken) — judge must NOT run.
    Iteration 1: hard gate GREEN, judge scores correctness 0.5 (a finding).
    Iteration 2: refined — correctness 0.95.
    Iteration 3: refined — correctness 0.96 (plateau vs 2 within epsilon).
    Iteration 4+: a deliberate REGRESSION to 0.40 (keep-best must reject it).
    """

    def __init__(self, regress_after=99):
        self.regress_after = regress_after
        self.judge_calls = 0
        self.refine_calls = 0
        self._correctness = {1: 0.5, 2: 0.95, 3: 0.96}

    def evaluate_fn(self, idx):
        gate_green = idx >= 1
        scores = {"tests-pass": 1.0 if gate_green else 0.0}
        return {
            "judge_needed": gate_green,  # red gate → no judge (objective-first)
            "hard_gates": {"tests-pass": gate_green},
            "scores": scores,
            "judge_dimensions": ["correctness"] if gate_green else [],
        }

    def judge_fn(self, idx):
        self.judge_calls += 1
        if idx >= self.regress_after:
            c = 0.40  # regression
        else:
            c = self._correctness.get(idx, 0.96)
        findings = []
        if c < 0.6:
            findings = [{"dimension": "correctness", "severity": "high", "note": "gap"}]
        return {"scores": {"correctness": c}, "findings": findings}

    def refine_fn(self, idx):
        self.refine_calls += 1


def run_default():
    loop = _load("loop")

    cfg = {"iteration_cap": 10, "model_call_budget": 50, "score_floor": 0.85,
           "epsilon": 0.01, "plateau_patience": 2}

    # --- e2e: flawed → fixed → converges, BEST emitted, judge skipped while red ---
    fx = _Fixture(regress_after=99)
    sc = loop.run_loop(_rubric(), fx.evaluate_fn, fx.judge_fn, fx.refine_fn, config=cfg)
    v = sc["verdict"]
    _check(v["status"] == "rubric-pass", f"e2e flawed fixture converges to rubric-pass (got {v['status']})")
    _check(len(sc["iterations"]) <= cfg["iteration_cap"], "converged within the iteration cap")
    # iteration 0 had a red gate → its model_calls must be 1 (refine only, NO judge)
    it0 = sc["iterations"][0]
    _check(it0["model_calls"] == 1 and it0["hard_gates"]["tests-pass"] is False,
           "iteration 0 (red gate) spent NO judge call — refine only (objective-first)")
    _check(fx.judge_calls == len(sc["iterations"]) - 1,
           f"the judge ran once per non-broken iteration ({fx.judge_calls} calls)")

    # --- keep-best: a regression on the final iteration must NOT win ---
    fx = _Fixture(regress_after=3)  # iter 3+ regress to 0.40
    sc = loop.run_loop(_rubric(), fx.evaluate_fn, fx.judge_fn, fx.refine_fn,
                       config=dict(cfg, iteration_cap=5))
    v = sc["verdict"]
    best = v["best_index"]
    last = sc["iterations"][-1]["index"]
    _check(best != last or sc["iterations"][best]["score"] >= sc["iterations"][last]["score"],
           "keep-best never emits a worse last iteration")
    best_score = sc["iterations"][best]["score"]
    last_score = sc["iterations"][last]["score"]
    _check(best_score >= last_score, f"best score ({best_score:.2f}) >= last score ({last_score:.2f})")
    _check(last_score < best_score, "the fixture actually regressed on the last iteration (test is non-vacuous)")

    # --- the constrained report renders and contains NO over-claim word ---
    report = loop.render_report(sc)
    low = report.lower()
    for w in ("perfect", "flawless"):
        _check(w not in low, f"report does not contain over-claim word '{w}'")
    _check("residual" in low or "no residual gaps" in low, "report includes a residual-gaps section")

    # render_report ACTIVELY rejects a banned word (defense-in-depth)
    bad = {"verdict": {"status": "rubric-pass", "best_index": 0, "best_score": 1.0,
                       "reason": "this artifact is perfect", "residual_gaps": []},
           "iterations": [{"index": 0, "model_calls": 0}]}
    raised = False
    try:
        loop.render_report(bad)
    except AssertionError:
        raised = True
    _check(raised, "render_report rejects a verdict that would print a banned over-claim word")

    # --- the cross-model judge (judge.sh) security contract ---
    _check(os.path.isfile(JUDGE_SH), "judge.sh exists")
    # anti-self-grade: author family == judge family → exit 5 (date + non-date
    # suffix variants must all be caught — the broadened normalization closes the
    # -v2/-latest/-preview bypass the security review flagged).
    for jm in ("claude-opus-4-8-20260601", "claude-opus-4-8-v2",
               "claude-opus-4-8-latest", "claude-opus-4-8-preview"):
        rc = _run_judge({"JUDGE_ARTIFACT": "x", "JUDGE_AUTHOR_MODEL": "claude-opus-4-8",
                         "JUDGE_MODEL": jm, "JUDGE_MOCK_VERDICT": "pass"})
        _check(rc == 5, f"judge.sh refuses to self-grade (author=opus-4-8, judge={jm}, exit {rc})")
    # cross-model OK: different families → mock verdict, exit 0
    rc = _run_judge({"JUDGE_ARTIFACT": "x", "JUDGE_AUTHOR_MODEL": "claude-opus-4-8",
                     "JUDGE_MODEL": "claude-haiku-4-5", "JUDGE_MOCK_VERDICT": "pass"})
    _check(rc == 0, f"judge.sh runs when the judge model differs from the author (exit {rc})")
    # secret-egress backstop trips before the mock (artifact never transmitted)
    out = _run_judge_out({"JUDGE_ARTIFACT": "key AKIAIOSFODNN7EXAMPLE99",
                          "JUDGE_AUTHOR_MODEL": "claude-opus-4-8",
                          "JUDGE_MODEL": "claude-haiku-4-5", "JUDGE_MOCK_VERDICT": "pass"})
    _check("not sent to the model API" in out or "secret-egress" in out,
           "judge.sh secret-egress backstop refuses to transmit a secret-shaped artifact")

    return True


def _run_judge(env):
    full = dict(os.environ)
    full.update(env)
    return subprocess.run(["bash", JUDGE_SH], env=full, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL, check=False).returncode


def _run_judge_out(env):
    full = dict(os.environ)
    full.update(env)
    return subprocess.run(["bash", JUDGE_SH], env=full, capture_output=True,
                          text=True, check=False).stdout


def run_must_fail_keepbest():
    """Mutate keep_best → 'last wins'; the loop should THEN emit the regressed
    final iteration. If it does, keep-best is the real protection (teeth)."""
    loop = _load("loop")
    converge = loop.converge
    cfg = {"iteration_cap": 5, "model_call_budget": 50, "score_floor": 0.85,
           "epsilon": 0.01, "plateau_patience": 2}

    fx = _Fixture(regress_after=3)
    # sanity: intact keep-best does NOT emit the regressed last iteration — the
    # emitted iteration scores strictly higher than the regressed final one.
    sc = loop.run_loop(_rubric(), fx.evaluate_fn, fx.judge_fn, fx.refine_fn, config=cfg)
    its = sc["iterations"]
    last_idx = its[-1]["index"]
    last_score = its[-1]["score"]
    intact_best = sc["verdict"]["best_index"]
    if intact_best == last_idx or its[intact_best]["score"] <= last_score:
        print("  ✗ intact keep-best already emitted the regression — broken", file=sys.stderr)
        return False

    # mutant: keep_best returns the LAST index → the loop emits the regressed
    # final iteration (a strictly worse output than intact keep-best chose).
    converge.keep_best = lambda iterations: int(iterations[-1]["index"])
    fx = _Fixture(regress_after=3)
    sc = loop.run_loop(_rubric(), fx.evaluate_fn, fx.judge_fn, fx.refine_fn, config=cfg)
    best = sc["verdict"]["best_index"]
    if best == sc["iterations"][-1]["index"] and \
       sc["iterations"][best]["score"] < its[intact_best]["score"]:
        print("  ✓ mutant (last-wins keep_best) WRONGLY emits the regressed last iteration — gate has teeth")
        return True
    print(f"  ✗ mutant did not emit the regression (best={best}) — teeth not demonstrated", file=sys.stderr)
    return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--must-fail-keepbest", action="store_true")
    args = ap.parse_args(argv)
    try:
        ok = run_must_fail_keepbest() if args.must_fail_keepbest else run_default()
    except _Fail as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
