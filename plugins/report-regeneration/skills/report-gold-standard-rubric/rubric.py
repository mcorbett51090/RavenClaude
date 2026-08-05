#!/usr/bin/env python3
"""
report-gold-standard-rubric — rubric.py (Phase 5, §6a of the FORGE plan).

Two pure, model-free responsibilities, and nothing else:

  1. score a fidelity-harness receipt (report-fidelity-harness's
     `fidelity-receipt.schema.json` shape) against the four rubric dimensions
     — Accurate / Dynamic / Inclusive / Polished — returning a per-dimension
     verdict plus whether that dimension still carries an unscored JUDGED
     residue (a "judged-stub").
  2. implement the loop's stop-decision, `terminate()`: PASS, or plateau
     (2 consecutive no-improvement iterations), or cap (6 iterations) —
     whichever fires first — plus the monotonic-ratchet accept/revert rule
     and the per-node edit budget.

NO model call. NO network. NO file write. Every function here is a pure
function of its arguments — the same discipline `refine-to-rubric/scripts/
converge.py` uses for the domain-neutral Convergence Engine, applied to this
plugin's own four-dimension rubric (this module does NOT import or wrap
converge.py — the two rubrics are shaped differently: converge.py grades one
weighted score, this module grades four independently-gated dimensions with
one of them a HARD FLOOR that is never traded for gains elsewhere).

The four dimensions (plan §6a):

  Accurate   — HARD FLOOR. Never iterated, never traded. Deterministic
               anchor = the WHOLE fidelity harness (V1-V6 + period-coherence).
               No judged residue. Fails CLOSED to "unverified" (never "pass")
               when V1 is in binding-correctness mode (RT1-F12) — i.e. leg V1
               has verdict "PARTIAL" per fidelity-receipt.schema.json's own
               description of that value.
  Dynamic    — anchor: V1 value-accuracy + a sign-consistency check (does the
               narrative say "up" iff delta>0). Judged residue: narrative
               fluency.
  Inclusive  — anchor: axe-core (HTML) / veraPDF (Office PDF) a11y floor.
               Judged residue: alt-text quality, plain-language.
  Polished   — anchor: V5 render referee (both formats) + a number/date
               format-consistency scanner. Judged residue: typographic taste,
               visual hierarchy.

The three supplementary signals (sign-consistency, the a11y gates, the
format-consistency scanner) are NOT part of fidelity-receipt.schema.json —
that schema only carries the six V-legs + period-coherence. They are passed
in as explicit optional keyword arguments so a bare fidelity-receipt with
none of them still scores Accurate correctly, and the other three dimensions
degrade honestly (anchor_pass stays False, never a silent pass) when a
signal is absent rather than assumed.

Path-guarded: this module opens no file except via its own CLI entry point,
and only the path given on the command line.
"""
from __future__ import annotations

import argparse
import json
import sys

SCHEMA_VERSION = "1.0.0"

DIMENSIONS = ("accurate", "dynamic", "inclusive", "polished")

# The fidelity-receipt leg verdicts that are NEVER a pass (per
# fidelity-receipt.schema.json's own `legReceipt.verdict` enum + its
# top-level allOf: overall_gate PASS forbids every one of these).
_BAD_VERDICTS = ("fail", "not_captured", "PARTIAL", "PROBE_ERROR", "disabled")

# Default numeric bar a judged dimension's N=3 median score must clear to
# count as "pass". Not a number the FORGE plan pins explicitly — a tunable
# default the caller may override; documented here rather than presented as
# an authoritative plan figure.
DEFAULT_BAR = 0.85

# N=3 median for judged dimensions (binding — RT2-F6, noisy-judge robustness).
JUDGED_SAMPLE_N = 3

# Loop mechanics (binding — TB-4a / RT2-F6).
ITERATION_CAP = 6
PLATEAU_PATIENCE = 2
NODE_EDIT_BUDGET = 2

# Fixed, bounded stop-verdict vocabulary — the loop never claims "perfect".
STATUS_PASS = "PASS"
STATUS_PLATEAU = "plateau"
STATUS_CAP = "cap"


# ──────────────────────────────────────────────────────────────────────────
# Fidelity-receipt readers
# ──────────────────────────────────────────────────────────────────────────
def _leg(receipt, name):
    """The single leg record named `name` (e.g. "V1"), or None if absent."""
    for leg in receipt.get("legs", []) or []:
        if leg.get("leg") == name:
            return leg
    return None


def _result(dimension, status, anchor_pass, judged_score, judged_stub, bar, reason):
    return {
        "dimension": dimension,
        "status": status,
        "anchor_pass": anchor_pass,
        "judged_score": judged_score,
        "judged_stub": judged_stub,
        "bar": bar,
        "reason": reason,
    }


# ──────────────────────────────────────────────────────────────────────────
# Accurate — the HARD FLOOR (no judged residue, never traded)
# ──────────────────────────────────────────────────────────────────────────
def score_accurate(receipt):
    """Accurate: deterministic anchor = the WHOLE harness. `status` is one of
    "pass" | "fail" | "unverified" — NEVER a partial-credit number, because the
    hard floor is binary by design. `judged_stub` is always False: this
    dimension carries no judged residue at all (the rubric table's own line
    reads "Judged residue: none").

    Precedence (deliberately in this order — see the docstring on `_BAD_VERDICTS`
    below for why a genuine OTHER-leg failure outranks the V1-degrade case):

      1. no legs at all                       -> "unverified" (nothing was checked)
      2. any OTHER *BLOCKING* leg is non-pass  -> "fail" (a proven failure elsewhere
                                                   is a stronger, more definite
                                                   result than "we couldn't verify
                                                   accuracy" and must not be
                                                   downgraded to the softer label).
                                                   NON-blocking legs — V5 render
                                                   referee — are EXCLUDED here (P2 #7):
                                                   V5 is the Polished anchor, never
                                                   Accurate's, and in the stdlib default
                                                   env V5 is `not_captured`, so gating
                                                   Accurate on it would pin Accurate to
                                                   `fail` forever and the loop could
                                                   never reach PASS.
      3. V1 verdict == "PARTIAL"                -> "unverified" (RT1-F12: V1 is in
                                                   binding-correctness mode — no
                                                   live data route — and Accurate
                                                   fails closed, never PASS)
      4. V1 verdict is otherwise non-pass       -> "fail" (a genuine V1 failure,
                                                   not a degrade)
      5. V1 pass + every blocking leg pass      -> "pass" (Accurate does NOT require
                                                   overall_gate == PASS: a legitimately
                                                   `not_captured` V5 makes overall_gate
                                                   PARTIAL, which must not veto Accurate)
      6. V1 absent                              -> "unverified" (value accuracy unproven)
    """
    legs = receipt.get("legs", []) or []
    if not legs:
        return _result("accurate", "unverified", False, None, False, None,
                        "no fidelity legs present — nothing was verified")

    v1 = _leg(receipt, "V1")

    # Only BLOCKING legs constitute the Accurate hard floor. V5 (the non-blocking render referee)
    # is the Polished dimension's anchor, not Accurate's — and it is `not_captured` in the stdlib
    # default (renderer-absent) env — so it is excluded here; otherwise a lone V5 not_captured would
    # pin Accurate to `fail` and terminate() could never emit STATUS_PASS (P2 #7).
    others_bad = [leg for leg in legs
                  if leg.get("leg") != "V1" and leg.get("blocking", True)
                  and leg.get("verdict") in _BAD_VERDICTS]
    if others_bad:
        names = ",".join(sorted(leg.get("leg", "?") for leg in others_bad))
        return _result("accurate", "fail", False, None, False, None,
                        f"non-passing blocking leg(s): {names}")

    if v1 is not None and v1.get("verdict") == "PARTIAL":
        return _result("accurate", "unverified", False, None, False, None,
                        "V1 is in binding-correctness mode (no live data route) "
                        "— Accurate fails closed to 'unverified', never PASS (RT1-F12)")

    if v1 is not None and v1.get("verdict") in _BAD_VERDICTS:
        return _result("accurate", "fail", False, None, False, None,
                        f"V1 verdict is {v1.get('verdict')!r}")

    if v1 is not None and v1.get("verdict") == "pass":
        return _result("accurate", "pass", True, None, False, None,
                        "V1 value-accuracy passed and every blocking fidelity leg "
                        "(V1-V4, V6, period-coherence) passed (V5 render referee is "
                        "non-blocking and does not gate the Accurate floor)")

    return _result("accurate", "unverified", False, None, False, None,
                   "V1 (value accuracy) is absent from the receipt — accuracy unproven")


# ──────────────────────────────────────────────────────────────────────────
# Dynamic / Inclusive / Polished — deterministic anchor + judged residue
# ──────────────────────────────────────────────────────────────────────────
def _finalize(dimension, anchor_pass, judged_score, bar, reason):
    """Shared verdict logic for the three anchor+judged dimensions.

    status is:
      "fail"  if the deterministic anchor itself is red (a judged score can
              never rescue a red anchor — the anchor is a NECESSARY condition)
      None    if the anchor is green but no judged score has been supplied yet
              (a "judged-stub": this dimension cannot be scored pass/fail until
              the N=3 judge runs — never silently treated as a pass)
      "pass"  if the anchor is green AND judged_score >= bar
      "fail"  if the anchor is green AND judged_score < bar
    """
    judged_stub = judged_score is None
    if not anchor_pass:
        status = "fail"
    elif judged_stub:
        status = None
    elif judged_score >= bar:
        status = "pass"
    else:
        status = "fail"
    return _result(dimension, status, anchor_pass, judged_score, judged_stub, bar, reason)


def score_dynamic(receipt, sign_consistency_pass=None, judged_score=None, bar=DEFAULT_BAR):
    """Dynamic: anchor = V1 leg pass AND (if supplied) the sign-consistency
    check (does the variance narrative say "up" iff delta>0). Judged residue:
    narrative fluency."""
    v1 = _leg(receipt, "V1")
    anchor_pass = bool(v1 is not None and v1.get("verdict") == "pass")
    if sign_consistency_pass is not None:
        anchor_pass = anchor_pass and bool(sign_consistency_pass)
    return _finalize("dynamic", anchor_pass, judged_score, bar,
                      "V1 value-accuracy" +
                      ("" if sign_consistency_pass is None else
                       " + sign-consistency (narrative direction matches data direction)"))


def score_inclusive(receipt, a11y_axe_pass=None, a11y_verapdf_pass=None,
                     judged_score=None, bar=DEFAULT_BAR):
    """Inclusive: anchor = the per-format a11y gate(s) supplied (axe-core for
    HTML, veraPDF for the PDF/Office path). At least one signal must be
    supplied AND green; an absent signal never counts as a silent pass.
    Judged residue: alt-text quality, plain-language."""
    signals = [s for s in (a11y_axe_pass, a11y_verapdf_pass) if s is not None]
    anchor_pass = bool(signals) and all(bool(s) for s in signals)
    return _finalize("inclusive", anchor_pass, judged_score, bar,
                      "axe-core (HTML) / veraPDF (Office PDF) a11y floor")


def score_polished(receipt, format_consistency_pass=None, judged_score=None, bar=DEFAULT_BAR):
    """Polished: anchor = V5 render-referee leg pass AND (if supplied) the
    number/date format-consistency scanner. Judged residue: typographic
    taste, visual hierarchy."""
    v5 = _leg(receipt, "V5")
    anchor_pass = bool(v5 is not None and v5.get("verdict") == "pass")
    if format_consistency_pass is not None:
        anchor_pass = anchor_pass and bool(format_consistency_pass)
    return _finalize("polished", anchor_pass, judged_score, bar,
                      "V5 render referee (both formats)" +
                      ("" if format_consistency_pass is None else
                       " + number/date format-consistency scanner"))


def score_all(receipt, sign_consistency_pass=None,
              a11y_axe_pass=None, a11y_verapdf_pass=None,
              format_consistency_pass=None,
              dynamic_judged=None, inclusive_judged=None, polished_judged=None,
              bar=DEFAULT_BAR):
    """Score all four dimensions against one receipt. Returns
    {dimension: result-dict} for every dimension in DIMENSIONS."""
    return {
        "accurate": score_accurate(receipt),
        "dynamic": score_dynamic(receipt, sign_consistency_pass=sign_consistency_pass,
                                  judged_score=dynamic_judged, bar=bar),
        "inclusive": score_inclusive(receipt, a11y_axe_pass=a11y_axe_pass,
                                      a11y_verapdf_pass=a11y_verapdf_pass,
                                      judged_score=inclusive_judged, bar=bar),
        "polished": score_polished(receipt, format_consistency_pass=format_consistency_pass,
                                    judged_score=polished_judged, bar=bar),
    }


def passes_bar(scores):
    """True iff every dimension's `status` is exactly "pass" — the PASS
    condition for `terminate()`. `scores` is a {dimension: result-dict} map
    (score_all's return shape, or an equivalent iteration record)."""
    return all(scores.get(dim, {}).get("status") == "pass" for dim in DIMENSIONS)


# ──────────────────────────────────────────────────────────────────────────
# N=3 median for judged dimensions (noisy-judge robustness, RT2-F6)
# ──────────────────────────────────────────────────────────────────────────
def judged_median(scores):
    """Median of a list of raw judge scores in [0,1]. `JUDGED_SAMPLE_N` (3) is
    the sanctioned sample width; use `judged_sample_insufficient()` to check
    that before trusting the result — this function itself computes a median
    for any non-empty list so a caller isn't blocked from inspecting partial
    data, but a caller MUST NOT treat a < 3-sample median as a scored verdict."""
    if not scores:
        return None
    ordered = sorted(float(s) for s in scores)
    n = len(ordered)
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def judged_sample_insufficient(scores, required=JUDGED_SAMPLE_N):
    """True iff fewer than `required` judge samples were supplied — the
    noisy-judge-robustness rule has teeth only if callers check this before
    trusting `judged_median()`."""
    return len(scores or []) < required


# ──────────────────────────────────────────────────────────────────────────
# Monotonic ratchet + per-node edit budget (binding — RT2-F6)
# ──────────────────────────────────────────────────────────────────────────
def dimension_score(result):
    """Collapse one dimension's result dict to a single comparable float in
    [0,1], for ratchet comparisons only (never used to decide pass/fail on its
    own — `status` is the source of truth for that).

    Accurate is categorical and collapses to 1.0 ONLY on a clean "pass" —
    both "unverified" and "fail" collapse to 0.0 (no partial credit; the hard
    floor is binary by design). Dynamic/Inclusive/Polished collapse to 0.0
    whenever their deterministic anchor is red (the anchor is a necessary
    condition regardless of any judged score), else to the judged score (or
    1.0 when the dimension carries no judged residue left to score, i.e. the
    anchor alone fully determines it)."""
    if result["dimension"] == "accurate":
        return 1.0 if result["status"] == "pass" else 0.0
    if not result.get("anchor_pass", False):
        return 0.0
    judged = result.get("judged_score")
    return 1.0 if judged is None else float(judged)


def accept_revision(prev_scores, new_scores, target_dim):
    """Monotonic ratchet (binding — RT2-F6): accept a revision only if its
    TARGET dimension improves AND no OTHER dimension drops; otherwise revert.

    Accurate is additionally NEVER allowed to regress from "pass" — this
    check fires regardless of which dimension the revision targeted, because
    Accurate is the hard floor and is "never traded" for gains elsewhere.

    `prev_scores` / `new_scores` are {dimension: result-dict} maps (score_all's
    shape) for all four dimensions. Returns True (accept) or False (revert).
    """
    if target_dim not in DIMENSIONS:
        raise ValueError(f"unknown target dimension: {target_dim!r}")

    prev_accurate = prev_scores.get("accurate", {}).get("status")
    new_accurate = new_scores.get("accurate", {}).get("status")
    if prev_accurate == "pass" and new_accurate != "pass":
        return False

    for dim in DIMENSIONS:
        prev_v = dimension_score(prev_scores[dim])
        new_v = dimension_score(new_scores[dim])
        if dim == target_dim:
            if new_v <= prev_v:
                return False
        elif new_v < prev_v:
            return False
    return True


def node_edit_budget_exceeded(edit_counts, node_id, budget=NODE_EDIT_BUDGET):
    """Per-node edit budget (binding): a node revised `budget` times (default
    2) without reaching the bar is FROZEN and flagged to the human reviewer —
    that residue is theirs, per the draft+QA model. `edit_counts` maps
    node_id -> number of revision attempts already made on that node."""
    return edit_counts.get(node_id, 0) >= budget


# ──────────────────────────────────────────────────────────────────────────
# The deterministic stop predicate — PASS / plateau / cap
# ──────────────────────────────────────────────────────────────────────────
def terminate(iterations, cap=ITERATION_CAP, plateau_patience=PLATEAU_PATIENCE):
    """The model-free loop stop-decision (binding — TB-4a).

    `iterations` is a list of iteration records, each shaped:
        {
          "index": int,
          "scores": {dimension: result-dict, ...},   # score_all()'s shape
          "content_diff_count": int,                  # bytes/nodes changed
                                                        # vs the prior iteration
          "improved": bool | None,   # did THIS iteration's revision survive
                                      # the monotonic ratchet (accept_revision)?
                                      # None only for a baseline iteration that
                                      # made no revision attempt yet.
          "target_dim": str | None,
        }

    Stop condition — PASS, OR plateau (2 consecutive no-improvement
    iterations), OR cap (6 iterations), whichever fires first:

      1. PASS takes precedence at any iteration count (a cap or plateau that
         coincides with a clean pass is still reported as PASS — success is
         never downgraded to a process label). PASS requires every dimension's
         `status == "pass"` — Accurate included, so a permanently-unverified
         Accurate (e.g. no live data route) can never fake a PASS no matter
         how long the loop runs.
      2. cap: len(iterations) >= cap.
      3. plateau: the most recent `plateau_patience` iterations ALL have
         "improved" == False (no accepted revision on any of them).
      4. otherwise: keep iterating.

    Returns (should_stop: bool, verdict: dict) — verdict["status"] is one of
    STATUS_PASS / STATUS_PLATEAU / STATUS_CAP / None (None == keep iterating).
    plateau and cap set escalate_to_human = True (the residual goes to
    `architect`, per the plan; genuine human-only residue is flagged, never
    faked as passing).
    """
    if not iterations:
        return False, {"status": None, "reason": "no iterations yet", "iterations": 0}

    n = len(iterations)
    latest = iterations[-1]

    if passes_bar(latest.get("scores", {})):
        return True, {
            "status": STATUS_PASS,
            "reason": "all four dimensions at bar (Accurate hard floor satisfied)",
            "iterations": n,
            "content_diff_count": latest.get("content_diff_count"),
            "escalate_to_human": False,
        }

    if n >= cap:
        return True, {
            "status": STATUS_CAP,
            "reason": f"iteration cap ({cap}) reached without satisfying all four dimensions",
            "iterations": n,
            "escalate_to_human": True,
        }

    if n >= plateau_patience:
        window = iterations[-plateau_patience:]
        if all(it.get("improved", True) is False for it in window):
            return True, {
                "status": STATUS_PLATEAU,
                "reason": f"{plateau_patience} consecutive iterations with no monotonic improvement",
                "iterations": n,
                "escalate_to_human": True,
            }

    return False, {"status": None, "reason": "continue iterating", "iterations": n}


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────
def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _flag(v):
    return None if v is None else (v == "true")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Score a fidelity-receipt against the gold-standard rubric, "
                    "or run the loop's terminate() predicate over an iteration history."
    )
    ap.add_argument("--receipt", help="path to a fidelity-receipt JSON to score")
    ap.add_argument("--iterations", help="path to a JSON list of iteration records "
                                          "to run terminate() over")
    ap.add_argument("--sign-consistency", choices=["true", "false"], default=None)
    ap.add_argument("--a11y-axe", choices=["true", "false"], default=None)
    ap.add_argument("--a11y-verapdf", choices=["true", "false"], default=None)
    ap.add_argument("--format-consistency", choices=["true", "false"], default=None)
    ap.add_argument("--dynamic-judged", type=float, default=None)
    ap.add_argument("--inclusive-judged", type=float, default=None)
    ap.add_argument("--polished-judged", type=float, default=None)
    ap.add_argument("--bar", type=float, default=DEFAULT_BAR)
    ap.add_argument("--emit-verdict", action="store_true",
                     help="print the scored/verdict JSON to stdout")
    args = ap.parse_args(argv)

    if args.iterations:
        try:
            iterations = _load(args.iterations)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"rubric: cannot read iterations: {exc}", file=sys.stderr)
            return 2
        try:
            should_stop, verdict = terminate(iterations)
        except (KeyError, TypeError, ValueError) as exc:
            print(f"rubric: contract error: {exc}", file=sys.stderr)
            return 2
        if args.emit_verdict:
            print(json.dumps(verdict, indent=2, sort_keys=True))
        return 0 if should_stop else 1

    if not args.receipt:
        print("rubric: one of --receipt or --iterations is required", file=sys.stderr)
        return 2

    try:
        receipt = _load(args.receipt)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"rubric: cannot read receipt: {exc}", file=sys.stderr)
        return 2

    scored = score_all(
        receipt,
        sign_consistency_pass=_flag(args.sign_consistency),
        a11y_axe_pass=_flag(args.a11y_axe),
        a11y_verapdf_pass=_flag(args.a11y_verapdf),
        format_consistency_pass=_flag(args.format_consistency),
        dynamic_judged=args.dynamic_judged,
        inclusive_judged=args.inclusive_judged,
        polished_judged=args.polished_judged,
        bar=args.bar,
    )
    if args.emit_verdict:
        print(json.dumps(scored, indent=2, sort_keys=True))
    return 0 if scored["accurate"]["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
