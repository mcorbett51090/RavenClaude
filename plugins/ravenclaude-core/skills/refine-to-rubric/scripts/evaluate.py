#!/usr/bin/env python3
"""evaluate.py — the OBJECTIVE-GATES-FIRST evaluator for the Convergence Engine.

This is the evaluate half of the refine→evaluate→refine loop, and it enforces the
plan's hardest invariant: **objective / deterministic gates run BEFORE any model
judge, and a broken artifact spends ZERO judge calls** (objective-first
short-circuit — the cost bound + the anti-self-grade ordering). The model judge
itself lives in P3; this module decides *whether the judge runs at all* and
produces the objective portion of an iteration scorecard.

How it works (deterministic; the only subprocesses are the objective evaluators,
each a versioned exit-coded CLI à la visual-feedback-loop/driver.py):

  - For each rubric dimension that carries an `objective_signal`, look up the
    command bound to that signal in the run config (signal → argv). Run it as a
    subprocess and read its EXIT CODE (the marketplace contract):
        exit 0 → green (gate passed / score 1.0)
        exit 1 → red   (gate failed / score 0.0)
        exit 2 → error → treated as RED + blocking (an evaluator that cannot run
                 is not a pass — never fail open on an objective gate)
  - Populate `hard_gates` (for hard_gate dims) and the objective `scores`.
  - Decide `judge_needed`: FALSE when any objective HARD GATE is red (short-circuit
    straight to refine — the judge would be wasted on a broken artifact) OR when
    there are no judge-graded dimensions at all; TRUE only when every objective
    hard gate is green AND at least one dimension still needs the cross-model judge.

The output envelope (printed as JSON) merges into a scorecard iteration. It carries
ONLY derived labels (booleans, [0,1] scores, the judge_needed flag, fixed-vocab
reason) — never a raw artifact echo.

CLI:
  python3 evaluate.py --rubric R.json --signals S.json [--timeout 60]
      --signals maps each objective_signal token to an argv list, e.g.
        {"lint-cmd": ["bash","-c","ruff check ."], "driver.py": ["python3","..."]}
      exit 0 → judge_needed is true  (objective gates green; proceed to judge)
      exit 1 → judge_needed is false (short-circuit to refine; a gate is red OR
               nothing left to judge)
      exit 2 → I/O / parse / contract error
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

SCHEMA_VERSION = "1.0.0"
DEFAULT_TIMEOUT_S = 60


def _run_signal(argv, timeout_s):
    """Run an objective evaluator subprocess; map its exit code to a verdict.
    Returns (green: bool|None, errored: bool). green=None means 'no command bound'
    (the dimension is judge-graded, not objective)."""
    if not argv:
        return (None, False)
    try:
        proc = subprocess.run(
            argv,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout_s,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        # cannot run / timed out → RED + errored (objective gate never fails open)
        return (False, True)
    rc = proc.returncode
    if rc == 0:
        return (True, False)
    if rc == 1:
        return (False, False)
    # exit 2+ → evaluator error → RED + blocking
    return (False, True)


def evaluate(rubric, signals, timeout_s=DEFAULT_TIMEOUT_S, _runner=_run_signal):
    """Run the objective gates for a rubric. Returns an evaluation envelope dict.
    `signals` maps an objective_signal token → an argv list. `_runner` is injected
    for testing (the audit gate stubs it so the gate needs no real evaluators)."""
    hard_gates = {}
    scores = {}
    objective_errors = []
    judge_dims = []

    for dim in rubric.get("dimensions", []):
        did = dim["id"]
        signal = dim.get("objective_signal") or ""
        # Delegated signals (e.g. agent-quality-rubric) are not objective CLIs;
        # they are handled by the delegated skill, not run here.
        if not signal or signal == "agent-quality-rubric":
            if dim.get("source") in ("library", "explicit") and bool(dim.get("verified")):
                judge_dims.append(did)
            continue
        argv = signals.get(signal)
        green, errored = _runner(argv, timeout_s)
        if green is None:
            # no command bound for this signal → treat as a judge dim, not a silent pass
            if dim.get("source") in ("library", "explicit") and bool(dim.get("verified")):
                judge_dims.append(did)
            continue
        scores[did] = 1.0 if green else 0.0
        if dim.get("hard_gate"):
            hard_gates[did] = bool(green)
        if errored:
            objective_errors.append(did)

    red_hard_gates = sorted(d for d, ok in hard_gates.items() if not ok)

    # judge_needed: only when every objective hard gate is green AND something
    # still needs the cross-model judge. A red hard gate short-circuits to refine
    # (0 judge calls). No judge dims → nothing for the judge to do.
    if red_hard_gates:
        judge_needed = False
        reason = f"short-circuit: red objective hard gate(s): {','.join(red_hard_gates)}"
        next_action = "refine"
    elif not judge_dims:
        judge_needed = False
        reason = "objective gates green; no judge-graded dimensions remain"
        next_action = "emit"
    else:
        judge_needed = True
        reason = "objective gates green; cross-model judge required"
        next_action = "judge"

    return {
        "schema_version": SCHEMA_VERSION,
        "judge_needed": judge_needed,
        "next_action": next_action,
        "reason": reason,
        "hard_gates": hard_gates,
        "red_hard_gates": red_hard_gates,
        "scores": scores,
        "objective_errors": objective_errors,
        "judge_dimensions": judge_dims,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Objective-gates-first evaluator.")
    ap.add_argument("--rubric", required=True)
    ap.add_argument("--signals", required=True,
                    help="JSON file mapping objective_signal token → argv list")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    args = ap.parse_args(argv)

    try:
        with open(args.rubric, encoding="utf-8") as fh:
            rubric = json.load(fh)
        with open(args.signals, encoding="utf-8") as fh:
            signals = json.load(fh)
        if not isinstance(signals, dict):
            raise ValueError("--signals must be a JSON object")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"evaluate: cannot read inputs: {exc}", file=sys.stderr)
        return 2

    env = evaluate(rubric, signals, timeout_s=args.timeout)
    print(json.dumps(env, indent=2, sort_keys=True))
    return 0 if env["judge_needed"] else 1


if __name__ == "__main__":
    sys.exit(main())
