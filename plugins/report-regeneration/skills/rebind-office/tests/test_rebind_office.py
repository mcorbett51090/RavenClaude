#!/usr/bin/env python3
"""
Unit + integration tests for rebind_office.py (the `rebind-office` skill, report-regeneration
pipeline stage 3, Office lane).

Covers the required contract against the real Office corpus fixture
(tests/fixtures/report-regeneration/sample-report.docx):
  - frozen OPC parts are byte-identical between template and output (everything except the
    one edited part word/document.xml + any regenerated media), and [Content_Types].xml is
    intact;
  - a frozen NODE inside document.xml is byte-identical (its outer OOXML span did not move);
  - a surgical value is replaced and the OLD value is absent from that run (and the document);
  - the output is a VALID docx: re-openable via zipfile + xml.etree, document.xml well-formed;
  - regenerate text (strip-then-write) reflects new data, old value gone;
  - regenerate raster replaces the embedded media binary (old bytes gone, fresh bytes in);
  - needs-review nodes are left untouched but visibly marked + logged;
  - the CLI is path-guarded, exit-coded, and never mutates the template file on disk.

Stdlib-only (unittest, base64, binascii, hashlib, io, json, struct, subprocess, tempfile,
zipfile, xml.etree). Runnable directly (`python3 test_rebind_office.py`) or via pytest —
neither is required.

Run from repo root:
    python3 plugins/report-regeneration/skills/rebind-office/tests/test_rebind_office.py
"""
from __future__ import annotations

import base64
import binascii
import copy
import hashlib
import io
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT = SKILL_DIR / "rebind_office.py"
SCRIPTS_DIR = REPO_ROOT / "plugins" / "report-regeneration" / "scripts"
SAMPLE_DOCX_PATH = REPO_ROOT / "tests" / "fixtures" / "report-regeneration" / "sample-report.docx"

for _p in (SKILL_DIR, SCRIPTS_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import rebind_office as ro  # noqa: E402
import rr_anchor  # noqa: E402

# ── a fresh 1x1 GREEN png (distinct from the fixture's red one) for the raster regenerate ──


def _png_1x1_green() -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", binascii.crc32(body) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    raw = b"\x00\x00\xff\x00"  # filter byte + RGB (0,255,0)
    idat = zlib.compress(raw, 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


FRESH_PNG = _png_1x1_green()

# Old (template) values that must not survive their edited nodes.
OLD_REVENUE = "$1,284,500"
OLD_INTRO = "Total bookings for the quarter reached "


def _manifest() -> dict:
    """A hand-built Office manifest over the fixture — one binding of every class, matching the
    anchors infer-office emits (verified against the fixture)."""
    return {
        "manifest_version": "1.0.0",
        "rsg_schema_version": "1.0.0",
        "template_id": "sample-report",
        "format": "office",
        "bindings": [
            {
                "node_id": "b-exec-heading",
                "anchor": {"kind": "ooxml_path", "value": "body/p[2]/r[1]"},
                "class": "frozen",
                "confidence": 0.99,
                "provenance": {"source": "n/a", "source_period": None},
                "data_query": None,
            },
            {
                "node_id": "bookmark(revenue_total)",
                "anchor": {"kind": "ooxml_path", "value": "bookmark(revenue_total)"},
                "class": "surgical",
                "confidence": 0.97,
                "provenance": {"source": "new-erp", "source_period": "Q3 2025", "method": "native-parse"},
                "data_query": {"kind": "literal-from-new-source", "expression": "revenue.total", "source_ref": "new-erp"},
            },
            {
                "node_id": "b-intro",
                "anchor": {"kind": "ooxml_path", "value": "body/p[3]/r[1]"},
                "class": "regenerate",
                "confidence": 0.8,
                "provenance": {"source": "new-erp", "source_period": "Q3 2025"},
                "data_query": {"kind": "literal-from-new-source", "expression": "templates.intro"},
            },
            {
                "node_id": "b-pct",
                "anchor": {"kind": "ooxml_path", "value": "body/p[3]/r[4]"},
                "class": "needs-review",
                "confidence": 0.6,
                "provenance": {"source": "n/a", "source_period": None},
                "data_query": {"kind": "none", "expression": "unmarked-percent-literal"},
            },
            {
                "node_id": "b-chart",
                "anchor": {"kind": "ooxml_path", "value": "body/p[6]/r[1]/drawing[1]"},
                "class": "regenerate",
                "confidence": 0.9,
                "provenance": {"source": "chart-engine", "source_period": "Q3 2025", "pbi_route": "screenshot"},
                "data_query": {"kind": "screenshot-capture", "expression": "assets.chart"},
            },
        ],
    }


def _new_data() -> dict:
    return {
        "revenue": {"total": "$3,120,900"},
        "templates": {"intro": "Bookings this period totalled "},
        "assets": {"chart": {"media_base64": base64.b64encode(FRESH_PNG).decode("ascii")}},
    }


def _outer_bytes(document_xml: bytes, anchor: str) -> bytes:
    return rr_anchor.ooxml_resolve(document_xml, anchor).outer_bytes()


def _node_text(document_xml: bytes, anchor: str) -> str:
    return rr_anchor.ooxml_resolve(document_xml, anchor).text()


class TestRebindOffice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SAMPLE_DOCX_PATH.is_file():
            raise unittest.SkipTest(f"corpus fixture not found: {SAMPLE_DOCX_PATH}")
        cls.template_bytes = SAMPLE_DOCX_PATH.read_bytes()
        cls.template_doc = ro.read_part(cls.template_bytes, ro.DOCUMENT_PART)
        cls.output_bytes, cls.changes, cls.nrc = ro.rebind(cls.template_bytes, _manifest(), _new_data())
        cls.output_doc = ro.read_part(cls.output_bytes, ro.DOCUMENT_PART)

    # ── frozen parts byte-identical template <-> output ──

    def test_untouched_opc_parts_are_byte_identical(self):
        regenerated_media = {"word/media/image1.png"}
        with zipfile.ZipFile(io.BytesIO(self.template_bytes)) as tzf, zipfile.ZipFile(
            io.BytesIO(self.output_bytes)
        ) as ozf:
            template_names = tzf.namelist()
            self.assertEqual(template_names, ozf.namelist(), "OPC member set/order must be preserved")
            for name in template_names:
                if name == ro.DOCUMENT_PART or name in regenerated_media:
                    continue
                self.assertEqual(
                    tzf.read(name), ozf.read(name), f"untouched OPC part changed: {name!r}"
                )

    def test_content_types_intact(self):
        with zipfile.ZipFile(io.BytesIO(self.template_bytes)) as tzf, zipfile.ZipFile(
            io.BytesIO(self.output_bytes)
        ) as ozf:
            self.assertIn(ro.CONTENT_TYPES_PART, ozf.namelist())
            self.assertEqual(tzf.read(ro.CONTENT_TYPES_PART), ozf.read(ro.CONTENT_TYPES_PART))

    def test_frozen_node_is_byte_identical(self):
        self.assertEqual(
            _outer_bytes(self.template_doc, "body/p[2]/r[1]"),
            _outer_bytes(self.output_doc, "body/p[2]/r[1]"),
        )
        self.assertEqual(_node_text(self.output_doc, "body/p[2]/r[1]"), "Executive Summary")

    def test_frozen_violation_is_caught(self):
        # A frozen node whose bytes DID move must raise — proves _assert_frozen_unchanged has teeth.
        mutated = self.template_doc.replace(b"Executive Summary", b"MUTATED HEADING")
        bindings = [b for b in _manifest()["bindings"] if b["class"] == "frozen"]
        with self.assertRaises(ro.RebindOfficeError):
            ro._assert_frozen_unchanged(self.template_doc, mutated, bindings)

    # ── surgical: value replaced, OLD value absent from that run (and the document) ──

    def test_surgical_replaces_value_and_old_value_absent(self):
        run_bytes = _outer_bytes(self.output_doc, "bookmark(revenue_total)")
        self.assertIn(b"$3,120,900", run_bytes)
        self.assertNotIn(OLD_REVENUE.encode("utf-8"), run_bytes)
        self.assertEqual(_node_text(self.output_doc, "bookmark(revenue_total)"), "$3,120,900")
        # zero-literal, document-wide: the old value survives nowhere in document.xml
        self.assertNotIn(OLD_REVENUE.encode("utf-8"), self.output_doc)

    def test_surgical_preserves_run_structure(self):
        # the edit targets w:t text only — the run element itself is intact and still resolves.
        node = rr_anchor.ooxml_resolve(self.output_doc, "bookmark(revenue_total)")
        self.assertEqual(node.local_name, "r")
        self.assertIn(b"<w:t", node.inner_bytes())

    def test_strip_then_write_is_a_genuine_two_step_zero_literal_construction(self):
        anchor = {"kind": "ooxml_path", "value": "bookmark(revenue_total)"}
        stripped, old = ro._strip_value(self.template_doc, anchor)
        self.assertEqual(old, OLD_REVENUE)
        # at the strip midpoint the node carries no old instance value, by construction
        self.assertNotIn(OLD_REVENUE.encode("utf-8"), _outer_bytes(stripped, "bookmark(revenue_total)"))
        written = ro._write_value(stripped, anchor, ro._xml_escape_text("$9,999,999"))
        self.assertEqual(_node_text(written, "bookmark(revenue_total)"), "$9,999,999")

    # ── regenerate ──

    def test_regenerate_text_reflects_new_data(self):
        run_bytes = _outer_bytes(self.output_doc, "body/p[3]/r[1]")
        self.assertIn(b"Bookings this period totalled", run_bytes)
        self.assertNotIn(OLD_INTRO.encode("utf-8"), run_bytes)
        self.assertNotIn(OLD_INTRO.encode("utf-8"), self.output_doc)

    def test_regenerate_raster_replaces_media_binary(self):
        with zipfile.ZipFile(io.BytesIO(self.template_bytes)) as tzf, zipfile.ZipFile(
            io.BytesIO(self.output_bytes)
        ) as ozf:
            old_media = tzf.read("word/media/image1.png")
            new_media = ozf.read("word/media/image1.png")
        self.assertEqual(new_media, FRESH_PNG, "raster must be replaced with the fresh capture")
        self.assertNotEqual(new_media, old_media, "the old raster binary must not survive")

    def test_regenerate_raster_refuses_transplant_without_fresh_capture(self):
        # a regenerate raster with no fresh capture in new-data is a loud error, never a transplant.
        with self.assertRaises(ro.RebindOfficeError):
            ro._fresh_media_bytes({"alt": "no media provided"})

    # ── needs-review: untouched content + visible marker + logged ──

    def test_needs_review_marks_visibly_and_leaves_content_untouched(self):
        self.assertEqual(self.nrc, 1)
        self.assertIn(ro.NEEDS_REVIEW_TOKEN.encode("utf-8"), self.output_doc)
        # the flagged run's own value is untouched
        self.assertEqual(_node_text(self.output_doc, "body/p[3]/r[4]"), "+8.5%")
        review_entries = [c for c in self.changes if c["class"] == "needs-review"]
        self.assertEqual(len(review_entries), 1)
        self.assertEqual(review_entries[0]["anchor"], "body/p[3]/r[4]")

    # ── the output is a VALID docx ──

    def test_output_is_a_valid_docx(self):
        with zipfile.ZipFile(io.BytesIO(self.output_bytes)) as ozf:
            self.assertIsNone(ozf.testzip(), "output zip has a corrupt member")
            names = ozf.namelist()
            self.assertIn(ro.DOCUMENT_PART, names)
            self.assertIn(ro.CONTENT_TYPES_PART, names)
            # document.xml re-parses under xml.etree (well-formed)
            ET.fromstring(ozf.read(ro.DOCUMENT_PART))
            # [Content_Types].xml re-parses too
            ET.fromstring(ozf.read(ro.CONTENT_TYPES_PART))

    def test_change_log_covers_every_class(self):
        classes = sorted(c["class"] for c in self.changes)
        self.assertEqual(classes, ["frozen", "needs-review", "regenerate", "regenerate", "surgical"])

    # ── manifest schema guards ──

    def test_load_manifest_rejects_non_office_format(self):
        bad = copy.deepcopy(_manifest())
        bad["format"] = "html"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "m.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ro.RebindOfficeError):
                ro.load_manifest(path)

    def test_load_manifest_rejects_non_ooxml_anchor(self):
        bad = copy.deepcopy(_manifest())
        bad["bindings"][0]["anchor"] = {"kind": "element_id", "value": "kpi-revenue"}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "m.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ro.RebindOfficeError):
                ro.load_manifest(path)

    def test_load_manifest_rejects_frozen_with_data_query(self):
        bad = copy.deepcopy(_manifest())
        bad["bindings"][0]["data_query"] = {"kind": "none", "expression": "x"}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "m.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ro.RebindOfficeError):
                ro.load_manifest(path)

    def test_xxe_dtd_is_rejected(self):
        hostile = (
            b'<?xml version="1.0"?>'
            b'<!DOCTYPE Relationships [<!ENTITY xxe "LEAK">]>'
            b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
        )
        with self.assertRaises(ro.RebindOfficeError):
            ro.parse_rels(hostile)


class TestCLI(unittest.TestCase):
    """Process-boundary tests: exit codes, path-guard, and the works-on-a-copy guarantee
    (the template .docx is never mutated on disk)."""

    def setUp(self):
        self.out_dir = REPO_ROOT / "tests" / "fixtures" / "report-regeneration" / "_out"
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir)

    @staticmethod
    def _rel(path: Path) -> str:
        return str(path.relative_to(REPO_ROOT))

    def _write_manifest_and_data(self):
        manifest_path = self.out_dir / "manifest.json"
        data_path = self.out_dir / "new-data.json"
        manifest_path.write_text(json.dumps(_manifest()), encoding="utf-8")
        data_path.write_text(json.dumps(_new_data()), encoding="utf-8")
        return manifest_path, data_path

    def test_cli_happy_path_writes_valid_docx_and_never_mutates_template(self):
        manifest_path, data_path = self._write_manifest_and_data()
        out_path = self.out_dir / "out.docx"
        before_hash = hashlib.sha256(SAMPLE_DOCX_PATH.read_bytes()).hexdigest()

        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--template", self._rel(SAMPLE_DOCX_PATH),
                "--manifest", self._rel(manifest_path),
                "--new-data", self._rel(data_path),
                "--out", self._rel(out_path),
            ],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["needs_review_count"], 1)
        self.assertTrue(out_path.is_file())

        with zipfile.ZipFile(out_path) as ozf:
            self.assertIsNone(ozf.testzip())
            ET.fromstring(ozf.read(ro.DOCUMENT_PART))
            self.assertIn(b"$3,120,900", ozf.read(ro.DOCUMENT_PART))
            self.assertNotIn(OLD_REVENUE.encode("utf-8"), ozf.read(ro.DOCUMENT_PART))

        after_hash = hashlib.sha256(SAMPLE_DOCX_PATH.read_bytes()).hexdigest()
        self.assertEqual(before_hash, after_hash, "the CLI must never mutate --template on disk")

    def test_cli_rejects_out_equal_to_template(self):
        manifest_path, data_path = self._write_manifest_and_data()
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--template", self._rel(SAMPLE_DOCX_PATH),
                "--manifest", self._rel(manifest_path),
                "--new-data", self._rel(data_path),
                "--out", self._rel(SAMPLE_DOCX_PATH),
            ],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)["ok"])

    def test_cli_rejects_path_traversal(self):
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--template", "../etc/passwd",
                "--manifest", "x.json",
                "--new-data", "y.json",
                "--out", "z.docx",
            ],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)["ok"])

    def test_cli_rejects_absolute_path(self):
        manifest_path, data_path = self._write_manifest_and_data()
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--template", str(SAMPLE_DOCX_PATH),  # absolute — must be rejected
                "--manifest", self._rel(manifest_path),
                "--new-data", self._rel(data_path),
                "--out", self._rel(self.out_dir / "out.docx"),
            ],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
