#!/usr/bin/env python3
"""
test_rubric.py — unit tests for rubric.py (report-gold-standard-rubric).

Stdlib-only (unittest), Python 3.9-compatible. Covers the three acceptance
tests named in the FORGE plan §6a:

  1. a zero-diff input (already at the bar) exits at iteration 1, unchanged
     (ZERO content diffs) — the do-no-harm fixture.
  2. a rigged never-improving scorer triggers the plateau escape at 2
     consecutive no-improvement iterations.
  3. the Accurate floor fails closed to "unverified" (never "pass") when the
     receipt's V1 leg is in binding-correctness mode.

Plus supporting coverage for the monotonic ratchet, the per-node edit budget,
the cap stop, and the N=3 judged-median helper — the other load-bearing
pieces of the loop contract.

Run: python3 plugins/report-regeneration/skills/report-gold-standard-rubric/tests/test_rubric.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rubric  # noqa: E402


# ──────────────────────────────────────────────────────────────────────────
# Fixture builders
# ──────────────────────────────────────────────────────────────────────────
def _leg(name, verdict, label="proven", inference_independent=True, blocking=True):
    return {
        "leg": name,
        "verdict": verdict,
        "label": label,
        "inference_independent": inference_independent,
        "blocking": blocking,
    }


ALL_LEGS_PASS = [
    _leg("V1", "pass"),
    _leg("V2", "pass"),
    _leg("V3", "pass"),
    _leg("V4", "pass"),
    _leg("V5", "pass", label="judged"),
    _leg("V6", "pass"),
    _leg("period-coherence", "pass"),
]


def make_receipt(legs, overall_gate="PASS", **extra):
    receipt = {
        "receipt_version": "1.0.0",
        "run_id": "test-run",
        "format": "html",
        "generated_at": "2026-07-16T00:00:00Z",
        "ttl_seconds": 3600,
        "env_fingerprint": "deadbeef",
        "overall_gate": overall_gate,
        "legs": legs,
    }
    receipt.update(extra)
    return receipt


def clean_scores():
    """A scores map where every dimension is already at the bar — the
    do-no-harm zero-diff fixture's starting point."""
    receipt = make_receipt(ALL_LEGS_PASS)
    return rubric.score_all(
        receipt,
        sign_consistency_pass=True,
        a11y_axe_pass=True,
        a11y_verapdf_pass=True,
        format_consistency_pass=True,
        dynamic_judged=0.95,
        inclusive_judged=0.95,
        polished_judged=0.95,
    )


def non_passing_scores(dynamic_judged=0.40):
    """A scores map where Dynamic has not yet reached the bar (the rest are
    green) — used to drive the plateau/cap fixtures without ever spuriously
    satisfying PASS."""
    receipt = make_receipt(ALL_LEGS_PASS)
    return rubric.score_all(
        receipt,
        sign_consistency_pass=True,
        a11y_axe_pass=True,
        a11y_verapdf_pass=True,
        format_consistency_pass=True,
        dynamic_judged=dynamic_judged,
        inclusive_judged=0.95,
        polished_judged=0.95,
    )


# ──────────────────────────────────────────────────────────────────────────
# 1. Do-no-harm zero-diff fixture
# ──────────────────────────────────────────────────────────────────────────
class TestZeroDiffFixture(unittest.TestCase):
    def test_already_at_bar_exits_iteration_1_with_zero_diffs(self):
        iteration_1 = {
            "index": 1,
            "scores": clean_scores(),
            "content_diff_count": 0,
            "improved": None,
            "target_dim": None,
        }
        should_stop, verdict = rubric.terminate([iteration_1])

        self.assertTrue(should_stop, "an already-at-bar input must stop immediately")
        self.assertEqual(verdict["status"], rubric.STATUS_PASS)
        self.assertEqual(verdict["iterations"], 1, "must exit at iteration 1, not later")
        self.assertEqual(
            iteration_1["content_diff_count"], 0,
            "the do-no-harm invariant: an input already at the bar must produce "
            "ZERO content diffs",
        )
        self.assertFalse(verdict["escalate_to_human"])

    def test_passes_bar_helper_agrees(self):
        self.assertTrue(rubric.passes_bar(clean_scores()))


# ──────────────────────────────────────────────────────────────────────────
# 2. Plateau escape at 2 consecutive no-improvement iterations
# ──────────────────────────────────────────────────────────────────────────
class TestPlateauEscape(unittest.TestCase):
    def test_rigged_never_improving_scorer_triggers_plateau_at_2(self):
        # A "rigged never-improving scorer": two consecutive iterations, each
        # explicitly marked as having made no accepted (ratchet-passing)
        # revision, and never actually at the bar (Dynamic stuck below 0.85).
        stuck_scores = non_passing_scores(dynamic_judged=0.40)
        iterations = [
            {
                "index": 1,
                "scores": stuck_scores,
                "content_diff_count": 12,
                "improved": False,
                "target_dim": "dynamic",
            },
            {
                "index": 2,
                "scores": stuck_scores,
                "content_diff_count": 12,
                "improved": False,
                "target_dim": "dynamic",
            },
        ]

        should_stop, verdict = rubric.terminate(iterations)

        self.assertTrue(should_stop)
        self.assertEqual(verdict["status"], rubric.STATUS_PLATEAU)
        self.assertEqual(verdict["iterations"], 2, "the plateau escape fires at 2")
        self.assertTrue(verdict["escalate_to_human"])

    def test_single_no_improvement_iteration_does_not_yet_plateau(self):
        stuck_scores = non_passing_scores(dynamic_judged=0.40)
        iterations = [
            {"index": 1, "scores": stuck_scores, "content_diff_count": 5,
             "improved": False, "target_dim": "dynamic"},
        ]
        should_stop, verdict = rubric.terminate(iterations)
        self.assertFalse(should_stop)
        self.assertIsNone(verdict["status"])

    def test_an_improving_iteration_between_resets_the_plateau_window(self):
        stuck_scores = non_passing_scores(dynamic_judged=0.40)
        iterations = [
            {"index": 1, "scores": stuck_scores, "content_diff_count": 5,
             "improved": False, "target_dim": "dynamic"},
            {"index": 2, "scores": stuck_scores, "content_diff_count": 4,
             "improved": True, "target_dim": "dynamic"},
            {"index": 3, "scores": stuck_scores, "content_diff_count": 3,
             "improved": False, "target_dim": "dynamic"},
        ]
        # Only the LAST iteration is a no-improvement one within the last-2
        # window (iteration 2 improved), so plateau must NOT fire yet.
        should_stop, verdict = rubric.terminate(iterations)
        self.assertFalse(should_stop)
        self.assertIsNone(verdict["status"])


# ──────────────────────────────────────────────────────────────────────────
# 3. The Accurate hard floor fails closed to "unverified"
# ──────────────────────────────────────────────────────────────────────────
class TestAccurateHardFloor(unittest.TestCase):
    def test_v1_binding_correctness_mode_fails_closed_to_unverified(self):
        legs = [
            _leg("V1", "PARTIAL"),  # binding-correctness mode: no live data route
            _leg("V2", "pass"),
            _leg("V3", "pass"),
            _leg("V4", "pass"),
            _leg("V5", "pass", label="judged"),
            _leg("V6", "pass"),
            _leg("period-coherence", "pass"),
        ]
        receipt = make_receipt(legs, overall_gate="PARTIAL")

        result = rubric.score_accurate(receipt)

        self.assertEqual(result["status"], "unverified")
        self.assertNotEqual(result["status"], "pass", "V1 in binding-correctness "
                             "mode must NEVER read as a pass")
        self.assertFalse(result["judged_stub"], "Accurate carries no judged residue")

    def test_v1_binding_correctness_mode_via_score_all_and_terminate(self):
        legs = [
            _leg("V1", "PARTIAL"),
            _leg("V2", "pass"), _leg("V3", "pass"), _leg("V4", "pass"),
            _leg("V5", "pass", label="judged"), _leg("V6", "pass"),
            _leg("period-coherence", "pass"),
        ]
        receipt = make_receipt(legs, overall_gate="PARTIAL")
        scores = rubric.score_all(
            receipt, sign_consistency_pass=True, a11y_axe_pass=True,
            a11y_verapdf_pass=True, format_consistency_pass=True,
            dynamic_judged=0.99, inclusive_judged=0.99, polished_judged=0.99,
        )
        self.assertFalse(rubric.passes_bar(scores),
                          "Accurate=unverified must block an overall PASS even "
                          "when every other dimension is fully judged and green")

        # And even after cap iterations, terminate() must never emit PASS.
        iterations = [
            {"index": i, "scores": scores, "content_diff_count": 0,
             "improved": (i > 1), "target_dim": "accurate"}
            for i in range(1, rubric.ITERATION_CAP + 1)
        ]
        should_stop, verdict = rubric.terminate(iterations)
        self.assertTrue(should_stop)
        self.assertEqual(verdict["status"], rubric.STATUS_CAP)
        self.assertNotEqual(verdict["status"], rubric.STATUS_PASS)

    def test_ordinary_v1_failure_is_fail_not_unverified(self):
        legs = [
            _leg("V1", "fail"),
            _leg("V2", "pass"), _leg("V3", "pass"), _leg("V4", "pass"),
            _leg("V5", "pass", label="judged"), _leg("V6", "pass"),
            _leg("period-coherence", "pass"),
        ]
        receipt = make_receipt(legs, overall_gate="FAIL")
        result = rubric.score_accurate(receipt)
        self.assertEqual(result["status"], "fail")

    def test_a_proven_other_leg_failure_outranks_the_v1_degrade(self):
        # V1 is degraded AND V4 (taint egress) genuinely fails — the proven
        # leak must report "fail", not the softer "unverified".
        legs = [
            _leg("V1", "PARTIAL"),
            _leg("V2", "pass"), _leg("V3", "pass"),
            _leg("V4", "fail"),
            _leg("V5", "pass", label="judged"), _leg("V6", "pass"),
            _leg("period-coherence", "pass"),
        ]
        receipt = make_receipt(legs, overall_gate="FAIL")
        result = rubric.score_accurate(receipt)
        self.assertEqual(result["status"], "fail")

    def test_no_legs_present_is_unverified(self):
        receipt = make_receipt([], overall_gate="FAIL")
        result = rubric.score_accurate(receipt)
        self.assertEqual(result["status"], "unverified")

    def test_clean_receipt_passes(self):
        receipt = make_receipt(ALL_LEGS_PASS, overall_gate="PASS")
        result = rubric.score_accurate(receipt)
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["anchor_pass"])


# ──────────────────────────────────────────────────────────────────────────
# Supporting coverage — monotonic ratchet, edit budget, cap, judged median
# ──────────────────────────────────────────────────────────────────────────
class TestMonotonicRatchet(unittest.TestCase):
    def test_target_improves_others_hold_is_accepted(self):
        prev = non_passing_scores(dynamic_judged=0.40)
        new = non_passing_scores(dynamic_judged=0.60)
        self.assertTrue(rubric.accept_revision(prev, new, "dynamic"))

    def test_target_does_not_improve_is_reverted(self):
        prev = non_passing_scores(dynamic_judged=0.40)
        new = non_passing_scores(dynamic_judged=0.40)
        self.assertFalse(rubric.accept_revision(prev, new, "dynamic"))

    def test_target_improves_but_another_dimension_drops_is_reverted(self):
        prev = non_passing_scores(dynamic_judged=0.40)
        receipt = make_receipt(ALL_LEGS_PASS)
        new = rubric.score_all(
            receipt, sign_consistency_pass=True, a11y_axe_pass=True,
            a11y_verapdf_pass=True, format_consistency_pass=True,
            dynamic_judged=0.60, inclusive_judged=0.50,  # dropped from 0.95
            polished_judged=0.95,
        )
        self.assertFalse(rubric.accept_revision(prev, new, "dynamic"))

    def test_accurate_regression_from_pass_is_never_accepted_even_off_target(self):
        prev = clean_scores()  # accurate == pass
        legs_degraded = [
            _leg("V1", "PARTIAL"),
            _leg("V2", "pass"), _leg("V3", "pass"), _leg("V4", "pass"),
            _leg("V5", "pass", label="judged"), _leg("V6", "pass"),
            _leg("period-coherence", "pass"),
        ]
        receipt = make_receipt(legs_degraded, overall_gate="PARTIAL")
        new = rubric.score_all(
            receipt, sign_consistency_pass=True, a11y_axe_pass=True,
            a11y_verapdf_pass=True, format_consistency_pass=True,
            dynamic_judged=0.99, inclusive_judged=0.99, polished_judged=0.99,
        )
        # Even though the revision TARGETED "polished" (not accurate) and
        # every judged dim improved, Accurate regressing from pass must veto.
        self.assertFalse(rubric.accept_revision(prev, new, "polished"))


class TestNodeEditBudget(unittest.TestCase):
    def test_under_budget_not_exceeded(self):
        self.assertFalse(rubric.node_edit_budget_exceeded({"n1": 1}, "n1"))

    def test_at_budget_is_exceeded(self):
        self.assertTrue(rubric.node_edit_budget_exceeded({"n1": 2}, "n1"))

    def test_absent_node_defaults_to_zero(self):
        self.assertFalse(rubric.node_edit_budget_exceeded({}, "n1"))


class TestCapStop(unittest.TestCase):
    def test_cap_fires_at_6_when_never_passing(self):
        stuck_scores = non_passing_scores(dynamic_judged=0.40)
        iterations = [
            {"index": i, "scores": stuck_scores, "content_diff_count": 1,
             "improved": True, "target_dim": "dynamic"}
            for i in range(1, rubric.ITERATION_CAP + 1)
        ]
        should_stop, verdict = rubric.terminate(iterations)
        self.assertTrue(should_stop)
        self.assertEqual(verdict["status"], rubric.STATUS_CAP)
        self.assertTrue(verdict["escalate_to_human"])

    def test_cap_reached_with_a_clean_pass_reports_pass_not_cap(self):
        good_scores = clean_scores()
        iterations = [
            {"index": i, "scores": good_scores, "content_diff_count": 0,
             "improved": True, "target_dim": None}
            for i in range(1, rubric.ITERATION_CAP + 1)
        ]
        should_stop, verdict = rubric.terminate(iterations)
        self.assertTrue(should_stop)
        self.assertEqual(verdict["status"], rubric.STATUS_PASS)


class TestJudgedMedian(unittest.TestCase):
    def test_median_of_three(self):
        self.assertAlmostEqual(rubric.judged_median([0.7, 0.9, 0.8]), 0.8)

    def test_insufficient_sample_flagged(self):
        self.assertTrue(rubric.judged_sample_insufficient([0.7, 0.9]))
        self.assertFalse(rubric.judged_sample_insufficient([0.7, 0.9, 0.8]))

    def test_empty_is_none(self):
        self.assertIsNone(rubric.judged_median([]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
