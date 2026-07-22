#!/usr/bin/env python3
"""
Unit + CLI tests for report-a11y-gate/a11y_lint.py.

Run from repo root:
    python3 -m pytest plugins/report-regeneration/skills/report-a11y-gate/tests/test_a11y_lint.py
or:
    python3 plugins/report-regeneration/skills/report-a11y-gate/tests/test_a11y_lint.py

Required coverage:
    - the CLEAN corpus (sample-report.html)              -> gate PASS
    - the D3 injector (missing alt-text)                 -> gate FAIL (img-alt BLOCK)  [crisp catch]
    - each blocking rule fires on a minimal bad fixture and passes on its good twin
    - manual residue is NEVER empty (even on a clean PASS)
    - CLI exit codes 0 / 1 / 2 + --version
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = TESTS_DIR.parent
PLUGIN_DIR = SKILL_DIR.parent.parent
REPO_ROOT = PLUGIN_DIR.parent.parent
SCRIPT = SKILL_DIR / "a11y_lint.py"
SAMPLE = REPO_ROOT / "tests" / "fixtures" / "report-regeneration" / "sample-report.html"
SEED_DEFECTS = PLUGIN_DIR / "scripts" / "seed_defects.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


AL = _load("a11y_lint", SCRIPT)
SEED = _load("rr_seed_defects_for_a11y", SEED_DEFECTS)


def _rules(receipt, blocking_only=False):
    return {
        v["rule"] for v in receipt["violations"]
        if (v["blocking"] or not blocking_only)
    }


class TestCleanCorpus(unittest.TestCase):
    def test_clean_sample_report_passes(self):
        receipt = AL.lint_html(SAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(receipt["gate"], "PASS", receipt["violations"])
        self.assertEqual(receipt["counts"]["blocking"], 0)
        # the fixture declares scope on every <th> and headings h1->h2, so no advisory either
        self.assertEqual(receipt["counts"]["advisory"], 0, receipt["violations"])

    def test_manual_residue_never_empty_on_pass(self):
        receipt = AL.lint_html(SAMPLE.read_text(encoding="utf-8"))
        self.assertGreater(len(receipt["manual_residue"]), 0)


class TestD3CrispCatch(unittest.TestCase):
    """The seeded D3 defect (missing alt-text) must be a crisp img-alt BLOCK -> gate FAIL."""

    def test_d3_missing_alt_is_img_alt_fail(self):
        bad_html, _changes = SEED.inject_D3(SAMPLE.read_text(encoding="utf-8"))
        receipt = AL.lint_html(bad_html)
        self.assertEqual(receipt["gate"], "FAIL")
        self.assertIn("img-alt", _rules(receipt, blocking_only=True))
        # attributed to the exact node the injector stripped
        self.assertTrue(any(
            v["rule"] == "img-alt" and v["node"] == "img#chart-region-mix"
            for v in receipt["violations"]
        ))


class TestImgAlt(unittest.TestCase):
    def test_missing_alt_fails(self):
        r = AL.lint_html('<html lang="en"><body><img src="x.png"></body></html>')
        self.assertEqual(r["gate"], "FAIL")
        self.assertIn("img-alt", _rules(r, blocking_only=True))

    def test_present_alt_passes(self):
        r = AL.lint_html('<html lang="en"><body><img src="x.png" alt="a chart"></body></html>')
        self.assertEqual(r["gate"], "PASS")

    def test_empty_alt_is_decorative_and_passes(self):
        r = AL.lint_html('<html lang="en"><body><img src="x.png" alt=""></body></html>')
        self.assertEqual(r["gate"], "PASS")

    def test_role_presentation_passes(self):
        r = AL.lint_html('<html lang="en"><body><img src="x.png" role="presentation"></body></html>')
        self.assertEqual(r["gate"], "PASS")

    def test_aria_hidden_passes(self):
        r = AL.lint_html('<html lang="en"><body><img src="x.png" aria-hidden="true"></body></html>')
        self.assertEqual(r["gate"], "PASS")


class TestHtmlLang(unittest.TestCase):
    def test_missing_lang_fails(self):
        r = AL.lint_html("<html><body><p>hi</p></body></html>")
        self.assertEqual(r["gate"], "FAIL")
        self.assertIn("html-lang", _rules(r, blocking_only=True))

    def test_empty_lang_fails(self):
        r = AL.lint_html('<html lang=""><body><p>hi</p></body></html>')
        self.assertEqual(r["gate"], "FAIL")
        self.assertIn("html-lang", _rules(r, blocking_only=True))

    def test_present_lang_passes(self):
        r = AL.lint_html('<html lang="en"><body><p>hi</p></body></html>')
        self.assertEqual(r["gate"], "PASS")


class TestLinks(unittest.TestCase):
    def test_empty_link_fails(self):
        r = AL.lint_html('<html lang="en"><body><a href="/x"></a></body></html>')
        self.assertEqual(r["gate"], "FAIL")
        self.assertIn("link-name", _rules(r, blocking_only=True))

    def test_text_link_passes(self):
        r = AL.lint_html('<html lang="en"><body><a href="/x">Go</a></body></html>')
        self.assertEqual(r["gate"], "PASS")

    def test_aria_label_link_passes(self):
        r = AL.lint_html('<html lang="en"><body><a href="/x" aria-label="Go"></a></body></html>')
        self.assertEqual(r["gate"], "PASS")

    def test_img_alt_child_names_link(self):
        r = AL.lint_html('<html lang="en"><body><a href="/x"><img src="i" alt="Home"></a></body></html>')
        self.assertEqual(r["gate"], "PASS")

    def test_anchor_without_href_is_not_a_link(self):
        r = AL.lint_html('<html lang="en"><body><a></a></body></html>')
        self.assertEqual(r["gate"], "PASS")


class TestButtons(unittest.TestCase):
    def test_empty_button_fails(self):
        r = AL.lint_html('<html lang="en"><body><button></button></body></html>')
        self.assertEqual(r["gate"], "FAIL")
        self.assertIn("button-name", _rules(r, blocking_only=True))

    def test_text_button_passes(self):
        r = AL.lint_html('<html lang="en"><body><button>Save</button></body></html>')
        self.assertEqual(r["gate"], "PASS")

    def test_input_button_needs_value(self):
        bad = AL.lint_html('<html lang="en"><body><input type="submit"></body></html>')
        self.assertEqual(bad["gate"], "FAIL")
        good = AL.lint_html('<html lang="en"><body><input type="submit" value="Go"></body></html>')
        self.assertEqual(good["gate"], "PASS")


class TestFormControls(unittest.TestCase):
    def test_unlabeled_input_fails(self):
        r = AL.lint_html('<html lang="en"><body><input type="text" id="q"></body></html>')
        self.assertEqual(r["gate"], "FAIL")
        self.assertIn("control-label", _rules(r, blocking_only=True))

    def test_label_for_passes(self):
        r = AL.lint_html(
            '<html lang="en"><body><label for="q">Search</label>'
            '<input type="text" id="q"></body></html>'
        )
        self.assertEqual(r["gate"], "PASS")

    def test_wrapping_label_passes(self):
        r = AL.lint_html(
            '<html lang="en"><body><label>Search <input type="text"></label></body></html>'
        )
        self.assertEqual(r["gate"], "PASS")

    def test_aria_label_passes(self):
        r = AL.lint_html('<html lang="en"><body><input type="text" aria-label="Search"></body></html>')
        self.assertEqual(r["gate"], "PASS")

    def test_hidden_input_needs_no_label(self):
        r = AL.lint_html('<html lang="en"><body><input type="hidden" name="t"></body></html>')
        self.assertEqual(r["gate"], "PASS")


class TestTables(unittest.TestCase):
    def test_data_table_without_th_fails(self):
        r = AL.lint_html(
            '<html lang="en"><body><table><tr><td>1</td><td>2</td></tr></table></body></html>'
        )
        self.assertEqual(r["gate"], "FAIL")
        self.assertIn("table-headers", _rules(r, blocking_only=True))

    def test_th_without_scope_is_advisory_not_blocking(self):
        r = AL.lint_html(
            '<html lang="en"><body><table><tr><th>H</th></tr>'
            '<tr><td>1</td></tr></table></body></html>'
        )
        self.assertEqual(r["gate"], "PASS")  # advisory only, not blocking
        self.assertIn("th-scope", _rules(r))
        self.assertNotIn("th-scope", _rules(r, blocking_only=True))

    def test_th_with_scope_no_advisory(self):
        r = AL.lint_html(
            '<html lang="en"><body><table><tr><th scope="col">H</th></tr>'
            '<tr><td>1</td></tr></table></body></html>'
        )
        self.assertEqual(r["gate"], "PASS")
        self.assertNotIn("th-scope", _rules(r))


class TestHeadingOrder(unittest.TestCase):
    def test_skipped_level_is_advisory(self):
        r = AL.lint_html('<html lang="en"><body><h1>A</h1><h3>B</h3></body></html>')
        self.assertEqual(r["gate"], "PASS")  # advisory, non-blocking
        self.assertIn("heading-order", _rules(r))

    def test_ordered_headings_pass(self):
        r = AL.lint_html('<html lang="en"><body><h1>A</h1><h2>B</h2><h3>C</h3></body></html>')
        self.assertEqual(r["gate"], "PASS")
        self.assertNotIn("heading-order", _rules(r))


class TestCLI(unittest.TestCase):
    def _run(self, html_text):
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as fh:
            fh.write(html_text)
            path = fh.name
        try:
            return subprocess.run(
                [sys.executable, str(SCRIPT), "--html", path, "--format", "json"],
                capture_output=True, text=True, timeout=30,
            )
        finally:
            Path(path).unlink()

    def test_cli_clean_exit_0(self):
        proc = self._run('<html lang="en"><body><img src="i" alt="x"></body></html>')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["gate"], "PASS")

    def test_cli_d3_exit_1(self):
        bad_html, _ = SEED.inject_D3(SAMPLE.read_text(encoding="utf-8"))
        proc = self._run(bad_html)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["gate"], "FAIL")

    def test_cli_missing_file_exit_2(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--html", "definitely-not-a-real-file.html"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 2)

    def test_cli_traversal_rejected_exit_2(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--html", "../../../../etc/passwd"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 2)

    def test_cli_version(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--version"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), AL.GATE_VERSION)


if __name__ == "__main__":
    unittest.main()
