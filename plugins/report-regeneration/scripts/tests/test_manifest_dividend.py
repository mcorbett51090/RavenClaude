#!/usr/bin/env python3
"""
test_manifest_dividend.py — unit tests for manifest_dividend.py (Phase-1 manifest-dividend
measurement, plan §5-P1).

Covers:
  1. `_is_human_touch` — needs-review OR sub-threshold confidence, nothing else.
  2. `human_amend_binding` — all four heuristic branches (discoverable data-bind key -> surgical;
     chart/image role -> regenerate; narrative role -> regenerate; unbound data-shaped literal ->
     surgical w/ human-authored placeholder; otherwise -> frozen).
  3. `reuse_manifest_for_new_period` — the two MUST-FAIL-style mutant proofs that the per-period
     re-check has teeth: (a) a frozen node whose text collides with the new period's value domain
     is demoted and counted as a touch (the earned-frozen re-check firing on a genuine mutant,
     mirroring this plugin's audit-gates.sh bidirectional-fixture convention); (b) a `file-cell`
     binding whose key the new period's dataset does not cover is counted as a touch (a coverage
     gap). Also proves the clean/good-path halves: no false positives on a non-colliding frozen
     node or a covered key, and a residual needs-review binding is still surfaced.
  4. `measure()` end-to-end on the real corpus (tests/fixtures/report-regeneration) — pins the
     regression values this run currently observes (run-1 touches, run-2 touches, dividend holds).
  5. `_guard_path` rejects path traversal.
  6. CLI smoke test (subprocess): --format text and --out both work, exit code 0.

Stdlib only (unittest). Runnable directly (`python3 test_manifest_dividend.py`) or via pytest.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = Path(__file__).resolve().parents[4]

if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import manifest_dividend as md  # noqa: E402


def _load_pipeline():
    return md._load_pipeline()


# ── a tiny inline template + RSG, independent of the real corpus, for the unit-level tests ─────

_INLINE_TEMPLATE = (
    "<!DOCTYPE html>\n"
    '<html lang="en">\n'
    "<head><title>Doc</title></head>\n"
    "<body>\n"
    '<h2 id="heading-frozen">Static Heading</h2>\n'
    '<span id="kpi-bound" data-bind="revenue.total">$1,000</span>\n'
    '<img id="chart-node" src="data:image/gif;base64,AA==" alt="a chart">\n'
    '<p id="narrative-node">Some generated prose.</p>\n'
    '<p id="mystery-node">Unbound but shaped: $500</p>\n'
    '<p id="plain-node">Nothing special here.</p>\n'
    "</body>\n"
    "</html>\n"
)


def _rsg_node(node_id, role, data_shaped):
    return {
        "id": node_id,
        "anchor": {"kind": "element_id", "value": node_id},
        "role": role,
        "class": "needs-review",
        "confidence": 0.5,
        "provenance": {"method": "rule-based", "source": "t", "source_period": None},
        "data_shaped_literal": data_shaped,
        "children": [],
    }


_RSG_INDEX = {
    "heading-frozen": _rsg_node("heading-frozen", "heading", False),
    "kpi-bound": _rsg_node("kpi-bound", "kpi-value", True),
    "chart-node": _rsg_node("chart-node", "chart", False),
    "narrative-node": _rsg_node("narrative-node", "narrative", False),
    "mystery-node": _rsg_node("mystery-node", "unknown", True),
    "plain-node": _rsg_node("plain-node", "static-chrome", False),
}


def _binding(node_id):
    return {
        "node_id": node_id,
        "anchor": {"kind": "element_id", "value": node_id},
        "class": "needs-review",
        "confidence": 0.5,
        "provenance": {"source": "t", "source_period": None},
        "data_query": {"kind": "none", "expression": "pending human sign-off; no binding proposed until reviewed"},
    }


class TestIsHumanTouch(unittest.TestCase):
    def test_needs_review_is_a_touch(self):
        self.assertTrue(md._is_human_touch({"class": "needs-review", "confidence": 0.95}, 0.7))

    def test_sub_threshold_confidence_is_a_touch_even_if_class_resolved(self):
        self.assertTrue(md._is_human_touch({"class": "surgical", "confidence": 0.5}, 0.7))

    def test_resolved_and_confident_is_not_a_touch(self):
        self.assertFalse(md._is_human_touch({"class": "frozen", "confidence": 0.9}, 0.7))


class TestHumanAmendBinding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _infer, _build_manifest, cls.rr_anchor = _load_pipeline()

    def _amend(self, node_id):
        return md.human_amend_binding(
            _binding(node_id), _RSG_INDEX, _INLINE_TEMPLATE, self.rr_anchor,
            template_id="t", source_ref="period-a", source_period="2025-Q1",
        )

    def test_discoverable_bind_key_resolves_surgical(self):
        b = self._amend("kpi-bound")
        self.assertEqual(b["class"], "surgical")
        self.assertEqual(b["data_query"]["expression"], "revenue.total")
        self.assertEqual(b["confidence"], 1.0)

    def test_chart_role_resolves_regenerate(self):
        b = self._amend("chart-node")
        self.assertEqual(b["class"], "regenerate")
        self.assertEqual(b["data_query"]["kind"], "screenshot-capture")

    def test_narrative_role_resolves_regenerate(self):
        b = self._amend("narrative-node")
        self.assertEqual(b["class"], "regenerate")
        self.assertEqual(b["data_query"]["kind"], "literal-from-new-source")

    def test_unbound_data_shaped_resolves_surgical_placeholder(self):
        b = self._amend("mystery-node")
        self.assertEqual(b["class"], "surgical")
        self.assertEqual(b["data_query"]["expression"], md._HUMAN_AUTHORED_PLACEHOLDER)

    def test_plain_static_resolves_frozen(self):
        b = self._amend("plain-node")
        self.assertEqual(b["class"], "frozen")
        self.assertIsNone(b["data_query"])
        self.assertIsNone(b["provenance"]["source_period"])

    def test_never_leaves_needs_review(self):
        for node_id in _RSG_INDEX:
            b = self._amend(node_id)
            self.assertNotEqual(b["class"], "needs-review")


class TestReuseManifestForNewPeriod(unittest.TestCase):
    """The must-fail-mutant proofs: the per-period re-check must FIRE on a genuine collision /
    coverage gap, and must NOT fire on the clean case."""

    @classmethod
    def setUpClass(cls):
        _infer, cls.build_manifest, cls.rr_anchor = _load_pipeline()

    def _reuse(self, manifest, new_data_b, threshold=0.7):
        return md.reuse_manifest_for_new_period(
            manifest, _INLINE_TEMPLATE, self.build_manifest, self.rr_anchor, new_data_b, threshold
        )

    def test_clean_case_zero_touches(self):
        manifest = {
            "template_id": "t",
            "bindings": [
                {"node_id": "heading-frozen", "anchor": {"kind": "element_id", "value": "heading-frozen"},
                 "class": "frozen", "confidence": 0.9,
                 "provenance": {"source": "t", "source_period": None}, "data_query": None},
                {"node_id": "kpi-bound", "anchor": {"kind": "element_id", "value": "kpi-bound"},
                 "class": "surgical", "confidence": 0.9,
                 "provenance": {"source": "period-a", "source_period": "2025-Q1"},
                 "data_query": {"kind": "file-cell", "expression": "revenue.total", "source_ref": "period-a"}},
            ],
        }
        new_data_b = {"source_ref": "period-b", "source_period": "2025-Q2",
                       "bindings": {"revenue.total": "$2,000"}}
        _reused, touches = self._reuse(manifest, new_data_b)
        self.assertEqual(touches, [])

    def test_frozen_new_domain_collision_is_caught(self):
        """MUST-FAIL MUTANT (good half): a frozen node's UNCHANGING text happens to equal one of
        the new period's values -> the earned-frozen re-check must fire, demote to needs-review,
        and count as a touch. This is a genuine re-check, not re-inference (RT1-F2)."""
        manifest = {
            "template_id": "t",
            "bindings": [
                {"node_id": "heading-frozen", "anchor": {"kind": "element_id", "value": "heading-frozen"},
                 "class": "frozen", "confidence": 0.9,
                 "provenance": {"source": "t", "source_period": None}, "data_query": None},
            ],
        }
        # "Static Heading" is heading-frozen's rendered text — force a collision.
        new_data_b = {"source_ref": "period-b", "source_period": "2025-Q2",
                       "bindings": {"some.key": "Static Heading"}}
        reused, touches = self._reuse(manifest, new_data_b)
        self.assertEqual(len(touches), 1)
        self.assertEqual(reused["bindings"][0]["class"], "needs-review")

    def test_frozen_no_collision_stays_frozen(self):
        """MUST-FAIL MUTANT (bad half): a frozen node whose text does NOT overlap the new
        period's domain values must NOT be flagged (no false positive)."""
        manifest = {
            "template_id": "t",
            "bindings": [
                {"node_id": "heading-frozen", "anchor": {"kind": "element_id", "value": "heading-frozen"},
                 "class": "frozen", "confidence": 0.9,
                 "provenance": {"source": "t", "source_period": None}, "data_query": None},
            ],
        }
        new_data_b = {"source_ref": "period-b", "source_period": "2025-Q2",
                       "bindings": {"revenue.total": "$9,999,999"}}
        reused, touches = self._reuse(manifest, new_data_b)
        self.assertEqual(touches, [])
        self.assertEqual(reused["bindings"][0]["class"], "frozen")

    def test_uncovered_file_cell_key_is_a_coverage_gap(self):
        manifest = {
            "template_id": "t",
            "bindings": [
                {"node_id": "kpi-bound", "anchor": {"kind": "element_id", "value": "kpi-bound"},
                 "class": "surgical", "confidence": 0.9,
                 "provenance": {"source": "period-a", "source_period": "2025-Q1"},
                 "data_query": {"kind": "file-cell", "expression": "revenue.total", "source_ref": "period-a"}},
            ],
        }
        new_data_b = {"source_ref": "period-b", "source_period": "2025-Q2",
                       "bindings": {"some.other.key": "$1"}}  # revenue.total MISSING
        _reused, touches = self._reuse(manifest, new_data_b)
        self.assertEqual(len(touches), 1)
        self.assertIn("revenue.total", touches[0]["reason"])

    def test_human_authored_placeholder_is_not_a_coverage_gap(self):
        """The bespoke human-authored placeholder is exempt from the generic dotted-path coverage
        check (it resolves through its own mechanism, not a dataset lookup)."""
        manifest = {
            "template_id": "t",
            "bindings": [
                {"node_id": "mystery-node", "anchor": {"kind": "element_id", "value": "mystery-node"},
                 "class": "surgical", "confidence": 1.0,
                 "provenance": {"source": "period-a", "source_period": "2025-Q1"},
                 "data_query": {"kind": "file-cell", "expression": md._HUMAN_AUTHORED_PLACEHOLDER,
                                "source_ref": "period-a"}},
            ],
        }
        new_data_b = {"source_ref": "period-b", "source_period": "2025-Q2", "bindings": {}}
        _reused, touches = self._reuse(manifest, new_data_b)
        self.assertEqual(touches, [])

    def test_residual_needs_review_is_surfaced(self):
        manifest = {
            "template_id": "t",
            "bindings": [_binding("mystery-node")],
        }
        new_data_b = {"source_ref": "period-b", "source_period": "2025-Q2", "bindings": {}}
        _reused, touches = self._reuse(manifest, new_data_b)
        self.assertEqual(len(touches), 1)
        self.assertIn("residual", touches[0]["reason"])


class TestGuardPath(unittest.TestCase):
    def test_rejects_traversal(self):
        with self.assertRaises(md.ManifestDividendError):
            md._guard_path("../evil.json", must_exist=False)

    def test_rejects_empty(self):
        with self.assertRaises(md.ManifestDividendError):
            md._guard_path("", must_exist=False)

    def test_accepts_absolute_in_scratch(self):
        with tempfile.TemporaryDirectory() as d:
            p = md._guard_path(str(Path(d) / "out.json"), must_exist=False)
            self.assertTrue(p.is_absolute())


class TestMeasureOnRealCorpus(unittest.TestCase):
    """End-to-end regression on the real corpus — pins the values this run currently observes."""

    @classmethod
    def setUpClass(cls):
        cls.report = md.measure(threshold=0.7, break_even_ratio=0.20)

    def test_schema_and_honesty_label_present(self):
        self.assertEqual(self.report["schema"], md.SCHEMA)
        self.assertIn("SYNTHETIC PROXY", self.report["honesty_label"])
        self.assertIn("NOT a validated human-time study", self.report["honesty_label"])

    def test_run1_touches_match_the_known_corpus_gaps(self):
        # the title (period token baked into otherwise-static text) and the unbound tfoot
        # percentage cell — see sample-report.html's own header comment, tricky cases 3/4.
        self.assertEqual(self.report["dividend"]["run1_human_touches"], 2)
        self.assertEqual(self.report["run1"]["total_bindings"], 31)

    def test_run2_touches_are_far_fewer_than_run1(self):
        d = self.report["dividend"]
        self.assertLess(d["run2_human_touches"], d["run1_human_touches"])
        self.assertLess(d["dividend_ratio"], 0.20)

    def test_break_even_holds_on_this_fixture(self):
        self.assertTrue(self.report["dividend"]["holds"])

    def test_run1_and_run2_cover_the_same_binding_count(self):
        self.assertEqual(self.report["run1"]["total_bindings"], self.report["run2"]["total_bindings"])

    def test_amendment_never_left_a_residual(self):
        self.assertEqual(self.report["run2"]["residual_needs_review_after_run1_amendment"], 0)


class TestCLISmoke(unittest.TestCase):
    def test_text_format_exits_zero(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "manifest_dividend.py"), "--format", "text"],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("dividend_ratio", proc.stdout)

    def test_out_flag_writes_valid_json(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "dividend.json"
            proc = subprocess.run(
                [sys.executable, str(_SCRIPTS_DIR / "manifest_dividend.py"), "--out", str(out)],
                capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(out.is_file())
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertIn("dividend", data)

    def test_strict_exits_nonzero_when_break_even_impossible(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "manifest_dividend.py"),
             "--break-even-ratio", "0.0", "--strict"],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)


if __name__ == "__main__":
    unittest.main()
