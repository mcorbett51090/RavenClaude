#!/usr/bin/env python3
"""
test_harness_office.py — TDD acceptance suite for the OFFICE (docx) lane of the report-fidelity
harness (harness.py), the Office analogue of test_harness.py. Uses hand-crafted docx
template/output pairs (built in-memory with stdlib `zipfile`, no python-docx / no Word) so every
leg's teeth are proven against a fully-controlled OOXML container.

Contract proven here (core-architecture-spec.md §5 leg matrix + §6 the DECODED-container leak
surface + §2.1 Office anchor grammar):
  1. FORMAT DETECTION — harness.py routes a `.docx` (by extension AND by `PK` magic) to the Office
     leg implementations; the HTML lane is unaffected.
  2. CLEAN OFFICE CONTROL PASSES every BLOCKING leg (V1/V2/V3/V4/V6/period-coherence); V5 is
     honestly not_captured (no soffice) so the gate is PARTIAL — never a fake PASS, never a FAIL.
  3. EACH LEG CATCHES ITS DEFECT over OOXML, attributed to the mapped leg:
       * V2  — a chrome edit OUTSIDE a bound anchor (a frozen document.xml run / a frozen OPC part).
       * V4  — an embedded-xlsx data-cache leak AND a docProps Author (identity) leak — the big one.
       * V6  — a dataset value carried in an unbound/frozen region (silent staleness).
       * period-coherence — a stale reporting-period label.
       * V1  — a wrong value at a bound OOXML anchor.
  4. MUST-FAIL HALVES PROVE THE DISABLE KNOB CAN'T GREEN-LIGHT A DEFECT — disabling a blocking leg
     (V2/V4/V6/period-coherence) via the test-only --disable-leg mutant knob never reports a fake
     "pass": the neutered leg reports verdict "disabled", and because each of these legs is
     BLOCKING, harness.compute_gate forces the overall gate to FAIL. Per-leg attribution is proven
     separately by the positive catches-tests in each section.
  5. RECEIPTS ARE SCHEMA-VALID (format:"office") and the ML-free legs are labeled
     inference_independent; PROBE_ERROR (a malformed document.xml) is never a pass.

Stdlib-only, Python 3.9.6-safe. Runnable directly (`python3 test_harness_office.py`) or under pytest.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
import zipfile
from pathlib import Path

# The --disable-leg mutant knob is a TEST-ONLY footgun (harness.py P1 #5): honored only under this
# env flag, so a neutered leg can never silently green-light a production run. This suite's
# must-fail-half tests are the sanctioned use of that footgun — they deliberately disable a leg to
# prove the knob itself can't be used to fake a "pass".
os.environ.setdefault("RR_HARNESS_ENABLE_DISABLE_LEG", "1")

_SKILL_DIR = Path(__file__).resolve().parent.parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


harness = _load("harness_office_under_test", _SKILL_DIR / "harness.py")

_TMP = Path(tempfile.mkdtemp(prefix="fidelity-office-tests-"))
_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# ── OOXML fragment builders ────────────────────────────────────────────────────

def _run(text: str) -> str:
    return '<w:r><w:t xml:space="preserve">' + text + "</w:t></w:r>"


def _heading(text: str, style: str) -> str:
    return (
        "<w:p><w:pPr><w:pStyle w:val=\"" + style + "\"/></w:pPr>"
        + _run(text) + "</w:p>"
    )


def _para(*runs: str) -> str:
    return "<w:p>" + "".join(runs) + "</w:p>"


def _bookmarked_value_para(value: str, percent: str) -> str:
    """The surgical-KPI archetype: a w:bookmarkStart name='revenue_total' opening on the value run."""
    return (
        "<w:p>"
        + _run("Total bookings reached ")
        + '<w:bookmarkStart w:id="1" w:name="revenue_total"/>'
        + _run(value)
        + '<w:bookmarkEnd w:id="1"/>'
        + _run(", up ")
        + _run(percent)
        + _run(" year over year.")
        + "</w:p>"
    )


def _sect() -> str:
    return '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/></w:sectPr>'


def _document(body_inner: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:document xmlns:w="' + _W + '"><w:body>' + body_inner + _sect() + "</w:body></w:document>"
    )


def _core_xml(creator: str, title: str, last_mod: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<cp:coreProperties '
        'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/">'
        "<dc:title>" + title + "</dc:title>"
        "<dc:creator>" + creator + "</dc:creator>"
        "<cp:lastModifiedBy>" + last_mod + "</cp:lastModifiedBy>"
        "</cp:coreProperties>"
    )


def _app_xml(company: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
        "<Company>" + company + "</Company></Properties>"
    )


_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    "</Types>"
)
_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    "</Relationships>"
)
_DOC_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
)


def _zip_bytes(parts: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in parts.items():
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            zf.writestr(info, data if isinstance(data, bytes) else data.encode("utf-8"))
    return buf.getvalue()


def _make_docx(body_inner: str, *, creator: str = "", title: str = "", last_mod: str = "",
               company: str = "", styles: str = "<w:styles/>", extra_parts=None) -> bytes:
    parts = {
        "[Content_Types].xml": _CONTENT_TYPES,
        "_rels/.rels": _RELS,
        "docProps/core.xml": _core_xml(creator, title, last_mod),
        "docProps/app.xml": _app_xml(company),
        "word/document.xml": _document(body_inner),
        "word/styles.xml": styles,
        "word/_rels/document.xml.rels": _DOC_RELS,
    }
    if extra_parts:
        parts.update(extra_parts)
    return _zip_bytes(parts)


def _make_xlsx(numbers) -> bytes:
    """A minimal embedded-cache xlsx (a nested OPC zip) whose sheet stores RAW figures — exactly how
    an embedded chart-data cache carries the client's old dataset."""
    sheet = (
        '<?xml version="1.0"?>\n<worksheet><sheetData>'
        + "".join(f"<row><c><v>{n}</v></c></row>" for n in numbers)
        + "</sheetData></worksheet>"
    )
    return _zip_bytes({
        "[Content_Types].xml": '<?xml version="1.0"?>\n<Types/>',
        "xl/worksheets/sheet1.xml": sheet,
    })


# ── canonical fixtures ─────────────────────────────────────────────────────────

def _template_body(period_title: str = "Q2 2025", value: str = "$1,284,500") -> str:
    return (
        _heading("Northwind Traders — " + period_title + " Report", "Title")
        + _heading("Executive Summary", "Heading1")
        + _bookmarked_value_para(value, "+8.5%")
        + _para(_run("Founded in 2011; headquartered in Portland."))
    )


_OLD_AUTHOR = "Ridgeline Capital LLC"
_OLD_COMPANY = "Ridgeline Capital"
_OLD_CACHE_FIGURE = "9876543"  # an OLD-client figure that does NOT appear in the new body


def _manifest(bindings) -> dict:
    return {
        "manifest_version": "1.0.0", "rsg_schema_version": "1.0.0",
        "template_id": "northwind-q2-2025", "format": "office", "bindings": bindings,
    }


def _bind(anchor_value, cls, expr=None, source_period="2025-Q2", node_id=None):
    b = {
        "node_id": node_id or anchor_value,
        "anchor": {"kind": "ooxml_path", "value": anchor_value},
        "class": cls, "confidence": 0.95,
        "provenance": {"source": "nw", "source_period": source_period,
                       "method": "rule-based", "pbi_route": None},
        "data_query": None,
    }
    if cls != "frozen":
        b["data_query"] = {
            "kind": "file-cell", "expression": expr or "revenue.total", "source_ref": "nw",
        }
    return b


def _clean_manifest() -> dict:
    return _manifest([_bind("bookmark(revenue_total)", "surgical", "revenue.total")])


def _new_data(period="2025-Q2", total="$1,284,500", extra=None) -> dict:
    values = {"revenue.total": {"value": total, "type": "currency", "period": period}}
    if extra:
        values.update(extra)
    return {"dataset_id": "nw", "period": period, "values": values}


def _write(name: str, data: bytes) -> str:
    p = _TMP / name
    p.write_bytes(data)
    return str(p)


_TEMPLATE_DOCX = _write(
    "template.docx",
    _make_docx(_template_body(), creator=_OLD_AUTHOR, title="Northwind Q2 2025",
               last_mod=_OLD_AUTHOR, company=_OLD_COMPANY),
)
# the clean output: same body + metadata SCRUBBED (creator/company/lastModifiedBy emptied) — the
# §6.6 pre-emit metadata scrub. document.xml is byte-identical (a same-period refresh).
_CLEAN_OUTPUT_DOCX = _write(
    "clean-output.docx",
    _make_docx(_template_body(), creator="", title="", last_mod="", company=""),
)


def _run_office(output_docx: str, manifest: dict, new_data: dict, *, taint=None, disabled=(),
                template_docx: str = _TEMPLATE_DOCX) -> dict:
    mp = _TMP / "manifest.json"
    mp.write_text(json.dumps(manifest), encoding="utf-8")
    nd = _TMP / "new-data.json"
    nd.write_text(json.dumps(new_data), encoding="utf-8")
    return harness.run_harness(
        template_docx, output_docx, str(mp), str(nd), taint=taint, disabled_legs=disabled
    )


def _legs(receipt: dict) -> dict:
    return {leg["leg"]: leg for leg in receipt["legs"]}


# ── 1. format detection ────────────────────────────────────────────────────────

def test_format_detected_by_extension_and_magic():
    assert harness._detect_format(_TEMPLATE_DOCX) == "office"
    # magic: a docx written to a non-.docx path is still detected as office by the PK zip header.
    magicless = _write("no-extension-blob", _make_docx(_template_body()))
    assert harness._detect_format(magicless) == "office"
    receipt = _run_office(_CLEAN_OUTPUT_DOCX, _clean_manifest(), _new_data())
    assert receipt["format"] == "office"


def test_html_lane_still_detects_html():
    html_path = _write("probe.html", b"<!doctype html><html><body><p>hi</p></body></html>")
    assert harness._detect_format(html_path) == "html"


# ── 2. clean office control passes every blocking leg ──────────────────────────

def test_clean_office_control_passes_every_blocking_leg():
    receipt = _run_office(_CLEAN_OUTPUT_DOCX, _clean_manifest(), _new_data())
    legs = _legs(receipt)
    blocking = [lg for lg in receipt["legs"] if lg["blocking"]]
    assert blocking, "expected blocking legs"
    for lg in blocking:
        assert lg["verdict"] == "pass", (
            "clean office control: blocking leg {} did not pass: {}".format(lg["leg"], lg["evidence"])
        )
    assert legs["V5"]["verdict"] == "not_captured"
    assert receipt["overall_gate"] == "PARTIAL"
    assert receipt["manual_residue"], "clean office control must surface advisory residue"


def test_clean_office_receipt_is_schema_valid_and_ml_free_labeled():
    receipt = _run_office(_CLEAN_OUTPUT_DOCX, _clean_manifest(), _new_data())
    assert harness.validate_receipt(receipt) == []
    legs = _legs(receipt)
    for name in ("V2", "V4", "V6", "period-coherence"):
        assert legs[name]["inference_independent"] is True, name
    assert legs["V1"]["inference_independent"] is False
    assert legs["V3"]["inference_independent"] is False


# ── 3. V2 frozen-complement over OOXML ─────────────────────────────────────────

def test_v2_office_catches_frozen_document_run_edit():
    # edit a FROZEN heading run ("Executive Summary") — outside any bound anchor.
    bad_body = _template_body().replace("Executive Summary", "Executive Summary (EDITED)")
    bad = _write("v2-doc-edit.docx", _make_docx(bad_body, creator="", title="", last_mod="", company=""))
    legs = _legs(_run_office(bad, _clean_manifest(), _new_data()))
    assert legs["V2"]["verdict"] == "fail", legs["V2"]["evidence"]
    assert "document.xml changed outside bound anchors" in legs["V2"]["evidence"]


def test_v2_office_catches_frozen_part_edit():
    # edit a FROZEN OPC part (word/styles.xml) — the part-level frozen complement.
    bad = _write(
        "v2-part-edit.docx",
        _make_docx(_template_body(), creator="", title="", last_mod="", company="",
                   styles="<w:styles><w:docDefaults/></w:styles>"),
    )
    legs = _legs(_run_office(bad, _clean_manifest(), _new_data()))
    assert legs["V2"]["verdict"] == "fail", legs["V2"]["evidence"]
    assert "frozen OPC part" in legs["V2"]["evidence"]


def test_v2_office_passes_when_only_bound_anchor_changes():
    # change ONLY the bookmarked value run (a licensed rebind) — V2 must stay clean (the value run
    # is masked); V1 will separately flag the value mismatch, but V2 is a frozen-complement pass.
    rebound_body = _template_body(value="$2,750,000")
    rebound = _write("v2-rebind.docx",
                     _make_docx(rebound_body, creator="", title="", last_mod="", company=""))
    legs = _legs(_run_office(rebound, _clean_manifest(), _new_data()))
    assert legs["V2"]["verdict"] == "pass", legs["V2"]["evidence"]


def test_v2_office_must_fail_half_slips_when_disabled():
    # Disabling V2 (the test-only --disable-leg mutant knob) must never fake a "pass": the
    # neutered leg reports verdict "disabled", and because V2 is BLOCKING, compute_gate forces
    # the overall gate to FAIL. (Per-leg catching teeth is already proven above by
    # test_v2_office_catches_frozen_document_run_edit; this is the disable-knob safety check.)
    bad_body = _template_body().replace("Executive Summary", "Executive Summary (EDITED)")
    bad = _write("v2-teeth.docx", _make_docx(bad_body, creator="", title="", last_mod="", company=""))
    enabled = _run_office(bad, _clean_manifest(), _new_data())
    assert _legs(enabled)["V2"]["verdict"] == "fail"
    assert enabled["overall_gate"] == "FAIL"
    neutered = _run_office(bad, _clean_manifest(), _new_data(), disabled=("V2",))
    assert _legs(neutered)["V2"]["verdict"] == "disabled", (
        f"a neutered V2 must report 'disabled', never 'pass' (got {_legs(neutered)['V2']['verdict']!r})"
    )
    assert neutered["overall_gate"] == "FAIL", (
        f"disabling BLOCKING leg V2 must force the gate to FAIL, never green-light it "
        f"(got {neutered['overall_gate']!r})"
    )


# ── 4. V4 taint egress over the DECODED docx container — the big one ────────────

def test_v4_office_catches_docprops_author_leak():
    # output metadata NOT scrubbed — the old client's Author survives in docProps/core.xml.
    leaky = _write(
        "v4-docprops-leak.docx",
        _make_docx(_template_body(), creator=_OLD_AUTHOR, title="", last_mod=_OLD_AUTHOR, company=""),
    )
    legs = _legs(_run_office(leaky, _clean_manifest(), _new_data()))
    assert legs["V4"]["verdict"] == "fail", legs["V4"]["evidence"]
    assert "Ridgeline" in legs["V4"]["evidence"]
    # control: the scrubbed clean output passes V4.
    assert _legs(_run_office(_CLEAN_OUTPUT_DOCX, _clean_manifest(), _new_data()))["V4"]["verdict"] == "pass"


def test_v4_office_catches_old_client_literal_in_xml_comment():
    # P2 (round-3 security): ElementTree DROPS XML comments, so an old-client literal hidden in a
    # <!-- --> comment inside a WELL-FORMED document.xml (docProps scrubbed) would parse fine and be
    # silently dropped — the office-lane analogue of the round-1 HTML comment-leak P0. The raw-byte
    # backstop over each decoded part must still catch it and FAIL V4.
    body = ("<!-- old_author: " + _OLD_AUTHOR + " -->"
            + _para(_run("Refreshed report for the new period.")))
    leaky = _write("v4-xml-comment-leak.docx",
                   _make_docx(body, creator="", title="", last_mod="", company=""))  # docProps scrubbed
    legs = _legs(_run_office(leaky, _manifest([]), _new_data(), taint={"old_author": _OLD_AUTHOR}))
    assert legs["V4"]["verdict"] == "fail", (
        f"an old-client literal in an XML comment must FAIL V4 via the raw-byte backstop "
        f"(got {legs['V4']['verdict']!r}: {legs['V4'].get('evidence')})"
    )
    assert "Ridgeline" in legs["V4"]["evidence"]


def test_v4_office_scans_nonxml_text_parts_by_magic_byte():
    # P2 (round-4 security): the V4 Office scan surface must be MAGIC-BYTE-keyed, not extension-keyed.
    # A legacy VML textbox (.vml) that rezip copies through byte-for-byte renders visible text; an
    # old-client literal there must enter the V4 corpus, never dropped as "binary" by its extension.
    vml = (b"<v:shape><v:textbox><w:txbxContent><w:p><w:r><w:t>"
           + _OLD_AUTHOR.encode() + b"</w:t></w:r></w:p></w:txbxContent></v:textbox></v:shape>")
    corpus, _ = harness._decoded_container_office(
        harness.OfficeContainer({"word/vmlDrawing1.vml": vml}))
    assert _OLD_AUTHOR in corpus, "a .vml textbox literal must enter the V4 corpus (magic-byte scan)"
    # a genuine binary (PNG magic) is still NOT text-scanned — the documented local-execution limit.
    png = harness.OfficeContainer({"word/media/image1.png": b"\x89PNG\r\n\x1a\n" + _OLD_AUTHOR.encode()})
    assert _OLD_AUTHOR not in harness._decoded_container_office(png)[0], (
        "a magic-byte-recognized binary (PNG) must remain unscanned")
    # P1 (round-5): a UTF-16-encoded non-XML text part must ALSO be scanned (not utf-8-only decode).
    htm16 = ("<html><body>" + _OLD_AUTHOR + " $1,284,500</body></html>").encode("utf-16")
    corpus16, _ = harness._decoded_container_office(
        harness.OfficeContainer({"word/afchunk.htm": htm16}))
    assert _OLD_AUTHOR in corpus16, "a UTF-16 altChunk/VML text literal must enter the V4 corpus"
    # P1 (round-6): a literal in an XML COMMENT inside a UTF-16 OOXML part must ALSO be caught — the
    # comment raw-backstop must be encoding-agnostic like the non-XML branch (the round-3 x round-5 seam).
    doc16 = ("<w:document><w:body><!-- old_author: " + _OLD_AUTHOR
             + " --><w:p/></w:body></w:document>").encode("utf-16")
    corpus_c16, _ = harness._decoded_container_office(
        harness.OfficeContainer({"word/document.xml": doc16}))
    assert _OLD_AUTHOR in corpus_c16, "a UTF-16 XML-comment literal must enter the V4 corpus"


def test_v4_office_catches_embedded_xlsx_leak():
    # the OLD dataset survives as a raw figure in word/embeddings/oldData.xlsx (the chart-data cache)
    # — invisible to a document.xml-only scan, present in the DECODED container.
    taint = {"old_revenue_total": "$9,876,543", "old_author": _OLD_AUTHOR}
    leaky = _write(
        "v4-xlsx-leak.docx",
        _make_docx(_template_body(), creator="", title="", last_mod="", company="",
                   extra_parts={"word/embeddings/oldData.xlsx": _make_xlsx([_OLD_CACHE_FIGURE, "42"])}),
    )
    legs = _legs(_run_office(leaky, _clean_manifest(), _new_data(), taint=taint))
    assert legs["V4"]["verdict"] == "fail", legs["V4"]["evidence"]
    assert "old_revenue_total" in legs["V4"]["evidence"]
    # control: WITHOUT the embedded cache the same old figure appears nowhere -> V4 passes.
    clean = _write("v4-xlsx-clean.docx",
                   _make_docx(_template_body(), creator="", title="", last_mod="", company=""))
    assert _legs(_run_office(clean, _clean_manifest(), _new_data(), taint=taint))["V4"]["verdict"] == "pass"


def test_v4_office_must_fail_half_leak_slips_when_disabled():
    # Disabling V4 must never fake a "pass": the neutered leg reports 'disabled' and, since V4 is
    # BLOCKING, compute_gate forces the gate to FAIL.
    leaky = _write(
        "v4-teeth.docx",
        _make_docx(_template_body(), creator=_OLD_AUTHOR, title="", last_mod=_OLD_AUTHOR, company=""),
    )
    enabled = _run_office(leaky, _clean_manifest(), _new_data())
    assert _legs(enabled)["V4"]["verdict"] == "fail"
    assert enabled["overall_gate"] == "FAIL"
    neutered = _run_office(leaky, _clean_manifest(), _new_data(), disabled=("V4",))
    assert _legs(neutered)["V4"]["verdict"] == "disabled", (
        f"a neutered V4 must report 'disabled', never 'pass' (got {_legs(neutered)['V4']['verdict']!r})"
    )
    assert neutered["overall_gate"] == "FAIL", (
        f"disabling BLOCKING leg V4 must force the gate to FAIL, never green-light it "
        f"(got {neutered['overall_gate']!r})"
    )


# ── 5. V6 value-coverage over OOXML ────────────────────────────────────────────
# The $742,300 paragraph lives in BOTH template and output (identical structure), so V2/V3 stay
# clean and V6 is the SOLE catch — the frozen-misclassification a value-in-a-frozen-region is.
_V6_BODY = _template_body() + _para(_run("Regional total: $742,300."))
_V6_TEMPLATE = _write("v6-template.docx",
                      _make_docx(_V6_BODY, creator=_OLD_AUTHOR, title="", last_mod=_OLD_AUTHOR,
                                 company=_OLD_COMPANY))
_V6_OUTPUT = _write("v6-output.docx",
                    _make_docx(_V6_BODY, creator="", title="", last_mod="", company=""))
_V6_NEWDATA = _new_data(
    extra={"revenue.north": {"value": "$742,300", "type": "currency", "period": "2025-Q2"}}
)


def test_v6_office_catches_uncovered_dataset_value():
    legs = _legs(_run_office(_V6_OUTPUT, _clean_manifest(), _V6_NEWDATA, template_docx=_V6_TEMPLATE))
    assert legs["V6"]["verdict"] == "fail", legs["V6"]["evidence"]
    assert "coverage failure" in legs["V6"]["evidence"]
    # V2/V3 stay clean — the defect is a coverage/partition error, not a chrome/structure one.
    assert legs["V2"]["verdict"] == "pass"
    assert legs["V3"]["verdict"] == "pass"


def test_v6_office_passes_when_value_is_covered():
    # bind the paragraph run that carries $742,300 (body/p[5]/r[1]) so it is covered.
    manifest = _manifest([
        _bind("bookmark(revenue_total)", "surgical", "revenue.total"),
        _bind("body/p[5]/r[1]", "surgical", "revenue.north"),
    ])
    legs = _legs(_run_office(_V6_OUTPUT, manifest, _V6_NEWDATA, template_docx=_V6_TEMPLATE))
    assert legs["V6"]["verdict"] == "pass", legs["V6"]["evidence"]


def test_v6_office_must_fail_half_slips_when_disabled():
    # Disabling V6 must never fake a "pass": the neutered leg reports 'disabled' and, since V6 is
    # BLOCKING, compute_gate forces the gate to FAIL.
    enabled = _run_office(_V6_OUTPUT, _clean_manifest(), _V6_NEWDATA, template_docx=_V6_TEMPLATE)
    assert _legs(enabled)["V6"]["verdict"] == "fail"
    assert enabled["overall_gate"] == "FAIL"
    neutered = _run_office(_V6_OUTPUT, _clean_manifest(), _V6_NEWDATA, template_docx=_V6_TEMPLATE,
                           disabled=("V6",))
    assert _legs(neutered)["V6"]["verdict"] == "disabled", (
        f"a neutered V6 must report 'disabled', never 'pass' (got {_legs(neutered)['V6']['verdict']!r})"
    )
    assert neutered["overall_gate"] == "FAIL", (
        f"disabling BLOCKING leg V6 must force the gate to FAIL, never green-light it "
        f"(got {neutered['overall_gate']!r})"
    )


def test_v6_office_surfaces_run_split_nondomain_literal_as_advisory():
    # P2 (round-2 code-review, guarantee (b)): a data-shaped literal SPLIT across sibling runs in an
    # unbound/frozen paragraph must not ship silently, even when it is NOT a new-data-domain value.
    # "$9,900" as <w:t>$9</w:t>+<w:t>,900</w:t> is only whole when the runs are joined; leg_v6_office
    # must surface it as an advisory needs-review (mirroring the per-run else-advisory), never silent.
    body = _para(_run("Prior costs were "), _run("$9"), _run(",900"), _run(" last year."))
    leg, advisory = harness.leg_v6_office(_document(body).encode(), _manifest([]), _V6_NEWDATA)
    # $9,900 is not a new-data-domain value, so V6 stays 'pass' (not a blocking coverage failure)...
    assert leg["verdict"] == "pass", leg["evidence"]
    # ...but the run-split literal is surfaced (not silent) — the P2 fix's teeth.
    assert any("run-split" in a for a in advisory), (
        "a run-split data-shaped literal in a frozen paragraph must surface as advisory "
        f"needs-review, never silent (got advisory={advisory})"
    )


# ── 6. period-coherence over OOXML ─────────────────────────────────────────────
# A period label NOT rebound to the new quarter: template AND output both read "Q1 2025" (an
# unchanged label — so V2/V3 stay clean), while new-data has advanced to 2025-Q2. period-coherence
# is the SOLE catch of the stale-period label.
_STALE_BODY = _template_body(period_title="Q1 2025")
_STALE_TEMPLATE = _write("period-template.docx",
                         _make_docx(_STALE_BODY, creator=_OLD_AUTHOR, title="", last_mod=_OLD_AUTHOR,
                                    company=_OLD_COMPANY))
_STALE_OUTPUT = _write("period-output.docx",
                       _make_docx(_STALE_BODY, creator="", title="", last_mod="", company=""))


def test_period_coherence_office_catches_stale_label():
    legs = _legs(_run_office(_STALE_OUTPUT, _clean_manifest(), _new_data(period="2025-Q2"),
                             template_docx=_STALE_TEMPLATE))
    assert legs["period-coherence"]["verdict"] == "fail", legs["period-coherence"]["evidence"]
    assert "2025-Q1" in legs["period-coherence"]["evidence"]
    assert legs["V2"]["verdict"] == "pass"  # the label is unchanged vs template — not a V2 defect


def test_period_coherence_office_must_fail_half_slips_when_disabled():
    # Disabling period-coherence must never fake a "pass": the neutered leg reports 'disabled'
    # and, since period-coherence is BLOCKING, compute_gate forces the gate to FAIL.
    enabled = _run_office(_STALE_OUTPUT, _clean_manifest(), _new_data(period="2025-Q2"),
                          template_docx=_STALE_TEMPLATE)
    assert _legs(enabled)["period-coherence"]["verdict"] == "fail"
    assert enabled["overall_gate"] == "FAIL"
    neutered = _run_office(_STALE_OUTPUT, _clean_manifest(), _new_data(period="2025-Q2"),
                           template_docx=_STALE_TEMPLATE, disabled=("period-coherence",))
    assert _legs(neutered)["period-coherence"]["verdict"] == "disabled", (
        "a neutered period-coherence must report 'disabled', never 'pass' (got {!r})".format(
            _legs(neutered)["period-coherence"]["verdict"]
        )
    )
    assert neutered["overall_gate"] == "FAIL", (
        f"disabling BLOCKING leg period-coherence must force the gate to FAIL, never green-light "
        f"it (got {neutered['overall_gate']!r})"
    )


# ── 7. V1 value accuracy over OOXML ────────────────────────────────────────────

def test_v1_office_catches_wrong_value_at_anchor():
    # bookmark value run carries $2,750,000 but new-data recomputes $1,284,500.
    wrong = _write("v1-wrong.docx",
                   _make_docx(_template_body(value="$2,750,000"),
                              creator="", title="", last_mod="", company=""))
    legs = _legs(_run_office(wrong, _clean_manifest(), _new_data(total="$1,284,500")))
    assert legs["V1"]["verdict"] == "fail", legs["V1"]["evidence"]


# ── 8. PROBE_ERROR discipline — a malformed document.xml never reads as a pass ──

def test_office_malformed_document_xml_is_probe_error_not_pass():
    malformed = _zip_bytes({
        "[Content_Types].xml": _CONTENT_TYPES,
        "_rels/.rels": _RELS,
        "docProps/core.xml": _core_xml("", "", ""),
        "docProps/app.xml": _app_xml(""),
        "word/document.xml": '<?xml version="1.0"?>\n<w:document xmlns:w="' + _W
        + '"><w:body><w:p><w:r><w:t>unclosed',  # deliberately truncated
        "word/styles.xml": "<w:styles/>",
        "word/_rels/document.xml.rels": _DOC_RELS,
    })
    out = _write("malformed.docx", malformed)
    receipt = _run_office(out, _clean_manifest(), _new_data())
    legs = _legs(receipt)
    # the structural legs crash-guard to PROBE_ERROR (never pass); a blocking PROBE_ERROR => FAIL.
    assert any(lg["verdict"] == "PROBE_ERROR" for lg in receipt["legs"]), legs
    assert receipt["overall_gate"] == "FAIL"
    assert harness.validate_receipt(receipt) == []


def test_every_office_receipt_is_schema_valid():
    receipts = [
        _run_office(_CLEAN_OUTPUT_DOCX, _clean_manifest(), _new_data()),
        _run_office(_TEMPLATE_DOCX, _clean_manifest(), _new_data()),  # unscrubbed -> V4 fail
    ]
    for r in receipts:
        assert harness.validate_receipt(r) == [], r["overall_gate"]
        assert r["overall_gate"] in ("FAIL", "PARTIAL")


# ── standalone runner (no pytest required) ─────────────────────────────────────

def _main() -> int:
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print("PASS  " + name)
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {name}\n      {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"ERROR {name}\n      {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    import sys

    sys.exit(_main())
