#!/usr/bin/env python3
"""
Tests for build_manifest.py (report-regeneration stage 2: detect -> strip -> rebind).

Proves the four load-bearing behaviors from the task brief:
  1. a candidate-`frozen` node containing a data-shaped literal is demoted to `needs-review`
     (via the INDEPENDENT re-run of the pinned detector over the rendered text), while a
     genuinely data-free candidate-`frozen` node stays `frozen`;
  2. the taint dictionary built from the OLD template includes the old company string
     (both the current report's identity AND a declared prior-artifact taint block);
  3. a raster / embedded-binary node is forced to `regenerate`;
  4. the emitted manifest validates against binding-manifest.schema.json.

Stdlib only (unittest). Runs on Python 3.9.6. Uses a tiny inline HTML fixture + a matching
inline RSG so it does not hard-depend on a parallel stage's output.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SKILL_DIR))

import build_manifest as bm  # noqa: E402


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".repo-layout.json").is_file() or (parent / "AGENTS.md").is_file():
            return parent
    raise RuntimeError("repo root not found")


# ── the tiny inline HTML fixture (the OLD template) ──

INLINE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<!--
  TAINT DICTIONARY — literals from the prior client artifact this template superseded:
    old_company:       "Globex Foundry LLC"
    old_author:        "R. Stone, Controller"
    old_source_file:   "globex_q4_2024_final.docx"
    old_revenue_total: "$2,540,000"
-->
<title>Northwind Traders, Inc. Report</title>
</head>
<body>
<h1>Northwind Traders, Inc.</h1>
<img id="logo" alt="Northwind logo"
     src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
     width="10" height="10">
<span id="kpi-rev" class="kpi-value" data-bind="revenue.total">$4,821,300</span>
<p id="tagline">100% Committed to Quality — proudly serving since 1998.</p>
<p id="appendix">Figures are reported in United States Dollars unless otherwise noted.</p>
</body>
</html>
"""

INLINE_NEW_DATA = {
    "source_ref": "northwind_q2_2025.xlsx",
    "source_period": "2025-Q2",
    "values": ["$5,102,900", "+8.1%", "19.2%"],
}


def _node(node_id, anchor_id, role, klass, confidence, method, period, ds_literal,
          pbi_route=None, children=None):
    provenance = {"method": method, "source": "old-template.html", "source_period": period}
    if pbi_route is not None:
        provenance["pbi_route"] = pbi_route
    return {
        "id": node_id,
        "anchor": {"kind": "element_id", "value": anchor_id},
        "role": role,
        "class": klass,
        "confidence": confidence,
        "provenance": provenance,
        "data_shaped_literal": ds_literal,
        "children": children or [],
    }


def _inline_rsg():
    # NOTE: the RSG is schema-valid on input — every candidate-frozen node carries
    # data_shaped_literal=false (a node with the flag true could not be class 'frozen' per
    # rsg.schema.json). The demotion in this test comes from the stage-2 re-run of the
    # independent detector over the rendered text, NOT from the RSG flag.
    root = _node("root", "/html", "static-chrome", "frozen", 1.0, "native-parse", None, False)
    root["anchor"] = {"kind": "json_pointer", "value": "/html"}
    root["children"] = [
        # RSG proposes 'frozen' for the logo; the raster construction-rule overrides -> regenerate
        _node("n-logo", "logo", "image", "frozen", 0.9, "native-parse", None, False),
        # a genuine data value -> stays surgical
        _node("n-kpi", "kpi-rev", "kpi-value", "surgical", 0.95, "llm-labeled", "2025-Q1", True),
        # candidate-frozen WITH a data-shaped literal ("100%") in the rendered text -> needs-review
        _node("n-tagline", "tagline", "narrative", "frozen", 0.9, "llm-labeled", None, False),
        # candidate-frozen, genuinely data-free -> stays frozen (earned)
        _node("n-appendix", "appendix", "narrative", "frozen", 0.9, "native-parse", None, False),
    ]
    return {
        "schema_version": "1.0.0",
        "format": "html",
        "template_id": "northwind-q-report",
        "root": root,
    }


class _Harness:
    """Writes the inline fixture + RSG + new-data to a temp dir and runs the builder."""

    def __init__(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="rebind-manifest-test-"))
        self.template = self.tmp / "template.html"
        self.rsg = self.tmp / "rsg.json"
        self.new_data = self.tmp / "new-data.json"
        self.out = self.tmp / "manifest.json"
        self.template.write_text(INLINE_TEMPLATE, encoding="utf-8")
        self.rsg.write_text(json.dumps(_inline_rsg()), encoding="utf-8")
        self.new_data.write_text(json.dumps(INLINE_NEW_DATA), encoding="utf-8")

    def run(self):
        return bm.run(self.rsg, self.template, self.new_data, self.out)


class TestRebindManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = _Harness()
        cls.result = cls.h.run()
        cls.manifest = json.loads(cls.h.out.read_text(encoding="utf-8"))
        cls.by_id = {b["node_id"]: b for b in cls.manifest["bindings"]}

    # 1. earned-frozen demotion --------------------------------------------------------------
    def test_data_shaped_literal_in_candidate_frozen_demotes_to_needs_review(self):
        tagline = self.by_id["n-tagline"]
        self.assertEqual(tagline["class"], "needs-review",
                         "a candidate-frozen node with '100%' must demote to needs-review")
        # a demoted (non-frozen) node MUST carry a data_query
        self.assertIsNotNone(tagline["data_query"])

    def test_genuinely_data_free_candidate_frozen_stays_frozen(self):
        appendix = self.by_id["n-appendix"]
        self.assertEqual(appendix["class"], "frozen",
                         "a data-free candidate-frozen node keeps its earned frozen class")
        # a frozen binding carries NO data_query
        self.assertIsNone(appendix["data_query"])

    # 2. taint dictionary includes the old company string ------------------------------------
    def test_taint_dict_includes_old_company_inline(self):
        taint = bm.build_taint_dictionary(self.h.template)
        self.assertIn("Globex Foundry LLC", taint["all"])
        self.assertIn("Globex Foundry LLC", taint["identity_strings"])
        self.assertIn("Northwind Traders, Inc.", taint["identity_strings"])

    def test_taint_dict_includes_old_company_real_corpus(self):
        # Faithful check against the real Phase-0 corpus referenced by the brief.
        sample = _repo_root() / "tests" / "fixtures" / "report-regeneration" / "sample-report.html"
        taint = bm.build_taint_dictionary(sample)
        self.assertIn("Ridgeline Fabricators Inc.", taint["all"])
        self.assertIn("Ridgeline Fabricators Inc.", taint["identity_strings"])
        # the current report's own rendered values become 'old' once regenerated
        self.assertIn("$4,821,300", taint["values"])

    # 3. raster node forced to regenerate ----------------------------------------------------
    def test_raster_node_is_regenerate(self):
        logo = self.by_id["n-logo"]
        self.assertEqual(logo["class"], "regenerate",
                         "an <img>/data-URI node must be forced to regenerate")
        self.assertIsNotNone(logo["data_query"])
        self.assertEqual(logo["data_query"]["kind"], "screenshot-capture")

    def test_surgical_value_node_kept_with_query(self):
        kpi = self.by_id["n-kpi"]
        self.assertEqual(kpi["class"], "surgical")
        self.assertIsNotNone(kpi["data_query"])

    # 4. manifest validates against the schema -----------------------------------------------
    def test_manifest_validates_against_schema(self):
        self.assertEqual(bm.validate_manifest(self.manifest), [])
        self.assertTrue(self.result["manifest_valid"])

    def test_one_binding_per_non_static_node(self):
        # root is static-chrome -> excluded; the four children each get one binding
        self.assertEqual(len(self.manifest["bindings"]), 4)

    def test_taint_dict_file_written(self):
        self.assertTrue(Path(self.result["taint_dict_path"]).is_file())

    # CLI end-to-end (exit code + structured stdout) -----------------------------------------
    def test_cli_runs_and_exits_zero(self):
        cli_out = self.h.tmp / "manifest-cli.json"
        proc = subprocess.run(
            [sys.executable, str(_SKILL_DIR / "build_manifest.py"),
             "--rsg", str(self.h.rsg), "--template", str(self.h.template),
             "--new-data", str(self.h.new_data), "--out", str(cli_out)],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(cli_out.is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
