#!/usr/bin/env python3
"""check-converge.py — bidirectional audit gate for the Convergence Engine's
deterministic core (skills/refine-to-rubric/scripts/converge.py).

The DEFAULT run proves every termination case the plan enumerates resolves the
way the deterministic predicate must:

  1. converged          → rubric-pass (all gates green, no new blocker, >=floor, plateau)
  2. capped             → iteration cap reached, best-so-far emitted
  3. budget             → model-call budget exhausted, best-so-far emitted
  4. regression-revert  → keep-best argmax emits the BEST iteration, not the last
  5. plateau-below-floor→ plateaued, status=plateaued, escalate_to_human=true
  6. new-high-finding   → a NEW high/critical finding BLOCKS convergence (no stop)
  7. red-hard-gate      → a RED objective hard gate BLOCKS convergence (no stop)

It also proves weighted_score() ignores derived/unverified dimensions and that
keep-best resolves ties to the earliest index.

The BIDIRECTIONAL TEETH (--must-fail-redgate): a default run is not vacuous only
if the SAME harness, with the red-hard-gate guard disabled, WRONGLY converges.
This flag monkeypatches converge._red_hard_gates to report no red gates, then
asserts that a scorecard with a red hard gate THEN reports rubric-pass — proving
the guard is what blocks it. Exit 0 means the leak was observed (gate has teeth).

Exit 0 = all assertions held (gate passes). Exit 1 = an assertion failed.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONVERGE_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "ravenclaude-core",
    "skills",
    "refine-to-rubric",
    "scripts",
    "converge.py",
)


def _load_converge():
    spec = importlib.util.spec_from_file_location("converge", CONVERGE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures (built in-process — no temp files; deterministic)
# ──────────────────────────────────────────────────────────────────────────────
def _rubric(extra_dims=None):
    """A minimal rubric: two graded dims + one objective hard gate dim. Plus an
    optional derived/unverified dim to prove it is excluded from the score."""
    dims = [
        {"id": "completeness", "title": "Completeness", "weight": 50,
         "source": "library", "verified": True},
        {"id": "clarity", "title": "Clarity", "weight": 50,
         "source": "explicit", "verified": True},
        {"id": "lints-clean", "title": "Lints clean", "weight": 0,
         "source": "library", "verified": True, "hard_gate": True,
         "objective_signal": "lint-cmd"},
    ]
    if extra_dims:
        dims.extend(extra_dims)
    return {"schema_version": "1.0.0", "artifact_kind": "generic", "dimensions": dims}


def _it(index, score, *, findings=None, hard_gates=None, model_calls=1):
    return {
        "index": index,
        "score": score,
        "scores": {"completeness": score, "clarity": score},
        "findings": findings or [],
        "hard_gates": hard_gates if hard_gates is not None else {"lints-clean": True},
        "model_calls": model_calls,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Assertion helper
# ──────────────────────────────────────────────────────────────────────────────
class _Fail(Exception):
    pass


def _check(cond, msg):
    if not cond:
        raise _Fail(msg)
    print(f"  ✓ {msg}")


# ──────────────────────────────────────────────────────────────────────────────
# Default (must-pass) suite
# ──────────────────────────────────────────────────────────────────────────────
def run_default(cv):
    cfg = {"iteration_cap": 6, "model_call_budget": 12, "score_floor": 0.85,
           "epsilon": 0.01, "plateau_patience": 2}

    # --- weighted_score: derived/unverified excluded ---
    r = _rubric(extra_dims=[{
        "id": "derived-thing", "title": "Derived", "weight": 1000,
        "source": "derived", "verified": False,
        "provenance": "[unverified — derived]"}])
    s = cv.weighted_score(r, {"completeness": 1.0, "clarity": 1.0, "derived-thing": 1.0})
    _check(abs(s - 1.0) < 1e-9,
           f"weighted_score ignores a huge-weight derived/unverified dim (got {s})")
    s2 = cv.weighted_score(_rubric(), {"completeness": 1.0, "clarity": 0.0})
    _check(abs(s2 - 0.5) < 1e-9, f"weighted_score is the weighted mean of graded dims (got {s2})")

    # --- keep_best: argmax, ties → earliest ---
    its = [_it(0, 0.9), _it(1, 0.9), _it(2, 0.7)]
    _check(cv.keep_best(its) == 0, "keep_best resolves a tie to the earliest index")
    its2 = [_it(0, 0.5), _it(1, 0.95), _it(2, 0.6)]
    _check(cv.keep_best(its2) == 1, "keep_best picks the argmax (peak in the middle)")

    # --- case 1: converged → rubric-pass ---
    # last two step-deltas (0.005, 0.003) are each < epsilon → plateaued; >= floor
    its = [_it(0, 0.86), _it(1, 0.90), _it(2, 0.905), _it(3, 0.908)]
    stop, v = cv.terminate(_rubric(), its, cfg)
    _check(stop and v["status"] == "rubric-pass", f"case converged → rubric-pass (got {v['status']})")
    _check(v["best_index"] == 3, "converged emits the best (last/peak) index")

    # --- case 6: new-high-finding BLOCKS convergence (no stop) ---
    its = [_it(0, 0.90), _it(1, 0.905, findings=[{"dimension": "completeness", "severity": "high"}])]
    stop, v = cv.terminate(_rubric(), its, cfg)
    _check((not stop) and v["status"] is None,
           f"case new-high-finding → blocked, no stop (got stop={stop}, status={v['status']})")

    # --- case 7: red-hard-gate BLOCKS convergence (no stop) ---
    its = [_it(0, 0.90), _it(1, 0.95, hard_gates={"lints-clean": False})]
    stop, v = cv.terminate(_rubric(), its, cfg)
    _check((not stop) and v["status"] is None,
           f"case red-hard-gate → blocked, no stop even with high score (got stop={stop}, status={v['status']})")

    # --- case 2: capped (cap reached, not a clean pass) ---
    capcfg = dict(cfg, iteration_cap=3)
    its = [_it(0, 0.50), _it(1, 0.60), _it(2, 0.70)]  # below floor, still climbing
    stop, v = cv.terminate(_rubric(), its, capcfg)
    _check(stop and v["status"] == "capped", f"case capped → status capped (got {v['status']})")
    _check(v["best_index"] == 2 and v["escalate_to_human"] is True,
           "capped emits best-so-far and escalates when below floor")

    # --- case 3: budget exhausted ---
    bcfg = dict(cfg, model_call_budget=4)
    its = [_it(0, 0.50, model_calls=2), _it(1, 0.60, model_calls=2)]  # cumulative 4 == budget
    stop, v = cv.terminate(_rubric(), its, bcfg)
    _check(stop and v["status"] == "budget-exhausted",
           f"case budget → status budget-exhausted (got {v['status']})")

    # --- case 4: regression-revert (keep-best emits BEST not last) ---
    # force a stop via budget so we can inspect best_index: the last iteration
    # regressed to 0.40 but keep-best must emit index 1 (0.95), never the last.
    its_budget = [_it(0, 0.50, model_calls=4), _it(1, 0.95, model_calls=4), _it(2, 0.40, model_calls=4)]
    stop, v = cv.terminate(_rubric(), its_budget, dict(cfg, model_call_budget=12))
    _check(stop and v["best_index"] == 1 and abs(v["best_score"] - 0.95) < 1e-9,
           f"case regression-revert → emits best index 1 (got index={v['best_index']})")

    # --- case 5: plateau-below-floor → plateaued + escalate ---
    pcfg = dict(cfg, score_floor=0.95)  # floor unreachable by a 0.70 plateau
    its = [_it(0, 0.69), _it(1, 0.70), _it(2, 0.705), _it(3, 0.708)]  # plateau, below floor
    stop, v = cv.terminate(_rubric(), its, pcfg)
    _check(stop and v["status"] == "plateaued" and v["escalate_to_human"] is True,
           f"case plateau-below-floor → plateaued + escalate (got status={v['status']}, esc={v['escalate_to_human']})")

    # --- the engine NEVER says 'perfect' ---
    _check({cv.STATUS_RUBRIC_PASS, cv.STATUS_CAPPED, cv.STATUS_PLATEAUED, cv.STATUS_BUDGET}
           == {"rubric-pass", "capped", "plateaued", "budget-exhausted"},
           "verdict vocabulary is exactly the 4 honest statuses")

    # --- residual_gaps surfaces derived dims + below-full graded dims ---
    r = _rubric(extra_dims=[{
        "id": "derived-thing", "title": "Derived", "weight": 1,
        "source": "derived", "verified": False,
        "provenance": "[unverified — derived]"}])
    its = [_it(0, 0.86), _it(1, 0.90), _it(2, 0.905), _it(3, 0.908)]
    stop, v = cv.terminate(r, its, cfg)
    joined = " | ".join(v["residual_gaps"])
    _check(stop and "derived-thing" in joined,
           "residual_gaps surfaces the unverified derived dimension on a converged verdict")

    return True


# ──────────────────────────────────────────────────────────────────────────────
# Bidirectional teeth (must-fail): disable the red-hard-gate guard → it WRONGLY
# converges. If it does, the guard is real (the gate has teeth) → exit 0.
# ──────────────────────────────────────────────────────────────────────────────
def run_must_fail_redgate(cv):
    cfg = {"iteration_cap": 6, "model_call_budget": 12, "score_floor": 0.85,
           "epsilon": 0.01, "plateau_patience": 2}
    # A scorecard with a RED hard gate but otherwise a clean, plateaued, >=floor pass.
    its = [
        _it(0, 0.90, hard_gates={"lints-clean": False}),
        _it(1, 0.905, hard_gates={"lints-clean": False}),
        _it(2, 0.905, hard_gates={"lints-clean": False}),
    ]

    # sanity: with the guard INTACT it must NOT converge
    stop, v = cv.terminate(_rubric(), its, cfg)
    if stop and v["status"] == "rubric-pass":
        print("  ✗ guard intact already converged with a red hard gate — guard is broken", file=sys.stderr)
        return False

    # disable the guard (the mutant): pretend there are never any red hard gates
    cv._red_hard_gates = lambda iteration: []
    stop, v = cv.terminate(_rubric(), its, cfg)
    if stop and v["status"] == "rubric-pass":
        print("  ✓ mutant (no red-gate guard) WRONGLY converges with a red hard gate — gate has teeth")
        return True
    print(f"  ✗ mutant did NOT converge (stop={stop}, status={v['status']}) — teeth not demonstrated",
          file=sys.stderr)
    return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--must-fail-redgate", action="store_true",
                    help="disable the red-hard-gate guard and assert it then wrongly converges")
    args = ap.parse_args(argv)

    cv = _load_converge()
    try:
        if args.must_fail_redgate:
            ok = run_must_fail_redgate(cv)
        else:
            ok = run_default(cv)
    except _Fail as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
