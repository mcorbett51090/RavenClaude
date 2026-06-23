#!/usr/bin/env python3
"""converge.py — the deterministic, MODEL-FREE core of the Convergence Engine
("refine-to-rubric").

This module is the *referee* for the refine→evaluate→refine loop. It contains
NO model call and NO network access. The stop decision is a pure function of the
scorecard history + the rubric + the config knobs — never a model judgment. That
is the central anti-failure-mode of the whole engine (Huang et al. 2310.01798:
pure self-critique without an external signal does not reliably improve and often
degrades — so the authority to STOP must live outside any model).

Three pure functions, all deterministic and stdlib-only:

  weighted_score(rubric, scores)
      The weighted mean over GRADED dimensions only (source in {library,explicit}
      AND verified=true). Derived/unverified dimensions are NEVER counted toward
      the score — they are surfaced as residual gaps. Returns a float in [0,1].

  keep_best(iterations)
      argmax over the iteration scores → the index of the BEST iteration. Ties
      resolve to the EARLIEST index (the cheapest artifact that reached the peak;
      also makes regression-revert deterministic). Returns an int index.

  terminate(rubric, iterations, config)
      The deterministic stop predicate. Returns (should_stop, verdict) where
      verdict has a fixed-vocabulary status — NEVER "perfect":
          rubric-pass | capped | plateaued | budget-exhausted
      plus best_index (keep-best argmax), best_score, a fixed-vocabulary reason,
      a residual_gaps Last-Mile list, and escalate_to_human (plateau below floor).

CLI (for the audit gate + ad-hoc use):
  python3 converge.py --rubric R.json --scorecard S.json [--emit-verdict]
      exit 0 → should_stop is true  (a verdict was reached)
      exit 1 → should_stop is false (the loop should continue)
      exit 2 → I/O / parse / contract error
  With --emit-verdict the verdict JSON is printed to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys

SCHEMA_VERSION = "1.0.0"  # contract version of the scorecard/rubric envelopes

# Defaults for the deterministic stop policy. A scorecard may override any of
# these via its `config` block; these are the engine's safe defaults.
DEFAULTS = {
    "iteration_cap": 6,
    "model_call_budget": 12,
    "score_floor": 0.85,
    "epsilon": 0.01,
    "plateau_patience": 2,
}

# The finding severities that BLOCK convergence when newly introduced.
BLOCKING_SEVERITIES = ("critical", "high")

# Fixed verdict vocabulary — the engine NEVER claims "perfect".
STATUS_RUBRIC_PASS = "rubric-pass"
STATUS_CAPPED = "capped"
STATUS_PLATEAUED = "plateaued"
STATUS_BUDGET = "budget-exhausted"


# ──────────────────────────────────────────────────────────────────────────────
# Pure scoring helpers
# ──────────────────────────────────────────────────────────────────────────────
def _graded_dimensions(rubric):
    """The dimensions sanctioned for automatic grading: library/explicit AND
    verified. Derived or unverified dimensions are excluded by contract — this is
    the anti-reward-hack + anti-self-grade boundary in code."""
    out = []
    for dim in rubric.get("dimensions", []):
        if dim.get("source") in ("library", "explicit") and bool(dim.get("verified")):
            out.append(dim)
    return out


def weighted_score(rubric, scores):
    """Weighted mean over GRADED dimensions only, in [0,1].

    `scores` is a dict {dimension_id: raw_score_in_0_1}. A graded dimension with
    no score present is treated as 0 (absence of a passing signal is not a pass).
    If the total weight of graded dimensions is 0 (or there are none), returns
    0.0 — there is nothing the engine is allowed to grade, so it cannot claim a
    high score.
    """
    graded = _graded_dimensions(rubric)
    total_w = 0.0
    acc = 0.0
    for dim in graded:
        w = float(dim.get("weight", 0))
        if w <= 0:
            continue
        raw = scores.get(dim["id"], 0.0)
        try:
            raw = float(raw)
        except (TypeError, ValueError):
            raw = 0.0
        raw = max(0.0, min(1.0, raw))
        acc += w * raw
        total_w += w
    if total_w <= 0:
        return 0.0
    return acc / total_w


def keep_best(iterations):
    """argmax over iteration `score`, ties → EARLIEST index. Returns -1 for an
    empty history. This is the keep-best / regression-revert core: the loop emits
    THIS index, never blindly the last."""
    best_i = -1
    best_s = None
    for it in iterations:
        s = float(it.get("score", 0.0))
        if best_s is None or s > best_s:
            best_s = s
            best_i = int(it["index"])
    return best_i


# ──────────────────────────────────────────────────────────────────────────────
# Finding / hard-gate analysis (all deterministic)
# ──────────────────────────────────────────────────────────────────────────────
def _blocking_findings(iteration):
    """The set of (dimension, severity) blocking findings in an iteration."""
    out = set()
    for f in iteration.get("findings", []):
        if f.get("severity") in BLOCKING_SEVERITIES:
            out.add((f.get("dimension", ""), f.get("severity", "")))
    return out


def _has_new_blocking_finding(iterations, idx):
    """True if iteration `idx` introduced a blocking (high/critical) finding that
    was NOT present in the immediately preceding iteration. A pre-existing blocker
    that is being worked is not 'new'; a regression that re-introduces one IS."""
    if idx <= 0:
        # Iteration 0: any blocking finding counts as 'new' (nothing precedes it).
        return len(_blocking_findings(iterations[idx])) > 0
    prev = _blocking_findings(iterations[idx - 1])
    cur = _blocking_findings(iterations[idx])
    return len(cur - prev) > 0


def _red_hard_gates(iteration):
    """List of dimension ids whose objective hard gate is RED (False) in this
    iteration. A red hard gate blocks convergence regardless of the weighted
    score — objective signals are the primary stop authority."""
    return sorted(d for d, ok in iteration.get("hard_gates", {}).items() if not ok)


def _total_model_calls(iterations):
    return sum(int(it.get("model_calls", 0)) for it in iterations)


def _residual_gaps(rubric, iteration):
    """Honest Last-Mile list for the emitted iteration: every GRADED dimension
    scoring below 1.0, every RED hard gate, plus every UNVERIFIED/derived
    dimension (surfaced, never silently graded)."""
    gaps = []
    scores = iteration.get("scores", {})
    for dim in rubric.get("dimensions", []):
        did = dim["id"]
        if dim.get("source") in ("library", "explicit") and bool(dim.get("verified")):
            raw = scores.get(did, 0.0)
            try:
                raw = float(raw)
            except (TypeError, ValueError):
                raw = 0.0
            if raw < 1.0:
                gaps.append(f"{did}: graded score {raw:.2f} (below full marks)")
        else:
            # derived or unverified → never auto-graded; always surfaced
            prov = dim.get("provenance") or "[unverified — derived]"
            gaps.append(f"{did}: {prov} — not auto-graded, needs human review")
    for did in _red_hard_gates(iteration):
        gaps.append(f"{did}: objective hard gate RED")
    return gaps


# ──────────────────────────────────────────────────────────────────────────────
# The deterministic stop predicate
# ──────────────────────────────────────────────────────────────────────────────
def _resolve_config(config):
    cfg = dict(DEFAULTS)
    for k, v in (config or {}).items():
        if v is not None:
            cfg[k] = v
    return cfg


def terminate(rubric, iterations, config=None):
    """The model-free stop predicate. Returns (should_stop: bool, verdict: dict).

    Decision order (precedence is load-bearing):
      0. No iterations yet → do not stop.
      1. HARD STOP — budget exhausted (cumulative model calls ≥ budget): stop with
         best-so-far. status = budget-exhausted.
      2. HARD STOP — iteration cap reached: stop with best-so-far. status =
         capped, UNLESS the best iteration also cleanly satisfies the rubric (then
         rubric-pass — a cap that coincides with success is still success).
      3. BLOCKERS (these PREVENT a rubric-pass on the latest iteration but do not
         themselves force a stop): a RED objective hard gate, or a NEW high/critical
         finding on the latest iteration. If either holds and no hard cap fired,
         do NOT stop — keep iterating.
      4. CONVERGENCE — rubric-pass requires ALL of, on the latest iteration:
         all hard gates green, no new blocking finding, score ≥ floor, AND the
         score has plateaued (Δ < epsilon vs the prior best for `patience` iters).
      5. PLATEAU below floor — the score plateaued but never reached the floor:
         stop and ESCALATE TO HUMAN. status = plateaued.
      6. Otherwise → do not stop (keep refining).

    keep-best: the emitted best_index is the argmax over iteration scores (ties →
    earliest), so a regression in the last iteration never wins.
    """
    cfg = _resolve_config(config)
    verdict = {
        "status": None,
        "best_index": -1,
        "best_score": 0.0,
        "reason": "",
        "residual_gaps": [],
        "escalate_to_human": False,
    }

    if not iterations:
        verdict["reason"] = "no iterations yet"
        return (False, verdict)

    # keep-best argmax (used by every stopping branch)
    best_index = keep_best(iterations)
    best_it = next(it for it in iterations if int(it["index"]) == best_index)
    best_score = float(best_it.get("score", 0.0))
    verdict["best_index"] = best_index
    verdict["best_score"] = best_score

    latest = iterations[-1]
    n_iters = len(iterations)

    red_gates = _red_hard_gates(latest)
    new_blocker = _has_new_blocking_finding(iterations, len(iterations) - 1)

    # Plateau detection: the last `patience` step-to-step deltas are EACH below
    # epsilon — i.e. the score has stopped meaningfully moving for `patience`
    # iterations. Gains are front-loaded (the research finding), so a sustained
    # sub-epsilon tail means further refinement is not paying off.
    def _plateaued():
        patience = int(cfg["plateau_patience"])
        if n_iters < patience + 1:
            return False
        window = iterations[-(patience + 1):]
        for prev, cur in zip(window, window[1:]):
            delta = abs(float(cur.get("score", 0.0)) - float(prev.get("score", 0.0)))
            if delta >= float(cfg["epsilon"]):
                return False
        return True

    clean_pass = (
        not red_gates
        and not new_blocker
        and float(latest.get("score", 0.0)) >= float(cfg["score_floor"])
    )

    # 1. budget exhausted (HARD)
    if _total_model_calls(iterations) >= int(cfg["model_call_budget"]):
        verdict["status"] = STATUS_BUDGET
        verdict["reason"] = "model-call budget exhausted; emitting best-so-far"
        verdict["residual_gaps"] = _residual_gaps(rubric, best_it)
        verdict["escalate_to_human"] = best_score < float(cfg["score_floor"])
        return (True, verdict)

    # 2. iteration cap (HARD) — but a cap that coincides with a clean pass is a pass
    if n_iters >= int(cfg["iteration_cap"]):
        if clean_pass:
            verdict["status"] = STATUS_RUBRIC_PASS
            verdict["reason"] = "rubric satisfied at the iteration cap"
        else:
            verdict["status"] = STATUS_CAPPED
            verdict["reason"] = "iteration cap reached; emitting best-so-far"
            verdict["escalate_to_human"] = best_score < float(cfg["score_floor"])
        verdict["residual_gaps"] = _residual_gaps(rubric, best_it)
        return (True, verdict)

    # 3. blockers prevent a rubric-pass on the latest iteration (no hard cap fired)
    if red_gates or new_blocker:
        verdict["status"] = None
        if red_gates:
            verdict["reason"] = f"blocked: red hard gate(s): {','.join(red_gates)}"
        else:
            verdict["reason"] = "blocked: new high/critical finding on latest iteration"
        return (False, verdict)

    # 4. convergence — rubric-pass
    if clean_pass and _plateaued():
        verdict["status"] = STATUS_RUBRIC_PASS
        verdict["reason"] = "all hard gates green, no new blockers, score >= floor, plateaued"
        verdict["residual_gaps"] = _residual_gaps(rubric, best_it)
        return (True, verdict)

    # 5. plateau below floor → escalate to human
    if _plateaued() and float(latest.get("score", 0.0)) < float(cfg["score_floor"]):
        verdict["status"] = STATUS_PLATEAUED
        verdict["reason"] = "plateaued below the score floor; escalating to human"
        verdict["residual_gaps"] = _residual_gaps(rubric, best_it)
        verdict["escalate_to_human"] = True
        return (True, verdict)

    # 6. keep refining
    verdict["reason"] = "not yet converged; continue refining"
    return (False, verdict)


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────
def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Deterministic convergence terminate() predicate.")
    ap.add_argument("--rubric", required=True, help="path to a rubric.schema.json document")
    ap.add_argument("--scorecard", required=True, help="path to a convergence-scorecard.schema.json document")
    ap.add_argument("--emit-verdict", action="store_true", help="print the verdict JSON to stdout")
    args = ap.parse_args(argv)

    try:
        rubric = _load(args.rubric)
        scorecard = _load(args.scorecard)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"converge: cannot read inputs: {exc}", file=sys.stderr)
        return 2

    iterations = scorecard.get("iterations", [])
    config = scorecard.get("config", {})

    try:
        should_stop, verdict = terminate(rubric, iterations, config)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"converge: contract error: {exc}", file=sys.stderr)
        return 2

    if args.emit_verdict:
        print(json.dumps(verdict, indent=2, sort_keys=True))

    return 0 if should_stop else 1


if __name__ == "__main__":
    sys.exit(main())
