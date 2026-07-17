#!/usr/bin/env python3
"""
build_sample_docx.py — generate the synthetic Office (docx) fixture for report-regeneration.

Builds a minimal-but-VALID `.docx` (an OPC/ZIP package) entirely with the stdlib `zipfile`
module — no python-docx, no Word — at
`tests/fixtures/report-regeneration/sample-report.docx`. The document is the Office analogue of
`sample-report.html`: the synthetic "old" quarterly report used as a surgical-transplant TEMPLATE
for the Office lane (infer-office -> rebind-office -> the Office fidelity harness).

It contains, in document order inside `w:body`:
  * a Title paragraph (pStyle="Title") whose text carries the reporting-period label "Q2 2025",
  * two Heading1 section paragraphs ("Executive Summary", "Revenue by Region"),
  * a narrative paragraph with a **bookmarked** currency value run ($1,284,500) + a percent run,
  * a table with numeric ($-shaped) body cells,
  * a third Heading1 section + a paragraph holding an inline **image** (a stdlib-built 1x1 PNG),
  * the mandatory trailing `w:sectPr`.

Everything is FAKE data (fictional company "Northwind Traders"); no PII, no real client artifact.

The output is byte-deterministic (fixed zip member order + fixed 1980-01-01 timestamps + STORED
image, DEFLATE for xml) so the committed binary is reproducible from source.

Design constraints (binding, matches the plugin floor): stdlib only (zipfile, zlib, struct,
binascii, argparse, os, sys). Python 3.9.6-safe (`from __future__ import annotations`; no `X|Y`
unions, no `match`). No network. Path-guarded output.

Usage:
    python3 build_sample_docx.py            # writes the canonical fixture path
    python3 build_sample_docx.py --out <path.docx>
"""
from __future__ import annotations

import argparse
import binascii
import io
import os
import struct
import sys
import zipfile
import zlib

# ── OOXML namespace URIs (declared once on w:document) ────────────────────────────────────────
_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
_PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"


def _png_1x1() -> bytes:
    """A valid 1x1 opaque-red PNG, built from scratch (stdlib zlib/struct/binascii) so it is
    guaranteed well-formed rather than a hand-copied byte blob."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", binascii.crc32(body) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    # IHDR: width=1, height=1, bitdepth=8, colortype=2 (truecolor), compression=0, filter=0, interlace=0
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    # one scanline: filter byte 0 + RGB (255,0,0)
    raw = b"\x00\xff\x00\x00"
    idat = zlib.compress(raw, 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def _content_types_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        "</Types>"
    )


def _root_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        "</Relationships>"
    )


def _document_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId100" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>'
        "</Relationships>"
    )


def _core_props_xml() -> str:
    # Fake authorship metadata — the Office-lane V4 egress scan will later scrub docProps too.
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        "<dc:title>Northwind Traders — Q2 2025 Quarterly Report</dc:title>"
        "<dc:creator>A. Sample, Analyst</dc:creator>"
        "<cp:lastModifiedBy>A. Sample, Analyst</cp:lastModifiedBy>"
        '<dcterms:created xsi:type="dcterms:W3CDTF">2025-07-01T00:00:00Z</dcterms:created>'
        "</cp:coreProperties>"
    )


def _app_props_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
        "<Application>report-regeneration/build_sample_docx</Application><Company>Northwind Traders</Company>"
        "</Properties>"
    )


def _drawing_xml(rel_id: str) -> str:
    """A minimal, well-formed inline picture (DrawingML) referencing `rel_id` (an image relationship).
    Kept compact but structurally valid: wp:inline > extent/docPr/cNvGraphicFramePr/graphic > pic."""
    return (
        "<w:drawing>"
        '<wp:inline distT="0" distB="0" distL="0" distR="0">'
        '<wp:extent cx="990600" cy="495300"/>'
        '<wp:docPr id="1" name="Performance chart"/>'
        "<wp:cNvGraphicFramePr/>"
        '<a:graphic xmlns:a="' + _A + '">'
        '<a:graphicData uri="' + _PIC + '">'
        '<pic:pic xmlns:pic="' + _PIC + '">'
        "<pic:nvPicPr>"
        '<pic:cNvPr id="0" name="image1.png"/>'
        "<pic:cNvPicPr/>"
        "</pic:nvPicPr>"
        "<pic:blipFill>"
        '<a:blip r:embed="' + rel_id + '"/>'
        "<a:stretch><a:fillRect/></a:stretch>"
        "</pic:blipFill>"
        "<pic:spPr>"
        '<a:xfrm><a:off x="0" y="0"/><a:ext cx="990600" cy="495300"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        "</pic:spPr>"
        "</pic:pic>"
        "</a:graphicData>"
        "</a:graphic>"
        "</wp:inline>"
        "</w:drawing>"
    )


def _p_heading(text: str, style: str) -> str:
    return (
        "<w:p>"
        '<w:pPr><w:pStyle w:val="' + style + '"/></w:pPr>'
        "<w:r><w:t>" + text + "</w:t></w:r>"
        "</w:p>"
    )


def _run(text: str, preserve: bool = False) -> str:
    space = ' xml:space="preserve"' if preserve else ""
    return "<w:r><w:t" + space + ">" + text + "</w:t></w:r>"


def _tc(inner_runs: str) -> str:
    return (
        "<w:tc>"
        '<w:tcPr><w:tcW w:w="4675" w:type="dxa"/></w:tcPr>'
        "<w:p>" + inner_runs + "</w:p>"
        "</w:tc>"
    )


def _document_xml() -> str:
    # A bookmarked currency value inside the narrative paragraph — the surgical-KPI archetype.
    narrative = (
        "<w:p>"
        + _run("Total bookings for the quarter reached ", preserve=True)
        + '<w:bookmarkStart w:id="1" w:name="revenue_total"/>'
        + _run("$1,284,500")
        + '<w:bookmarkEnd w:id="1"/>'
        + _run(", up ", preserve=True)
        + _run("+8.5%")
        + _run(" year over year, the strongest print since 2019.", preserve=True)
        + "</w:p>"
    )
    table = (
        "<w:tbl>"
        "<w:tblPr>"
        '<w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/>'
        "</w:tblPr>"
        '<w:tblGrid><w:gridCol w:w="4675"/><w:gridCol w:w="4675"/></w:tblGrid>'
        "<w:tr>" + _tc(_run("Region")) + _tc(_run("Bookings")) + "</w:tr>"
        "<w:tr>" + _tc(_run("North")) + _tc(_run("$742,300")) + "</w:tr>"
        "<w:tr>" + _tc(_run("South")) + _tc(_run("$542,200")) + "</w:tr>"
        "</w:tbl>"
    )
    image_para = "<w:p><w:r>" + _drawing_xml("rId100") + "</w:r></w:p>"
    sect = (
        "<w:sectPr>"
        '<w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>'
        "</w:sectPr>"
    )
    body = (
        "<w:body>"
        + _p_heading("Northwind Traders — Q2 2025 Quarterly Report", "Title")
        + _p_heading("Executive Summary", "Heading1")
        + narrative
        + _p_heading("Revenue by Region", "Heading1")
        + table
        + _p_heading("Performance Snapshot", "Heading1")
        + image_para
        + sect
        + "</w:body>"
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:document xmlns:w="' + _W + '" xmlns:r="' + _R + '" xmlns:wp="' + _WP + '" '
        'xmlns:a="' + _A + '" xmlns:pic="' + _PIC + '">'
        + body
        + "</w:document>"
    )


def _members() -> list[tuple[str, bytes]]:
    """The OPC parts in a fixed order (deterministic archive)."""
    return [
        ("[Content_Types].xml", _content_types_xml().encode("utf-8")),
        ("_rels/.rels", _root_rels_xml().encode("utf-8")),
        ("docProps/core.xml", _core_props_xml().encode("utf-8")),
        ("docProps/app.xml", _app_props_xml().encode("utf-8")),
        ("word/document.xml", _document_xml().encode("utf-8")),
        ("word/_rels/document.xml.rels", _document_rels_xml().encode("utf-8")),
        ("word/media/image1.png", _png_1x1()),
    ]


def build_docx_bytes() -> bytes:
    """Return the full .docx as bytes (byte-deterministic)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in _members():
            # Fixed timestamp (1980-01-01) so the archive is reproducible run-to-run.
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            # STORE the PNG (already compressed); DEFLATE the XML text.
            if name.endswith(".png"):
                info.compress_type = zipfile.ZIP_STORED
            else:
                info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, data)
    return buf.getvalue()


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    root = here
    for _ in range(12):
        if os.path.isfile(os.path.join(root, ".repo-layout.json")) or os.path.isfile(
            os.path.join(root, "AGENTS.md")
        ):
            return root
        parent = os.path.dirname(root)
        if parent == root:
            break
        root = parent
    return os.path.abspath(os.path.join(here, "..", "..", ".."))


def _default_out() -> str:
    return os.path.join(
        _repo_root(), "tests", "fixtures", "report-regeneration", "sample-report.docx"
    )


def _safe_out(raw: str) -> str:
    if ".." in raw.replace("\\", "/").split("/"):
        raise SystemExit(f"[build-docx] error: output path contains a '..' component: {raw!r}")
    repo = os.path.realpath(_repo_root())
    resolved = os.path.realpath(os.path.join(os.getcwd(), raw))
    if resolved != repo and not resolved.startswith(repo + os.sep):
        raise SystemExit(f"[build-docx] error: output path escapes the repo root: {resolved!r}")
    return resolved


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="build_sample_docx.py", description="Build the synthetic Office (docx) fixture.")
    parser.add_argument("--out", dest="out", default=None, help="output .docx path (default: the canonical fixture path)")
    args = parser.parse_args(argv)

    out_abs = _safe_out(args.out) if args.out else _default_out()
    data = build_docx_bytes()
    out_dir = os.path.dirname(out_abs)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(out_abs, "wb") as fh:
        fh.write(data)
    print(f"[build-docx] wrote {len(data)} bytes -> {out_abs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
