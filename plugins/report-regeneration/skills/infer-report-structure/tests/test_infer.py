#!/usr/bin/env python3
"""
test_infer.py — acceptance tests for the infer-report-structure skill.

Asserts:
  * the sample report parses into an RSG,
  * that RSG validates against knowledge/rsg.schema.json,
  * every data-bind node in the corpus is found,
  * the deterministic data-shaped-literal detector flags the tricky cases (a year, a
    percent-shaped tagline) and rejects plain chrome,
  * the earned-frozen demotion + the raster construction rule both fire,
  * the companion new-data.sample.json fixture covers every binding,
  * the CLI (--in/--out) runs end-to-end and writes a schema-valid RSG.

Runs under pytest OR as a plain stdlib script (`python3 tests/test_infer.py`) — no third-party
test runner required (the plugin is stdlib-only on Python 3.9.6).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_DIR = os.path.dirname(_THIS_DIR)
if _SKILL_DIR not in sys.path:
    sys.path.insert(0, _SKILL_DIR)

import infer  # noqa: E402

_REPO_ROOT = infer._repo_root()
_FIXTURE = os.path.join(_REPO_ROOT, "tests", "fixtures", "report-regeneration", "sample-report.html")
_NEW_DATA = os.path.join(_REPO_ROOT, "tests", "fixtures", "report-regeneration", "new-data.sample.json")
_INFER_PY = os.path.join(_SKILL_DIR, "infer.py")


# ── helpers ───────────────────────────────────────────────────────────────────────────────────

def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _index_nodes(node, out):
    out[node["id"]] = node
    for child in node.get("children", []):
        _index_nodes(child, out)
    return out


def _built_rsg():
    html = _read(_FIXTURE)
    rsg, stats = infer.build_rsg(html, template_id="sample-report")
    return html, rsg, stats


def _html_binds(html):
    """(id, data-bind) pairs for every element carrying data-bind (all such elements have ids)."""
    pairs = []
    for tag in re.findall(r"<[a-zA-Z][^>]*\bdata-bind=\"[^\"]*\"[^>]*>", html):
        bind_m = re.search(r'data-bind="([^"]+)"', tag)
        id_m = re.search(r'\bid="([^"]+)"', tag)
        if bind_m and id_m:
            pairs.append((id_m.group(1), bind_m.group(1)))
    return pairs


# ── tests ───────────────────────────────────────────────────────────────────────────────────

def test_sample_report_parses():
    _, rsg, stats = _built_rsg()
    assert rsg["format"] == "html"
    assert rsg["schema_version"] == infer.RSG_SCHEMA_VERSION
    assert rsg["template_id"] == "sample-report"
    assert stats["total_nodes"] > 20, "expected a non-trivial tree for the sample report"
    # root is a single real element (the <html>), not the synthetic #document umbrella.
    assert rsg["root"]["anchor"]["value"] == "html"


def test_rsg_validates_against_schema():
    _, rsg, _ = _built_rsg()
    schema = infer.load_schema()
    errors = infer.validate_instance(rsg, schema)
    assert errors == [], "RSG failed schema validation:\n  " + "\n  ".join(errors)


def test_every_data_bind_node_is_found():
    html, rsg, stats = _built_rsg()
    index = _index_nodes(rsg["root"], {})
    pairs = _html_binds(html)
    assert pairs, "fixture drifted? no data-bind elements found in the corpus"

    html_binds = sorted({b for _, b in pairs})
    assert sorted(set(stats["data_binds"])) == html_binds, (
        "RSG data-binds do not match the corpus:\n"
        "  in RSG:  {}\n  in HTML: {}".format(sorted(set(stats["data_binds"])), html_binds)
    )

    for node_id, bind in pairs:
        assert node_id in index, f"data-bind node id={node_id!r} (bind {bind!r}) missing from the RSG"
        node = index[node_id]
        # every bound value in this corpus carries a data-shaped literal (currency/percent/date/period)
        assert node["data_shaped_literal"] is True, (
            f"bound node id={node_id!r} should carry a data-shaped literal"
        )


def test_detector_flags_the_tricky_cases():
    # a year (static Outlook citation) — the detector flags the SHAPE, not the meaning.
    year_case = infer.detect_data_shaped_literal(
        "Fiscal Year 2024 targets were exceeded, with total bookings reaching $18.2M"
    )
    assert year_case["is_data_shaped"] is True
    assert "year" in year_case["kinds"]

    # a percent-shaped marketing tagline (#tagline-text) — percent + founding year.
    tagline_case = infer.detect_data_shaped_literal(
        "100% Committed to Quality — Acme Widgets has proudly served customers since 1998."
    )
    assert tagline_case["is_data_shaped"] is True
    assert "percent" in tagline_case["kinds"]

    # currency / percent / date / period all detected
    assert infer.detect_data_shaped_literal("$4,821,300")["is_data_shaped"] is True
    assert infer.detect_data_shaped_literal("+12.4%")["is_data_shaped"] is True
    assert infer.detect_data_shaped_literal("April 4, 2025")["is_data_shaped"] is True
    assert infer.detect_data_shaped_literal("Q1 2025")["is_data_shaped"] is True

    # negative controls — plain chrome is NOT data-shaped
    assert infer.detect_data_shaped_literal("Executive Summary")["is_data_shaped"] is False
    assert infer.detect_data_shaped_literal("Skip to main content")["is_data_shaped"] is False
    assert infer.detect_data_shaped_literal("Revenue by Region")["is_data_shaped"] is False
    assert infer.detect_data_shaped_literal("")["is_data_shaped"] is False


def test_earned_frozen_demotion_fires():
    _, rsg, _ = _built_rsg()
    index = _index_nodes(rsg["root"], {})
    # #tagline-text is annotated data-role="frozen" but carries "100%"/"1998" -> force needs-review.
    tagline = index["tagline-text"]
    assert tagline["data_shaped_literal"] is True
    assert tagline["class"] == "needs-review", (
        "a data-shaped literal in a candidate-frozen node must force-demote to needs-review"
    )


def test_construction_rule_forces_rasters_to_regenerate():
    _, rsg, _ = _built_rsg()
    index = _index_nodes(rsg["root"], {})
    # rasters cannot be proven data-free -> forced regenerate, even the logo annotated frozen.
    for raster_id in ("logo-header", "pbi-screenshot", "chart-region-mix"):
        assert index[raster_id]["class"] == "regenerate", (
            f"raster id={raster_id!r} must be forced to regenerate (construction rule)"
        )


def test_pbi_route_is_recorded():
    _, rsg, _ = _built_rsg()
    index = _index_nodes(rsg["root"], {})
    xmla = index["xmla-figure-latest"]
    assert xmla["provenance"].get("pbi_route") == "xmla"
    assert xmla["provenance"]["source_period"] == "2025-Q1"
    screenshot = index["pbi-screenshot"]
    assert screenshot["provenance"].get("pbi_route") == "screenshot"


def test_new_data_fixture_covers_every_binding():
    html, _, _ = _built_rsg()
    assert os.path.isfile(_NEW_DATA), "companion new-data.sample.json fixture is missing"
    with open(_NEW_DATA, encoding="utf-8") as fh:
        new_data = json.load(fh)
    bindings = new_data.get("bindings", {})
    corpus_binds = {b for _, b in _html_binds(html)}
    missing = sorted(corpus_binds - set(bindings))
    assert not missing, f"new-data.sample.json is missing binding keys: {missing}"
    # every value is a non-empty display string
    for key, val in bindings.items():
        assert isinstance(val, str) and val.strip(), f"empty new-data value for {key!r}"


def test_cli_end_to_end():
    out_dir = os.path.join(_REPO_ROOT, "tests", "fixtures", "report-regeneration", "_out")
    out_path = os.path.join(out_dir, "rsg.cli-test.json")
    try:
        proc = subprocess.run(
            [sys.executable, _INFER_PY, "--in", _FIXTURE, "--out", out_path, "--format", "json"],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, f"CLI failed (exit {proc.returncode}):\n{proc.stderr}"
        assert os.path.isfile(out_path), "CLI did not write the RSG output file"
        with open(out_path, encoding="utf-8") as fh:
            rsg = json.load(fh)
        errors = infer.validate_instance(rsg, infer.load_schema())
        assert errors == [], "CLI-written RSG failed schema validation:\n  " + "\n  ".join(errors)
        summary = json.loads(proc.stdout)
        assert summary["ok"] is True
        assert summary["total_nodes"] == infer.build_rsg(_read(_FIXTURE), "sample-report")[1]["total_nodes"]
    finally:
        if os.path.isfile(out_path):
            os.remove(out_path)
        if os.path.isdir(out_dir) and not os.listdir(out_dir):
            os.rmdir(out_dir)


def test_cli_rejects_path_traversal():
    proc = subprocess.run(
        [sys.executable, _INFER_PY, "--in", "../../../etc/passwd", "--out", "x.json", "--format", "json"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2, "path traversal must be rejected with exit 2"
    err = json.loads(proc.stdout)
    assert err["ok"] is False


# ── plain-script harness (no pytest required) ─────────────────────────────────────────────────

def _run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = []
    for fn in tests:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as exc:
            failures.append((fn.__name__, str(exc)))
            print(f"  FAIL  {fn.__name__}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failures.append((fn.__name__, repr(exc)))
            print(f"  ERROR {fn.__name__}: {exc!r}")
    print(f"\n{len(tests) - len(failures)} passed, {len(failures)} failed (of {len(tests)})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_run_all())
