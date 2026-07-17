#!/usr/bin/env python3
"""
Unit + integration tests for rebind_html.py (the `rebind-html` skill, report-regeneration
pipeline stage 3).

Covers the required contract:
  - frozen nodes are byte-identical template<->output
  - a surgical value is replaced and the OLD value is absent from that node
  - a regenerate node (text AND raster) reflects new data, old value absent
  - needs-review nodes are flagged, left untouched, and logged
  - the output parses under html.parser
  - the CLI is path-guarded, exit-coded, and never mutates the template file
  - the real sample-report.html corpus end-to-end

Stdlib-only (unittest, json, subprocess, hashlib, tempfile). Runnable both directly
(`python3 test_rebind.py`) and via `python3 -m pytest` if pytest happens to be installed
— neither is required.

Run from repo root:
    python3 plugins/report-regeneration/skills/rebind-html/tests/test_rebind.py
"""
from __future__ import annotations

import copy
import hashlib
import html.parser
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT = SKILL_DIR / "rebind_html.py"
SAMPLE_REPORT_PATH = REPO_ROOT / "tests" / "fixtures" / "report-regeneration" / "sample-report.html"

if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

import rebind_html as rh  # noqa: E402


# ── small synthetic fixture (fast, self-contained, exercises every node class) ──

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Test Report</title></head>
<body>
<p id="frozen-note" data-role="frozen">This report is prepared for internal use only.</p>
<span id="kpi-revenue" data-role="surgical" data-bind="revenue.total">$1,000</span>
<p id="narrative" data-role="regenerate">Legacy Co delivered $1,000 in Q4 2024.</p>
<img id="logo" data-role="frozen" src="data:image/gif;base64,OLDLOGO==" alt="Old Co logo" width="10" height="10">
<img id="chart" data-role="regenerate" src="data:image/gif;base64,OLDCHART==" alt="Old chart, Q4 2024">
<p id="tagline" data-role="frozen">100% Committed to Quality since 1998.</p>
</body>
</html>
"""

FROZEN_BINDING = {
    "node_id": "n-frozen-note",
    "anchor": {"kind": "element_id", "value": "frozen-note"},
    "class": "frozen",
    "confidence": 0.99,
    "provenance": {"source": "n/a", "source_period": None},
    "data_query": None,
}

FROZEN_LOGO_BINDING = {
    "node_id": "n-logo",
    "anchor": {"kind": "element_id", "value": "logo"},
    "class": "frozen",
    "confidence": 0.99,
    "provenance": {"source": "n/a", "source_period": None},
    "data_query": None,
}

SURGICAL_BINDING = {
    "node_id": "n-kpi-revenue",
    "anchor": {"kind": "element_id", "value": "kpi-revenue"},
    "class": "surgical",
    "confidence": 0.95,
    "provenance": {"source": "new-erp", "source_period": "2025-Q1", "method": "native-parse"},
    "data_query": {"kind": "literal-from-new-source", "expression": "revenue.total", "source_ref": "new-erp"},
}

REGENERATE_TEXT_BINDING = {
    "node_id": "n-narrative",
    "anchor": {"kind": "element_id", "value": "narrative"},
    "class": "regenerate",
    "confidence": 0.8,
    "provenance": {"source": "new-erp", "source_period": "2025-Q1"},
    "data_query": {"kind": "literal-from-new-source", "expression": "templates.narrative"},
}

REGENERATE_IMAGE_BINDING = {
    "node_id": "n-chart",
    "anchor": {"kind": "element_id", "value": "chart"},
    "class": "regenerate",
    "confidence": 0.9,
    "provenance": {"source": "chart-engine", "source_period": "2025-Q1"},
    "data_query": {"kind": "screenshot-capture", "expression": "assets.chart"},
}

NEEDS_REVIEW_BINDING = {
    "node_id": "n-tagline",
    "anchor": {"kind": "element_id", "value": "tagline"},
    "class": "needs-review",
    "confidence": 0.42,
    "provenance": {"source": "n/a", "source_period": None},
    "data_query": {"kind": "none", "expression": "ambiguous-marketing-literal"},
}

MANIFEST = {
    "manifest_version": "1.0.0",
    "rsg_schema_version": "1.0.0",
    "template_id": "test-report",
    "format": "html",
    "bindings": [
        FROZEN_BINDING,
        FROZEN_LOGO_BINDING,
        SURGICAL_BINDING,
        REGENERATE_TEXT_BINDING,
        REGENERATE_IMAGE_BINDING,
        NEEDS_REVIEW_BINDING,
    ],
}

NEW_DATA = {
    "revenue": {"total": "$2,500"},
    "templates": {"narrative": "Acme Co delivered ${revenue.total} in Q1 2025."},
    "assets": {"chart": {"src": "data:image/gif;base64,NEWCHART==", "alt": "New chart, Q1 2025"}},
}


class TestCoreMechanics(unittest.TestCase):
    def test_frozen_is_byte_identical(self):
        output, _changes, _nrc = rh.rebind(TEMPLATE, MANIFEST, NEW_DATA)
        self.assertEqual(
            rh.full_node_text(TEMPLATE, "frozen-note"), rh.full_node_text(output, "frozen-note")
        )
        self.assertEqual(rh.full_node_text(TEMPLATE, "logo"), rh.full_node_text(output, "logo"))

    def test_frozen_violation_is_caught(self):
        # A frozen node whose bytes DID move between template and output must raise —
        # proves _assert_frozen_unchanged has teeth, not just an unchecked assumption.
        mutated_output = TEMPLATE.replace("internal use only", "MUTATED")
        with self.assertRaises(rh.RebindError):
            rh._assert_frozen_unchanged(TEMPLATE, mutated_output, MANIFEST["bindings"])

    def test_surgical_replaces_value_and_old_value_absent(self):
        output, changes, _nrc = rh.rebind(TEMPLATE, MANIFEST, NEW_DATA)
        node = rh.full_node_text(output, "kpi-revenue")
        self.assertIn("$2,500", node)
        self.assertNotIn("$1,000", node)
        surgical_entries = [c for c in changes if c["class"] == "surgical"]
        self.assertEqual(len(surgical_entries), 1)
        self.assertEqual(surgical_entries[0]["old_value"], "$1,000")
        self.assertEqual(surgical_entries[0]["new_value"], "$2,500")

    def test_strip_then_write_is_a_genuine_two_step_zero_literal_construction(self):
        # The midpoint between strip and write must carry NO old instance value.
        stripped, old = rh.strip_inner_by_id(TEMPLATE, "kpi-revenue")
        self.assertEqual(old, "$1,000")
        self.assertNotIn("$1,000", rh.full_node_text(stripped, "kpi-revenue"))
        written = rh.write_inner_by_id(stripped, "kpi-revenue", "$2,500")
        self.assertIn("$2,500", rh.full_node_text(written, "kpi-revenue"))

    def test_regenerate_text_reflects_new_data(self):
        output, _changes, _nrc = rh.rebind(TEMPLATE, MANIFEST, NEW_DATA)
        node = rh.full_node_text(output, "narrative")
        self.assertIn("$2,500", node)
        self.assertIn("Acme Co", node)
        self.assertNotIn("$1,000", node)
        self.assertNotIn("Legacy Co", node)

    def test_regenerate_image_rebinds_src_and_alt_old_value_absent(self):
        output, _changes, _nrc = rh.rebind(TEMPLATE, MANIFEST, NEW_DATA)
        node = rh.full_node_text(output, "chart")
        self.assertIn("NEWCHART", node)
        self.assertIn("New chart, Q1 2025", node)
        self.assertNotIn("OLDCHART", node)
        self.assertNotIn("Old chart, Q4 2024", node)

    def test_needs_review_flags_visibly_and_leaves_content_untouched(self):
        output, changes, needs_review_count = rh.rebind(TEMPLATE, MANIFEST, NEW_DATA)
        self.assertEqual(needs_review_count, 1)
        node = rh.full_node_text(output, "tagline")
        self.assertIn('data-rebind-flag="needs-review"', node)
        self.assertIn("NEEDS REVIEW", node)
        self.assertIn("100% Committed to Quality since 1998.", node)  # original untouched
        review_entries = [c for c in changes if c["class"] == "needs-review"]
        self.assertEqual(len(review_entries), 1)
        self.assertEqual(review_entries[0]["anchor"], "tagline")

    def test_output_parses_under_html_parser(self):
        output, _changes, _nrc = rh.rebind(TEMPLATE, MANIFEST, NEW_DATA)
        rh._assert_parseable(output)  # must not raise
        parser = html.parser.HTMLParser()
        parser.feed(output)
        parser.close()

    def test_render_template_stdlib_only(self):
        rendered = rh.render_template("Total: ${revenue.total}", NEW_DATA)
        self.assertEqual(rendered, "Total: $2,500")

    def test_render_template_jinja_syntax_without_jinja2_raises_loudly(self):
        if rh.jinja2 is not None:
            self.skipTest("jinja2 is installed in this environment; nothing to assert here")
        with self.assertRaises(rh.RebindError):
            rh.render_template("{% if true %}x{% endif %}", NEW_DATA)

    def test_load_manifest_rejects_frozen_with_data_query(self):
        bad = copy.deepcopy(MANIFEST)
        bad["bindings"] = [dict(FROZEN_BINDING, data_query={"kind": "none", "expression": "x"})]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad-manifest.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(rh.RebindError):
                rh.load_manifest(path)

    def test_load_manifest_rejects_non_frozen_without_data_query(self):
        bad = copy.deepcopy(MANIFEST)
        bad["bindings"] = [dict(SURGICAL_BINDING, data_query=None)]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad-manifest.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(rh.RebindError):
                rh.load_manifest(path)

    def test_load_manifest_rejects_non_html_format(self):
        bad = copy.deepcopy(MANIFEST)
        bad["format"] = "office"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad-manifest.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(rh.RebindError):
                rh.load_manifest(path)


class TestSampleReportCorpus(unittest.TestCase):
    """End-to-end against the real Phase-0 corpus fixture (tests/fixtures/
    report-regeneration/sample-report.html)."""

    @classmethod
    def setUpClass(cls):
        if not SAMPLE_REPORT_PATH.is_file():
            raise unittest.SkipTest(f"corpus fixture not found: {SAMPLE_REPORT_PATH}")
        cls.template_html = SAMPLE_REPORT_PATH.read_text(encoding="utf-8")

    @staticmethod
    def _manifest():
        return {
            "manifest_version": "1.0.0",
            "rsg_schema_version": "1.0.0",
            "template_id": "acme-widgets-q1-2025",
            "format": "html",
            "bindings": [
                {
                    "node_id": "b-logo",
                    "anchor": {"kind": "element_id", "value": "logo-header"},
                    "class": "frozen",
                    "confidence": 0.99,
                    "provenance": {"source": "n/a", "source_period": None},
                    "data_query": None,
                },
                {
                    "node_id": "b-kpi-revenue",
                    "anchor": {"kind": "element_id", "value": "kpi-revenue"},
                    "class": "surgical",
                    "confidence": 0.97,
                    "provenance": {"source": "new-erp", "source_period": "2025-Q2", "method": "native-parse"},
                    "data_query": {"kind": "literal-from-new-source", "expression": "revenue.total", "source_ref": "new-erp"},
                },
                {
                    "node_id": "b-hdr-period",
                    "anchor": {"kind": "element_id", "value": "hdr-period"},
                    "class": "surgical",
                    "confidence": 0.95,
                    "provenance": {"source": "new-erp", "source_period": "2025-Q2"},
                    "data_query": {"kind": "literal-from-new-source", "expression": "meta.period_label"},
                },
                {
                    "node_id": "b-exec-summary",
                    "anchor": {"kind": "element_id", "value": "exec-summary-narrative"},
                    "class": "regenerate",
                    "confidence": 0.7,
                    "provenance": {"source": "new-erp", "source_period": "2025-Q2"},
                    "data_query": {"kind": "literal-from-new-source", "expression": "templates.exec_summary"},
                },
                {
                    "node_id": "b-chart-region-mix",
                    "anchor": {"kind": "element_id", "value": "chart-region-mix"},
                    "class": "regenerate",
                    "confidence": 0.9,
                    "provenance": {"source": "chart-engine", "source_period": "2025-Q2"},
                    "data_query": {"kind": "screenshot-capture", "expression": "assets.chart_region_mix"},
                },
                {
                    # the deliberately-tricky percent-shaped marketing literal, per the
                    # fixture's own header comment — correctly classed needs-review, not
                    # frozen, by whatever upstream classifier produced this manifest.
                    "node_id": "b-tagline",
                    "anchor": {"kind": "element_id", "value": "tagline-text"},
                    "class": "needs-review",
                    "confidence": 0.42,
                    "provenance": {"source": "n/a", "source_period": None},
                    "data_query": {"kind": "none", "expression": "unclassified-marketing-literal"},
                },
            ],
        }

    @staticmethod
    def _new_data():
        return {
            "revenue": {"total": "$5,014,300"},
            "meta": {"period_label": "Q2 2025"},
            "templates": {
                "exec_summary": (
                    "Acme Widgets delivered ${revenue.total} in ${meta.period_label}, a new "
                    "quarterly record."
                ),
            },
            "assets": {
                "chart_region_mix": {
                    "src": "data:image/gif;base64,UkVHRU5FUkFURUQ=",
                    "alt": "Bar chart comparing Q2 2025 revenue share across regions.",
                },
            },
        }

    def test_end_to_end_against_real_corpus(self):
        manifest = self._manifest()
        new_data = self._new_data()
        output, changes, needs_review_count = rh.rebind(self.template_html, manifest, new_data)

        # frozen (void element) — byte-identical
        self.assertEqual(
            rh.full_node_text(self.template_html, "logo-header"),
            rh.full_node_text(output, "logo-header"),
        )

        # surgical — new value present, OLD value absent, at that node
        kpi = rh.full_node_text(output, "kpi-revenue")
        self.assertIn("$5,014,300", kpi)
        self.assertNotIn("$4,821,300", kpi)

        hdr = rh.full_node_text(output, "hdr-period")
        self.assertIn("Q2 2025", hdr)
        self.assertNotIn("Q1 2025", hdr)

        # regenerate (text) — reflects new data; old figures gone from that node
        narrative = rh.full_node_text(output, "exec-summary-narrative")
        self.assertIn("$5,014,300", narrative)
        self.assertIn("Q2 2025", narrative)
        self.assertNotIn("$4,821,300", narrative)
        self.assertNotIn("+12.4%", narrative)

        # regenerate (raster) — src/alt rebound, old asset bytes/alt gone
        chart = rh.full_node_text(output, "chart-region-mix")
        self.assertIn("UkVHRU5FUkFURUQ=", chart)
        self.assertIn("Q2 2025 revenue share", chart)
        self.assertNotIn("R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==", chart)
        self.assertNotIn("Bar chart comparing Q1 2025", chart)

        # needs-review — flagged, original text untouched, logged exactly once
        tagline = rh.full_node_text(output, "tagline-text")
        self.assertIn('data-rebind-flag="needs-review"', tagline)
        self.assertIn("100% Committed to Quality", tagline)
        self.assertEqual(needs_review_count, 1)

        # the template file on disk was never touched by processing it in memory
        self.assertEqual(self.template_html, SAMPLE_REPORT_PATH.read_text(encoding="utf-8"))

        # the whole regenerated document still parses
        rh._assert_parseable(output)
        change_classes = sorted(c["class"] for c in changes)
        self.assertEqual(change_classes, ["frozen", "needs-review", "regenerate", "regenerate", "surgical", "surgical"])


class TestCLI(unittest.TestCase):
    """Process-boundary tests: exit codes, path-guard, and the works-on-a-copy
    guarantee (the template file is never mutated on disk)."""

    def setUp(self):
        self.out_dir = REPO_ROOT / "tests" / "fixtures" / "report-regeneration" / "_out"
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir)

    @staticmethod
    def _rel(path: Path) -> str:
        return str(path.relative_to(REPO_ROOT))

    def _write_fixture_set(self):
        template_path = self.out_dir / "template.html"
        manifest_path = self.out_dir / "manifest.json"
        data_path = self.out_dir / "new-data.json"
        template_path.write_text(TEMPLATE, encoding="utf-8")
        manifest_path.write_text(json.dumps(MANIFEST), encoding="utf-8")
        data_path.write_text(json.dumps(NEW_DATA), encoding="utf-8")
        return template_path, manifest_path, data_path

    def test_cli_happy_path_writes_output_and_never_mutates_template(self):
        template_path, manifest_path, data_path = self._write_fixture_set()
        out_path = self.out_dir / "out.html"
        before_hash = hashlib.sha256(template_path.read_bytes()).hexdigest()

        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--template", self._rel(template_path),
                "--manifest", self._rel(manifest_path),
                "--new-data", self._rel(data_path),
                "--out", self._rel(out_path),
            ],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["needs_review_count"], 1)
        self.assertTrue(out_path.is_file())
        self.assertIn("$2,500", out_path.read_text(encoding="utf-8"))

        after_hash = hashlib.sha256(template_path.read_bytes()).hexdigest()
        self.assertEqual(before_hash, after_hash, "the CLI must never mutate --template on disk")

    def test_cli_rejects_out_equal_to_template(self):
        template_path, manifest_path, data_path = self._write_fixture_set()

        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--template", self._rel(template_path),
                "--manifest", self._rel(manifest_path),
                "--new-data", self._rel(data_path),
                "--out", self._rel(template_path),
            ],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])

    def test_cli_rejects_path_traversal(self):
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--template", "../etc/passwd",
                "--manifest", "x.json",
                "--new-data", "y.json",
                "--out", "z.html",
            ],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])

    def test_cli_rejects_absolute_path(self):
        template_path, manifest_path, data_path = self._write_fixture_set()
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--template", str(template_path),  # absolute — must be rejected
                "--manifest", self._rel(manifest_path),
                "--new-data", self._rel(data_path),
                "--out", self._rel(self.out_dir / "out.html"),
            ],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
