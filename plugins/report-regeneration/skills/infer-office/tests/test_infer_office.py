#!/usr/bin/env python3
"""
test_infer_office.py — acceptance tests for the infer-office skill.

Asserts:
  * the synthetic sample-report.docx parses into an RSG (stdlib zipfile + xml.etree),
  * that RSG validates against knowledge/rsg.schema.json (format "office"),
  * the bookmarked currency run classifies `surgical` with the right anchor + source_period,
  * the earned-frozen demotion + the period-label surfacing both fire,
  * the raster/drawing construction rule forces `regenerate`,
  * numeric table cells surface as needs-review,
  * the data-shaped-literal detector is REUSED verbatim from the HTML lane,
  * the XXE / DTD guard rejects a hostile DOCTYPE,
  * the committed fixture is byte-reproducible from build_sample_docx.py,
  * the CLI (--in/--out) runs end-to-end and writes a schema-valid RSG, and rejects traversal.

Runs under pytest OR as a plain stdlib script (`python3 tests/test_infer_office.py`).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_DIR = os.path.dirname(_THIS_DIR)
if _SKILL_DIR not in sys.path:
    sys.path.insert(0, _SKILL_DIR)

import infer_office  # noqa: E402
import infer  # noqa: E402  (loaded transitively by infer_office; used here for the schema validator)

_REPO_ROOT = infer._repo_root()
_FIXTURE = os.path.join(_REPO_ROOT, "tests", "fixtures", "report-regeneration", "sample-report.docx")
_INFER_OFFICE_PY = os.path.join(_SKILL_DIR, "infer_office.py")
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "plugins", "report-regeneration", "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
import build_sample_docx  # noqa: E402


# ── helpers ───────────────────────────────────────────────────────────────────────────────────

def _index_nodes(node, out):
    out[node["id"]] = node
    for child in node.get("children", []):
        _index_nodes(child, out)
    return out


def _built_rsg():
    document_xml = infer_office.read_document_xml(_FIXTURE)  # exercises the stdlib zip read path
    rsg, stats = infer_office.build_rsg(document_xml, template_id="sample-report")
    return rsg, stats


# ── tests ───────────────────────────────────────────────────────────────────────────────────

def test_sample_docx_parses():
    rsg, stats = _built_rsg()
    assert rsg["format"] == "office"
    assert rsg["schema_version"] == infer_office.RSG_SCHEMA_VERSION
    assert rsg["template_id"] == "sample-report"
    assert stats["total_nodes"] > 20, "expected a non-trivial tree for the sample docx"
    # root is the w:body element, anchored "body".
    assert rsg["root"]["anchor"] == {"kind": "ooxml_path", "value": "body"}
    assert stats["accelerator"] in ("python-docx", None)


def test_rsg_validates_against_schema():
    rsg, _ = _built_rsg()
    errors = infer.validate_instance(rsg, infer.load_schema())
    assert errors == [], "RSG failed schema validation:\n  " + "\n  ".join(errors)


def test_every_anchor_is_ooxml_path():
    rsg, _ = _built_rsg()
    index = _index_nodes(rsg["root"], {})
    for node in index.values():
        assert node["anchor"]["kind"] == "ooxml_path", (
            "Office anchors must all be kind 'ooxml_path', got {}".format(node["anchor"])
        )


def test_bookmarked_currency_run_is_surgical():
    rsg, stats = _built_rsg()
    index = _index_nodes(rsg["root"], {})
    node = index["bookmark(revenue_total)"]
    assert node["class"] == "surgical", "a bookmark-governed data value is a surgical edit"
    assert node["role"] == "kpi-value"
    assert node["data_shaped_literal"] is True
    assert node["provenance"]["source_period"] == "Q2 2025"
    assert node["provenance"]["method"] == "rule-based"
    assert "revenue_total" in stats["bookmarks"]


def test_period_label_surfaces_and_propagates():
    rsg, _ = _built_rsg()
    index = _index_nodes(rsg["root"], {})
    # the Title run carries the reporting-period token "Q2 2025" -> period-label, surfaced for review.
    title_run = index["body/p[1]/r[1]"]
    assert title_run["role"] == "period-label"
    assert title_run["data_shaped_literal"] is True
    assert title_run["class"] == "needs-review", "a data-shaped period label is not earned-frozen"


def test_earned_frozen_demotion_and_unmarked_value():
    rsg, _ = _built_rsg()
    index = _index_nodes(rsg["root"], {})
    # the "+8.5%" run is data-shaped but carries NO bookmark bind -> surfaced as needs-review.
    pct = index["body/p[3]/r[4]"]
    assert pct["data_shaped_literal"] is True
    assert pct["class"] == "needs-review"
    # no node bearing a data-shaped literal is ever class 'frozen' (schema + classifier invariant).
    for node in index.values():
        if node["data_shaped_literal"]:
            assert node["class"] != "frozen", "earned-frozen violation on {}".format(node["id"])


def test_construction_rule_forces_drawing_regenerate():
    rsg, _ = _built_rsg()
    index = _index_nodes(rsg["root"], {})
    drawing = index["body/p[6]/r[1]/drawing[1]"]
    assert drawing["class"] == "regenerate", "a raster/drawing cannot be proven data-free"
    assert drawing["role"] in ("image", "chart")
    assert drawing["provenance"]["method"] == "native-parse"


def test_numeric_table_cells_surface():
    rsg, _ = _built_rsg()
    index = _index_nodes(rsg["root"], {})
    for anchor in ("body/tbl[1]/tr[2]/tc[2]/p[1]/r[1]", "body/tbl[1]/tr[3]/tc[2]/p[1]/r[1]"):
        cell_run = index[anchor]
        assert cell_run["data_shaped_literal"] is True, "a $-shaped cell must be data-shaped"
        assert cell_run["class"] == "needs-review", "an unmarked numeric cell must surface"


def test_detector_is_reused_from_html_lane():
    # infer-office reuses the HTML lane's deterministic detector verbatim (single source of truth).
    assert infer_office.infer.detect_data_shaped_literal is infer.detect_data_shaped_literal
    assert infer_office.infer.detect_data_shaped_literal("$1,284,500")["is_data_shaped"] is True
    assert infer_office.infer.detect_data_shaped_literal("Executive Summary")["is_data_shaped"] is False


def test_xxe_dtd_is_rejected():
    hostile = (
        b'<?xml version="1.0"?>'
        b'<!DOCTYPE w:document [<!ENTITY xxe "LEAK">]>'
        b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        b"<w:body><w:p><w:r><w:t>&xxe;</w:t></w:r></w:p></w:body></w:document>"
    )
    raised = False
    try:
        infer_office.build_rsg(hostile, template_id="hostile")
    except infer_office.OfficeInferError as exc:
        raised = True
        assert "XXE" in str(exc) or "DOCTYPE" in str(exc)
    assert raised, "a DOCTYPE/ENTITY in document.xml must be rejected (XXE defense)"


def test_fixture_is_byte_reproducible():
    # the committed .docx must be exactly what build_sample_docx.py emits (locks fixture<->generator).
    with open(_FIXTURE, "rb") as fh:
        committed = fh.read()
    assert committed == build_sample_docx.build_docx_bytes(), (
        "sample-report.docx has drifted from build_sample_docx.py — regenerate it"
    )


def test_cli_end_to_end():
    out_dir = os.path.join(_REPO_ROOT, "tests", "fixtures", "report-regeneration", "_out")
    out_path = os.path.join(out_dir, "rsg.office.cli-test.json")
    try:
        proc = subprocess.run(
            [sys.executable, _INFER_OFFICE_PY, "--in", _FIXTURE, "--out", out_path, "--format", "json"],
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
        assert summary["format"] == "office"
    finally:
        if os.path.isfile(out_path):
            os.remove(out_path)
        if os.path.isdir(out_dir) and not os.listdir(out_dir):
            os.rmdir(out_dir)


def test_cli_rejects_path_traversal():
    proc = subprocess.run(
        [sys.executable, _INFER_OFFICE_PY, "--in", "../../../etc/passwd", "--out", "x.json", "--format", "json"],
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
