#!/usr/bin/env python3
"""loop.py — the Convergence Engine orchestrator (refine-to-rubric).

Ties the deterministic pieces together into the full loop:

    derive-rubric → [ evaluate (objective gates FIRST) → judge (cross-model,
    only after gates green) ] → score → terminate (deterministic) → refine →
    repeat → emit BEST iteration + a constrained report.

The orchestrator itself is deterministic *control flow*; the two model-touching
steps (judge, refine) are injected as callables so the loop is fully testable
without a model and so the SAME control flow runs in production with the real
cross-model judge (judge.sh) and the real author-agent refine step.

Invariants enforced here (the rest live in converge.py / evaluate.py / judge.sh):
  - objective evaluate runs BEFORE the judge every iteration (evaluate.py owns
    the short-circuit; loop.py never calls the judge when judge_needed is false);
  - terminate() is the ONLY stop authority (model-free);
  - keep-best: emit the argmax iteration, never blindly the last;
  - the report NEVER contains the word "perfect" (asserted on the way out);
  - a hard iteration cap + a model-call budget bound cost (converge.py defaults).

This module is import-friendly: run_loop() takes injected `evaluate_fn`,
`judge_fn`, `refine_fn`, `score_fn` so the audit gate drives an e2e with a
flawed→fixed fixture and no model. The CLI is a thin demonstration harness.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load_sibling(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


converge = _load_sibling("converge")


def _default_score_fn(rubric, objective_scores, judge_scores):
    """Merge objective + judge per-dimension scores, then weighted_score over
    graded dims. Objective scores win on a key collision (deterministic signals
    outrank a model opinion)."""
    merged = dict(judge_scores or {})
    merged.update(objective_scores or {})  # objective overrides judge
    return converge.weighted_score(rubric, merged), merged


def run_loop(rubric, evaluate_fn, judge_fn, refine_fn, config=None, score_fn=_default_score_fn):
    """Run the full convergence loop. Returns the scorecard dict (iterations +
    verdict). All four *_fn are injected:

      evaluate_fn(iteration_index) -> dict with keys:
          judge_needed (bool), hard_gates (dict id->bool), scores (dict id->float),
          judge_dimensions (list), model_calls (int, the objective subprocesses
          do not count as MODEL calls — pass 0 here; the judge call is counted
          separately by the loop).
      judge_fn(iteration_index) -> dict with keys:
          scores (dict id->float), findings (list of {dimension,severity,note}).
      refine_fn(iteration_index) -> None  (side effect: the author edits the
          artifact for the next iteration; the loop does not inspect it).

    The loop counts model calls (judge + refine) toward the budget and asks
    terminate() after EACH iteration whether to stop.
    """
    cfg = converge._resolve_config(config)
    iterations = []
    idx = 0
    while True:
        ev = evaluate_fn(idx)
        objective_scores = ev.get("scores", {})
        hard_gates = ev.get("hard_gates", {})
        model_calls = 0
        findings = []
        judge_scores = {}

        if ev.get("judge_needed"):
            verdict = judge_fn(idx) or {}
            judge_scores = verdict.get("scores", {})
            findings = verdict.get("findings", [])
            model_calls += 1  # the cross-model judge is one model call

        score, _merged = score_fn(rubric, objective_scores, judge_scores)
        iterations.append({
            "index": idx,
            "score": score,
            "scores": {**judge_scores, **objective_scores},
            "findings": findings,
            "hard_gates": hard_gates,
            "model_calls": model_calls,
        })

        should_stop, verdict = converge.terminate(rubric, iterations, cfg)
        if should_stop:
            break

        # refine is a model call too (the author re-edits); count it toward budget.
        refine_fn(idx)
        iterations[-1]["model_calls"] += 1
        # re-check budget immediately after refine so a refine that exhausts the
        # budget stops without spending another evaluate/judge cycle.
        should_stop, verdict = converge.terminate(rubric, iterations, cfg)
        if should_stop:
            break
        idx += 1

    scorecard = {
        "schema_version": converge.SCHEMA_VERSION,
        "config": {k: cfg[k] for k in cfg},
        "iterations": iterations,
        "verdict": verdict,
    }
    return scorecard


# ──────────────────────────────────────────────────────────────────────────────
# Constrained report — the engine reports honestly and NEVER claims "perfect".
# ──────────────────────────────────────────────────────────────────────────────
_BANNED_WORDS = ("perfect", "flawless", "100% complete", "essentially perfect")

_STATUS_BLURB = {
    "rubric-pass": "The artifact passes the bounded rubric (objective gates green, no new high/critical findings, score above the floor, and the score has plateaued). This is a rubric pass — not a claim of perfection.",
    "capped": "The iteration cap was reached before a rubric pass. Emitting the best iteration seen; residual gaps remain.",
    "plateaued": "The score plateaued below the floor — further refinement is not paying off. Escalating to a human; this is not a pass.",
    "budget-exhausted": "The model-call budget was exhausted. Emitting the best iteration seen; residual gaps remain.",
}


def render_report(scorecard):
    """Render a constrained, honest Markdown report. Raises AssertionError if any
    banned over-claim word would appear (defense-in-depth over the verdict vocab)."""
    v = scorecard["verdict"]
    status = v["status"]
    lines = []
    lines.append("# Convergence report")
    lines.append("")
    lines.append(f"- **Verdict:** `{status}`")
    lines.append(f"- **Best iteration:** {v['best_index']} (score {v['best_score']:.3f})")
    lines.append(f"- **Iterations run:** {len(scorecard['iterations'])}")
    total_calls = sum(it.get("model_calls", 0) for it in scorecard["iterations"])
    lines.append(f"- **Model calls spent:** {total_calls}")
    if v.get("escalate_to_human"):
        lines.append("- **Escalation:** this run is surfaced for human judgement (plateaued below the floor or below floor at a hard cap).")
    lines.append("")
    lines.append(_STATUS_BLURB.get(status, "Unknown verdict."))
    lines.append("")
    gaps = v.get("residual_gaps") or []
    if gaps:
        lines.append("## Residual gaps (Last-Mile)")
        lines.append("")
        for g in gaps:
            lines.append(f"- {g}")
    else:
        lines.append("No residual gaps recorded for the emitted iteration.")
    report = "\n".join(lines) + "\n"

    low = report.lower()
    for w in _BANNED_WORDS:
        assert w not in low, f"report contains a banned over-claim word: {w!r}"
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description="Convergence Engine demonstration harness.")
    ap.add_argument("--scorecard", help="render a constrained report from an existing scorecard JSON")
    args = ap.parse_args(argv)
    if args.scorecard:
        with open(args.scorecard, encoding="utf-8") as fh:
            sc = json.load(fh)
        sys.stdout.write(render_report(sc))
        return 0
    print("loop.py is the convergence orchestrator. See SKILL.md for the loop and "
          "judge.sh for the cross-model judge. Pass --scorecard to render a report.",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
