#!/usr/bin/env python3
"""
Unit + CLI tests for report-qa-gate/qa_gate.py.

Run from repo root:
    python3 -m pytest plugins/report-regeneration/skills/report-qa-gate/tests/test_qa_gate.py
or:
    python3 plugins/report-regeneration/skills/report-qa-gate/tests/test_qa_gate.py

Required coverage (per the build spec):
    - a V4-fail receipt                 -> computed_gate == FAIL
    - a not_captured-V5 receipt         -> computed_gate == PARTIAL (never PASS)
    - a clean receipt                   -> computed_gate == PASS
    - manual-residue checklist non-empty in the PARTIAL case (and, per the module's
      own stronger invariant, in every case -- exercised below too)
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "qa_gate.py"


def _load_module():
    """Import qa_gate.py by path (mirrors tests/fixtures/test_security_deny_floor.py's
    importlib convention -- robust regardless of how the test runner's sys.path is
    set up)."""
    spec = importlib.util.spec_from_file_location("qa_gate", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["qa_gate"] = mod
    spec.loader.exec_module(mod)
    return mod


QG = _load_module()
REPO_ROOT = QG._repo_root()

# blocking flag per leg, per fidelity-receipt.schema.json's leg description
# (V1-V4, V6, period-coherence are blocking; V5 is proven-where-deterministic /
# judged-for-polish, i.e. non-blocking).
_BLOCKING = {
    "V1": True, "V2": True, "V3": True, "V4": True,
    "V5": False, "V6": True, "period-coherence": True,
}


def _leg(leg_id, verdict="pass", label="proven", inference_independent=True, evidence=None):
    d = {
        "leg": leg_id,
        "verdict": verdict,
        "label": label,
        "inference_independent": inference_independent,
        "blocking": _BLOCKING[leg_id],
    }
    if evidence is not None:
        d["evidence"] = evidence
    return d


def _clean_legs():
    return [_leg(leg_id) for leg_id in QG.EXPECTED_LEGS]


def _receipt(legs, overall_gate="PASS", manual_residue=None):
    r = {
        "receipt_version": "1.0.0",
        "run_id": "run-test-0001",
        "format": "html",
        "generated_at": "2026-07-16T00:00:00Z",
        "ttl_seconds": 3600,
        "env_fingerprint": "sha256:deadbeef",
        "overall_gate": overall_gate,
        "legs": legs,
    }
    if manual_residue is not None:
        r["manual_residue"] = manual_residue
    return r


def _set_leg_verdict(legs, leg_id, verdict, evidence=None):
    out = copy.deepcopy(legs)
    for leg in out:
        if leg["leg"] == leg_id:
            leg["verdict"] = verdict
            if evidence is not None:
                leg["evidence"] = evidence
    return out


class TestRequiredCases(unittest.TestCase):
    """The four cases the build spec explicitly requires."""

    def test_v4_fail_receipt_is_FAIL(self):
        legs = _set_leg_verdict(
            _clean_legs(), "V4", "fail",
            evidence="old company name 'Ridgeline Fabricators Inc.' found at byte offset 4021",
        )
        receipt = _receipt(legs, overall_gate="FAIL")
        result = QG.build_result(receipt)
        self.assertEqual(result["computed_gate"], "FAIL")
        self.assertIn("V4", result["blocking_leg_failures"])
        self.assertFalse(result["review_ready"])

    def test_not_captured_v5_receipt_is_PARTIAL_never_PASS(self):
        legs = _set_leg_verdict(_clean_legs(), "V5", "not_captured")
        receipt = _receipt(legs, overall_gate="PARTIAL")
        result = QG.build_result(receipt)
        self.assertEqual(result["computed_gate"], "PARTIAL")
        self.assertNotEqual(result["computed_gate"], "PASS")
        self.assertTrue(any(d["leg"] == "V5" for d in result["degraded_legs"]))

    def test_clean_receipt_is_PASS(self):
        receipt = _receipt(_clean_legs(), overall_gate="PASS")
        result = QG.build_result(receipt)
        self.assertEqual(result["computed_gate"], "PASS")
        self.assertTrue(result["review_ready"])
        self.assertEqual(result["blocking_leg_failures"], [])
        self.assertEqual(result["degraded_legs"], [])
        self.assertEqual(result["missing_legs"], [])

    def test_manual_residue_non_empty_in_PARTIAL_case(self):
        legs = _set_leg_verdict(_clean_legs(), "V5", "not_captured")
        receipt = _receipt(legs, overall_gate="PARTIAL")
        result = QG.build_result(receipt)
        self.assertGreater(len(result["manual_residue_checklist"]), 0)
        self.assertTrue(
            any(item["category"] == "leg-not-captured"
                for item in result["manual_residue_checklist"])
        )


class TestManualResidueInvariant(unittest.TestCase):
    def test_residue_never_empty_even_on_PASS(self):
        """a11y is only ever partially auto-covered -- the canonical WCAG residue
        ships on EVERY run, including a clean PASS."""
        receipt = _receipt(_clean_legs(), overall_gate="PASS")
        result = QG.build_result(receipt)
        self.assertGreater(len(result["manual_residue_checklist"]), 0)
        self.assertTrue(
            all(item["category"] == "manual-wcag-residue"
                for item in result["manual_residue_checklist"])
        )

    def test_receipt_reported_residue_is_echoed(self):
        receipt = _receipt(
            _clean_legs(), overall_gate="PASS",
            manual_residue=["reviewer must confirm the executive summary tone"],
        )
        result = QG.build_result(receipt)
        self.assertTrue(
            any(
                item["category"] == "receipt-reported-residue"
                and item["detail"] == "reviewer must confirm the executive summary tone"
                for item in result["manual_residue_checklist"]
            )
        )

    def test_needs_review_evidence_surfaces_in_checklist(self):
        legs = _set_leg_verdict(
            _clean_legs(), "V6", "pass",
            evidence="node #kpi-report-date flagged needs-review: frozen-misclassified per sec 4",
        )
        receipt = _receipt(legs, overall_gate="PASS")
        result = QG.build_result(receipt)
        self.assertTrue(
            any(item["category"] == "needs-review-node"
                for item in result["manual_residue_checklist"])
        )

    def test_v1_binding_correctness_degrade_flags_values_unverified(self):
        legs = _set_leg_verdict(
            _clean_legs(), "V1", "PARTIAL",
            evidence="no live XMLA/REST route reachable; binding-correctness mode only",
        )
        receipt = _receipt(legs, overall_gate="PARTIAL")
        result = QG.build_result(receipt)
        self.assertEqual(result["computed_gate"], "PARTIAL")
        self.assertTrue(
            any(item["category"] == "values-unverified"
                for item in result["manual_residue_checklist"])
        )
        # V1 is blocking but verdict is PARTIAL, not "fail" -- a degrade, never
        # the hard FAIL tier.
        self.assertEqual(result["blocking_leg_failures"], [])


class TestTieringEdgeCases(unittest.TestCase):
    def test_missing_leg_forces_PARTIAL(self):
        legs = [leg for leg in _clean_legs() if leg["leg"] != "period-coherence"]
        receipt = _receipt(legs, overall_gate="PARTIAL")
        result = QG.build_result(receipt)
        self.assertEqual(result["computed_gate"], "PARTIAL")
        self.assertIn("period-coherence", result["missing_legs"])

    def test_nonblocking_fail_does_not_force_hard_FAIL_but_blocks_PASS(self):
        legs = _set_leg_verdict(_clean_legs(), "V5", "fail", evidence="overlap detected")
        receipt = _receipt(legs, overall_gate="PARTIAL")
        result = QG.build_result(receipt)
        self.assertEqual(result["computed_gate"], "PARTIAL")
        self.assertEqual(result["blocking_leg_failures"], [])

    def test_blocking_probe_error_hard_fails(self):
        # Code-review-loop fix #6 (P2): a crashed BLOCKING leg (PROBE_ERROR) must FAIL, never soften
        # to PARTIAL. "We could not run the leak/fidelity scan" is a hard failure (PROBE_ERROR != pass),
        # matching the harness's own compute_gate — the two stages must not disagree on the safety case.
        legs = _set_leg_verdict(_clean_legs(), "V2", "PROBE_ERROR", evidence="parser crashed")
        receipt = _receipt(legs, overall_gate="FAIL")
        result = QG.build_result(receipt)
        self.assertEqual(result["computed_gate"], "FAIL")
        self.assertIn("V2", result["blocking_leg_failures"])
        self.assertFalse(any(d.get("leg") == "V2" for d in result["degraded_legs"]))

    def test_overclaim_detected_when_receipt_claims_better_than_computed(self):
        legs = _set_leg_verdict(_clean_legs(), "V5", "not_captured")
        receipt = _receipt(legs, overall_gate="PASS")  # receipt over-claims PASS
        result = QG.build_result(receipt)
        self.assertEqual(result["computed_gate"], "PARTIAL")
        self.assertTrue(result["overclaim_detected"])

    def test_no_overclaim_when_receipt_matches_computed(self):
        receipt = _receipt(_clean_legs(), overall_gate="PASS")
        result = QG.build_result(receipt)
        self.assertFalse(result["overclaim_detected"])


class TestReceiptValidation(unittest.TestCase):
    def test_missing_required_field_raises(self):
        receipt = _receipt(_clean_legs())
        del receipt["env_fingerprint"]
        with self.assertRaises(QG.QAGateError):
            QG.build_result(receipt)

    def test_bad_verdict_enum_raises(self):
        legs = _clean_legs()
        legs[0]["verdict"] = "kinda-passed"
        receipt = _receipt(legs)
        with self.assertRaises(QG.QAGateError):
            QG.build_result(receipt)

    def test_empty_legs_array_raises(self):
        receipt = _receipt(_clean_legs())
        receipt["legs"] = []
        with self.assertRaises(QG.QAGateError):
            QG.build_result(receipt)


class TestPathGuard(unittest.TestCase):
    def test_rejects_traversal(self):
        with self.assertRaises(QG.QAGateError):
            QG._guard_path("../../../etc/passwd")

    def test_rejects_absolute_path(self):
        with self.assertRaises(QG.QAGateError):
            QG._guard_path("/etc/passwd")

    def test_rejects_missing_file(self):
        with self.assertRaises(QG.QAGateError):
            QG._guard_path(
                "plugins/report-regeneration/skills/report-qa-gate/"
                "definitely-not-a-real-receipt.json"
            )


def _a11y(gate="PASS", violations=None, manual_residue=None):
    return {
        "schema": QG.A11Y_SCHEMA,
        "gate": gate,
        "violations": violations if violations is not None else [],
        "manual_residue": manual_residue if manual_residue is not None
        else ["alt-text QUALITY is human-judged (the ~30-50% floor)"],
    }


def _injection(gate="PASS", findings=None):
    return {
        "schema": QG.INJECTION_SCHEMA,
        "gate": gate,
        "findings": findings if findings is not None else [],
    }


_A11Y_FAIL = _a11y(
    gate="FAIL",
    violations=[{
        "rule": "img-alt", "wcag": "1.1.1", "impact": "critical", "blocking": True,
        "node": "img#chart-region-mix", "detail": "a non-decorative <img> has no alt (D3)",
    }],
)
_INJECTION_FAIL = _injection(
    gate="FAIL",
    findings=[{
        "check": "provenance-bound-narrative", "node": "#outlook-narrative",
        "token": "finance-verify@corp-payouts.example", "blocking": True,
        "detail": "an un-provenanced email in a regenerate slot (D13)",
    }],
)


class TestAdjacentGateFolding(unittest.TestCase):
    """The a11y + injection sub-receipts fold into the assembled verdict (the D3 / D13 wiring)."""

    def test_backward_compatible_without_subreceipts(self):
        result = QG.build_result(_receipt(_clean_legs(), overall_gate="PASS"))
        self.assertEqual(result["computed_gate"], "PASS")
        self.assertIsNone(result["a11y_gate"])
        self.assertIsNone(result["injection_gate"])
        self.assertEqual(result["aux_gate_failures"], [])

    def test_a11y_blocking_folds_to_FAIL(self):
        # a clean fidelity receipt (PASS) + a blocking a11y violation -> assembled FAIL (D3 path)
        result = QG.build_result(
            _receipt(_clean_legs(), overall_gate="PASS"), a11y=_A11Y_FAIL,
        )
        self.assertEqual(result["fidelity_gate"], "PASS")
        self.assertEqual(result["a11y_gate"], "FAIL")
        self.assertEqual(result["computed_gate"], "FAIL")
        self.assertIn("a11y", result["aux_gate_failures"])
        self.assertFalse(result["review_ready"])
        self.assertTrue(any(item["category"] == "a11y-blocking"
                            for item in result["manual_residue_checklist"]))

    def test_injection_blocking_folds_to_FAIL(self):
        # a clean fidelity receipt (PASS) + a blocking injection finding -> assembled FAIL (D13 path)
        result = QG.build_result(
            _receipt(_clean_legs(), overall_gate="PASS"), injection=_INJECTION_FAIL,
        )
        self.assertEqual(result["injection_gate"], "FAIL")
        self.assertEqual(result["computed_gate"], "FAIL")
        self.assertIn("injection", result["aux_gate_failures"])
        self.assertTrue(any(item["category"] == "injection-blocking"
                            for item in result["manual_residue_checklist"]))

    def test_both_pass_keeps_fidelity_tier_and_folds_residue(self):
        result = QG.build_result(
            _receipt(_clean_legs(), overall_gate="PASS"),
            a11y=_a11y("PASS"), injection=_injection("PASS"),
        )
        self.assertEqual(result["computed_gate"], "PASS")
        self.assertEqual(result["a11y_gate"], "PASS")
        self.assertEqual(result["injection_gate"], "PASS")
        self.assertEqual(result["aux_gate_failures"], [])
        # a11y manual residue folds into the checklist even on a clean PASS
        self.assertTrue(any(item["category"] == "a11y-manual-residue"
                            for item in result["manual_residue_checklist"]))

    def test_a11y_pass_does_not_upgrade_a_partial(self):
        legs = _set_leg_verdict(_clean_legs(), "V5", "not_captured")
        result = QG.build_result(
            _receipt(legs, overall_gate="PARTIAL"), a11y=_a11y("PASS"),
        )
        self.assertEqual(result["computed_gate"], "PARTIAL")

    def test_a11y_fail_beats_a_partial(self):
        legs = _set_leg_verdict(_clean_legs(), "V5", "not_captured")
        result = QG.build_result(
            _receipt(legs, overall_gate="PARTIAL"), a11y=_A11Y_FAIL,
        )
        self.assertEqual(result["computed_gate"], "FAIL")

    def test_aux_failure_is_not_an_overclaim(self):
        # receipt honestly claims PASS about its OWN legs; the a11y failure is adjacent, so the
        # receipt did not over-claim -- overclaim_detected stays False even though computed==FAIL.
        result = QG.build_result(
            _receipt(_clean_legs(), overall_gate="PASS"), a11y=_A11Y_FAIL,
        )
        self.assertEqual(result["computed_gate"], "FAIL")
        self.assertFalse(result["overclaim_detected"])

    def test_malformed_a11y_schema_raises(self):
        bad = _a11y("PASS")
        bad["schema"] = "not-the-a11y-schema"
        with self.assertRaises(QG.QAGateError):
            QG.build_result(_receipt(_clean_legs(), overall_gate="PASS"), a11y=bad)

    def test_malformed_injection_gate_raises(self):
        bad = _injection("PASS")
        bad["gate"] = "kinda-ok"
        with self.assertRaises(QG.QAGateError):
            QG.build_result(_receipt(_clean_legs(), overall_gate="PASS"), injection=bad)


class TestCLI(unittest.TestCase):
    """Exercises the process-boundary contract: argv parsing, path guard, exit
    codes, and the JSON envelope on stdout."""

    def _run_receipt(self, receipt, extra_args=None):
        fd, path = tempfile.mkstemp(suffix=".json", dir=str(Path(__file__).resolve().parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(receipt, fh)
            rel = os.path.relpath(path, start=str(REPO_ROOT))
            cmd = [sys.executable, str(SCRIPT), "--receipt", rel, "--format", "json"]
            if extra_args:
                cmd.extend(extra_args)
            return subprocess.run(
                cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30
            )
        finally:
            os.remove(path)

    def test_cli_clean_receipt_exit_0(self):
        proc = self._run_receipt(_receipt(_clean_legs(), overall_gate="PASS"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["computed_gate"], "PASS")

    def test_cli_v4_fail_exit_1(self):
        legs = _set_leg_verdict(_clean_legs(), "V4", "fail")
        proc = self._run_receipt(_receipt(legs, overall_gate="FAIL"))
        self.assertEqual(proc.returncode, 1, proc.stderr)

    def test_cli_partial_exit_3(self):
        legs = _set_leg_verdict(_clean_legs(), "V5", "not_captured")
        proc = self._run_receipt(_receipt(legs, overall_gate="PARTIAL"))
        self.assertEqual(proc.returncode, 3, proc.stderr)

    def test_cli_path_traversal_exit_2(self):
        cmd = [
            sys.executable, str(SCRIPT),
            "--receipt", "../../../../../../etc/passwd",
            "--format", "json",
        ]
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 2)

    def test_cli_invalid_json_exit_2(self):
        fd, path = tempfile.mkstemp(suffix=".json", dir=str(Path(__file__).resolve().parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write("{not valid json")
            rel = os.path.relpath(path, start=str(REPO_ROOT))
            cmd = [sys.executable, str(SCRIPT), "--receipt", rel]
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30)
            self.assertEqual(proc.returncode, 2)
        finally:
            os.remove(path)

    def test_cli_version_flag(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--version"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), QG.GATE_VERSION)

    def test_cli_a11y_subreceipt_folds_to_fail_exit_1(self):
        """--a11y feeds a blocking a11y sub-receipt; a clean fidelity receipt still exits 1."""
        rfd, rpath = tempfile.mkstemp(suffix=".json", dir=str(Path(__file__).resolve().parent))
        afd, apath = tempfile.mkstemp(suffix=".json", dir=str(Path(__file__).resolve().parent))
        try:
            with os.fdopen(rfd, "w", encoding="utf-8") as fh:
                json.dump(_receipt(_clean_legs(), overall_gate="PASS"), fh)
            with os.fdopen(afd, "w", encoding="utf-8") as fh:
                json.dump(_A11Y_FAIL, fh)
            rrel = os.path.relpath(rpath, start=str(REPO_ROOT))
            arel = os.path.relpath(apath, start=str(REPO_ROOT))
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--receipt", rrel, "--a11y", arel,
                 "--format", "json"],
                cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(proc.returncode, 1, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["computed_gate"], "FAIL")
            self.assertEqual(payload["a11y_gate"], "FAIL")
        finally:
            os.remove(rpath)
            os.remove(apath)


if __name__ == "__main__":
    unittest.main()
