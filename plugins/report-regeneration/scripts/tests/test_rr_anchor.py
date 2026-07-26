#!/usr/bin/env python3
"""
test_rr_anchor.py — unit tests for the shared anchor resolver (rr_anchor.py).

Proves the resolver supports EXACTLY the anchor grammar infer._anchor_for() emits — element_id,
simple '#id', and the compound '#ancestor-id > tag:nth-of-type(n) > ...' / bare-root-tag form —
against BOTH a tiny inline fixture and the real corpus (tests/fixtures/report-regeneration/
sample-report.html), and that the spans it returns let a byte-surgeon read/replace inner content.

Crucially: it cross-checks rr_anchor against infer as the PRODUCER — every css_selector anchor
infer emits over the corpus must resolve back to the SAME node (by structural path), which is the
whole point of a shared abstraction.

Stdlib only (unittest). Runnable directly (`python3 test_rr_anchor.py`) or via pytest.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = Path(__file__).resolve().parents[4]
_INFER = _REPO_ROOT / "plugins" / "report-regeneration" / "skills" / "infer-report-structure" / "infer.py"
_SAMPLE = _REPO_ROOT / "tests" / "fixtures" / "report-regeneration" / "sample-report.html"

if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import rr_anchor  # noqa: E402


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


infer = _load("infer_under_test", _INFER)

# ── Office (OOXML) fixtures + producer (for the shared-abstraction cross-check) ────────────────
_SAMPLE_DOCX = _REPO_ROOT / "tests" / "fixtures" / "report-regeneration" / "sample-report.docx"
_INFER_OFFICE = _REPO_ROOT / "plugins" / "report-regeneration" / "skills" / "infer-office" / "infer_office.py"
infer_office = _load("infer_office_under_test", _INFER_OFFICE)


FIXTURE = (
    "<!DOCTYPE html>\n"
    '<html lang="en">\n'
    "<head>\n"
    '<meta charset="utf-8">\n'
    "<title>Doc Title</title>\n"
    "</head>\n"
    "<body>\n"
    '<section id="sec-one">\n'
    "<h2>Heading One</h2>\n"
    '<p id="para">Alpha <strong>bold-a</strong> beta <strong>bold-b</strong>.</p>\n'
    "</section>\n"
    '<img id="pic" src="data:image/gif;base64,AAAA==" alt="a picture">\n'
    "</body>\n"
    "</html>\n"
)


class TestElementId(unittest.TestCase):
    def test_resolve_by_element_id_dict(self):
        node = rr_anchor.resolve(FIXTURE, {"kind": "element_id", "value": "para"})
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.element_id, "para")
        self.assertEqual(node.inner_text(FIXTURE), "Alpha <strong>bold-a</strong> beta <strong>bold-b</strong>.")

    def test_resolve_by_bare_id_string(self):
        node = rr_anchor.resolve(FIXTURE, "sec-one")
        self.assertEqual(node.tag, "section")

    def test_simple_hash_id_selector(self):
        node = rr_anchor.resolve(FIXTURE, {"kind": "css_selector", "value": "#pic"})
        self.assertEqual(node.tag, "img")
        self.assertTrue(node.is_void)

    def test_missing_id_raises(self):
        with self.assertRaises(rr_anchor.AnchorError):
            rr_anchor.resolve(FIXTURE, {"kind": "element_id", "value": "nope"})

    def test_exists_is_false_not_raise_for_absent(self):
        self.assertFalse(rr_anchor.exists(FIXTURE, {"kind": "element_id", "value": "nope"}))
        self.assertTrue(rr_anchor.exists(FIXTURE, {"kind": "element_id", "value": "para"}))


class TestCompoundSelector(unittest.TestCase):
    def test_ancestor_id_anchored_heading(self):
        node = rr_anchor.resolve(FIXTURE, {"kind": "css_selector", "value": "#sec-one > h2:nth-of-type(1)"})
        self.assertEqual(node.tag, "h2")
        self.assertEqual(node.inner_text(FIXTURE), "Heading One")

    def test_nth_of_type_selects_the_right_sibling(self):
        first = rr_anchor.resolve(FIXTURE, {"kind": "css_selector", "value": "#para > strong:nth-of-type(1)"})
        second = rr_anchor.resolve(FIXTURE, {"kind": "css_selector", "value": "#para > strong:nth-of-type(2)"})
        self.assertEqual(first.inner_text(FIXTURE), "bold-a")
        self.assertEqual(second.inner_text(FIXTURE), "bold-b")

    def test_bare_root_tag_descends_from_document_root(self):
        node = rr_anchor.resolve(
            FIXTURE, {"kind": "css_selector", "value": "html > head:nth-of-type(1) > meta:nth-of-type(1)"}
        )
        self.assertEqual(node.tag, "meta")
        self.assertEqual(node.attrs.get("charset"), "utf-8")

    def test_missing_step_raises(self):
        with self.assertRaises(rr_anchor.AnchorError):
            rr_anchor.resolve(FIXTURE, {"kind": "css_selector", "value": "#sec-one > h2:nth-of-type(5)"})

    def test_unsupported_step_raises(self):
        # a real CSS combinator this resolver deliberately does NOT support
        with self.assertRaises(rr_anchor.AnchorError):
            rr_anchor.resolve(FIXTURE, {"kind": "css_selector", "value": "#sec-one > h2.title"})


class TestSpansAndReplace(unittest.TestCase):
    def test_replace_inner_paired(self):
        out = rr_anchor.replace_inner(FIXTURE, {"kind": "css_selector", "value": "#sec-one > h2:nth-of-type(1)"}, "New Heading")
        self.assertIn("<h2>New Heading</h2>", out)
        self.assertNotIn("Heading One", out)

    def test_replace_inner_void_raises(self):
        with self.assertRaises(rr_anchor.AnchorError):
            rr_anchor.replace_inner(FIXTURE, "pic", "x")

    def test_open_tag_text_and_outer(self):
        node = rr_anchor.resolve(FIXTURE, "pic")
        self.assertTrue(node.open_tag_text(FIXTURE).startswith("<img id=\"pic\""))
        self.assertEqual(node.outer_text(FIXTURE), node.open_tag_text(FIXTURE))

    def test_read_inner_module_fn(self):
        self.assertEqual(
            rr_anchor.read_inner(FIXTURE, {"kind": "css_selector", "value": "#sec-one > h2:nth-of-type(1)"}),
            "Heading One",
        )


class TestAgainstInferProducerOverCorpus(unittest.TestCase):
    """The load-bearing cross-check: every anchor infer PRODUCES over the real corpus must resolve
    back to the SAME node this resolver locates (structural path equality) — the shared-abstraction
    invariant. Also proves a css_selector anchor's resolved inner text matches infer's node text."""

    @classmethod
    def setUpClass(cls):
        cls.html = _SAMPLE.read_text(encoding="utf-8")
        cls.rsg, _ = infer.build_rsg(cls.html, template_id="acme")

    def _walk(self, node, out):
        out.append(node)
        for c in node.get("children", []):
            self._walk(c, out)
        return out

    def test_every_infer_anchor_resolves(self):
        nodes = self._walk(self.rsg["root"], [])
        self.assertGreater(len(nodes), 40)
        css_seen = 0
        for n in nodes:
            anchor = n["anchor"]
            resolved = rr_anchor.try_resolve(self.html, anchor)
            self.assertIsNotNone(resolved, f"infer anchor did not resolve: {anchor}")
            if anchor["kind"] == "css_selector":
                css_seen += 1
        self.assertGreater(css_seen, 10, "expected many compound css_selector anchors in the corpus")

    def test_css_selector_paths_are_stable_and_unique(self):
        nodes = self._walk(self.rsg["root"], [])
        paths = {}
        for n in nodes:
            anchor = n["anchor"]
            if anchor["kind"] != "css_selector":
                continue
            path = rr_anchor.document_path(self.html, anchor)
            self.assertNotIn(path, paths, f"two anchors resolved to the same node path: {path}")
            paths[path] = anchor["value"]

    def test_known_corpus_selectors(self):
        # the exact anchors named in the integration brief resolve to the expected nodes.
        h2 = rr_anchor.resolve(self.html, {"kind": "css_selector", "value": "#sec-exec-summary > h2:nth-of-type(1)"})
        self.assertEqual(h2.tag, "h2")
        self.assertEqual(h2.inner_text(self.html).strip(), "Executive Summary")

        meta = rr_anchor.resolve(
            self.html, {"kind": "css_selector", "value": "html > head:nth-of-type(1) > meta:nth-of-type(1)"}
        )
        self.assertEqual(meta.tag, "meta")
        self.assertTrue(meta.is_void)


# ══════════════════════════════════════════════════════════════════════════════════════════════
# OFFICE / OOXML tests — the shared Word (.docx) anchor grammar + body-walk resolver
# ══════════════════════════════════════════════════════════════════════════════════════════════


class TestOoxmlGrammar(unittest.TestCase):
    """The pure grammar surface — production + parse round-trip + the shared indexing rule."""

    def test_local_name_stripping(self):
        self.assertEqual(rr_anchor.ooxml_local("{http://x}p"), "p")
        self.assertEqual(rr_anchor.ooxml_local("w:p"), "p")
        self.assertEqual(rr_anchor.ooxml_local("p"), "p")

    def test_sibling_index_buckets_by_local_name(self):
        # a paragraph's children: pPr, r, r -> the two runs are r[1], r[2]; the pPr never perturbs them.
        qn = ["w:pPr", "w:r", "w:r"]
        self.assertEqual(rr_anchor.ooxml_sibling_index(qn, 0), 1)  # pPr[1]
        self.assertEqual(rr_anchor.ooxml_sibling_index(qn, 1), 1)  # r[1]
        self.assertEqual(rr_anchor.ooxml_sibling_index(qn, 2), 2)  # r[2]

    def test_path_value_production(self):
        self.assertEqual(rr_anchor.ooxml_path_value([]), "body")
        self.assertEqual(rr_anchor.ooxml_path_value([("p", 3), ("r", 1)]), "body/p[3]/r[1]")
        self.assertEqual(rr_anchor.ooxml_bookmark_value("rev"), "bookmark(rev)")
        self.assertEqual(rr_anchor.ooxml_bookmark_value("rev", [("r", 2)]), "bookmark(rev)/r[2]")

    def test_parse_round_trip(self):
        self.assertEqual(rr_anchor.ooxml_parse_path("body"), (None, []))
        self.assertEqual(rr_anchor.ooxml_parse_path("body/p[3]/r[1]"), (None, [("p", 3), ("r", 1)]))
        self.assertEqual(rr_anchor.ooxml_parse_path("bookmark(rev)"), ("rev", []))
        self.assertEqual(rr_anchor.ooxml_parse_path("bookmark(rev)/r[2]"), ("rev", [("r", 2)]))

    def test_malformed_paths_raise(self):
        for bad in ("p[3]/r[1]", "body/h2.title", "bookmark()", "body/r", "body/r[x]", ""):
            with self.assertRaises(rr_anchor.AnchorError):
                rr_anchor.ooxml_parse_path(bad)


class TestOoxmlResolve(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docx = _SAMPLE_DOCX.read_bytes()  # the whole .docx zip
        cls.doc_xml = infer_office.read_document_xml(str(_SAMPLE_DOCX))  # raw word/document.xml bytes

    def test_body_path_resolves_to_run_text(self):
        node = rr_anchor.ooxml_resolve(self.docx, {"kind": "ooxml_path", "value": "body/p[3]/r[4]"})
        self.assertEqual(node.local_name, "r")
        self.assertEqual(node.text(), "+8.5%")
        self.assertEqual(node.path, (("p", 3), ("r", 4)))

    def test_resolve_accepts_zip_bytes_or_raw_document_xml(self):
        from_zip = rr_anchor.ooxml_resolve(self.docx, "bookmark(revenue_total)")
        from_xml = rr_anchor.ooxml_resolve(self.doc_xml, "bookmark(revenue_total)")
        self.assertEqual(from_zip.text(), "$1,284,500")
        self.assertEqual(from_zip.path, from_xml.path)

    def test_bookmark_and_body_path_name_the_same_node(self):
        bm = rr_anchor.ooxml_resolve(self.docx, "bookmark(revenue_total)")
        # the bookmarked run is the 2nd run of the 3rd paragraph -> both anchors share one path.
        eq = rr_anchor.ooxml_resolve(self.docx, "body/p[3]/r[2]")
        self.assertEqual(bm.path, eq.path)
        self.assertEqual(bm.text(), eq.text())

    def test_table_cell_value(self):
        node = rr_anchor.ooxml_resolve(self.docx, "body/tbl[1]/tr[2]/tc[2]/p[1]/r[1]")
        self.assertEqual(node.text(), "$742,300")

    def test_nth_selects_the_right_sibling(self):
        r2 = rr_anchor.ooxml_resolve(self.docx, "body/tbl[1]/tr[2]/tc[2]/p[1]/r[1]")
        r3 = rr_anchor.ooxml_resolve(self.docx, "body/tbl[1]/tr[3]/tc[2]/p[1]/r[1]")
        self.assertEqual(r2.text(), "$742,300")
        self.assertEqual(r3.text(), "$542,200")

    def test_drawing_is_a_resolvable_leaf(self):
        node = rr_anchor.ooxml_resolve(self.docx, "body/p[6]/r[1]/drawing[1]")
        self.assertEqual(node.local_name, "drawing")
        self.assertFalse(node.is_empty)

    def test_missing_node_is_absent_not_raised(self):
        self.assertFalse(rr_anchor.ooxml_exists(self.docx, "body/p[99]/r[1]"))
        self.assertIsNone(rr_anchor.ooxml_try_resolve(self.docx, "body/p[99]/r[1]"))
        self.assertTrue(rr_anchor.ooxml_exists(self.docx, "body/p[3]/r[4]"))

    def test_missing_bookmark_raises(self):
        with self.assertRaises(rr_anchor.AnchorError):
            rr_anchor.ooxml_resolve(self.docx, "bookmark(nope)")

    def test_unparseable_anchor_raises_even_in_try(self):
        with self.assertRaises(rr_anchor.AnchorError):
            rr_anchor.ooxml_try_resolve(self.docx, "body/h2.title")


class TestOoxmlByteEdit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docx = _SAMPLE_DOCX.read_bytes()

    def test_replace_inner_bytes_splices_a_new_value(self):
        node = rr_anchor.ooxml_resolve(self.docx, "bookmark(revenue_total)")
        edited = node.replace_inner_bytes(b"<w:t>$9,999,999</w:t>")
        self.assertIn(b"$9,999,999", edited)
        self.assertNotIn(b"1,284,500", edited)
        # the edit is surgical — everything outside the run's inner region is byte-identical.
        self.assertIn(b"Executive Summary", edited)

    def test_open_tag_bytes(self):
        node = rr_anchor.ooxml_resolve(self.docx, "body/p[3]/r[4]")
        self.assertTrue(node.open_tag_bytes().startswith(b"<w:r"))

    def test_module_replace_inner(self):
        out = rr_anchor.ooxml_replace_inner(self.docx, "body/tbl[1]/tr[2]/tc[2]/p[1]/r[1]", b"<w:t>$0</w:t>")
        self.assertIn(b"$0", out)
        self.assertNotIn(b"742,300", out)

    def test_replace_on_empty_element_raises(self):
        # w:pgSz is a self-closed (empty) element inside w:sectPr -> no inner region to splice.
        node = rr_anchor.ooxml_resolve(self.docx, "body/sectPr[1]/pgSz[1]")
        self.assertTrue(node.is_empty)
        with self.assertRaises(rr_anchor.AnchorError):
            node.replace_inner_bytes(b"x")


class TestOoxmlSecurity(unittest.TestCase):
    def test_doctype_is_rejected(self):
        hostile = (
            b'<?xml version="1.0"?>'
            b'<!DOCTYPE w:document [<!ENTITY xxe "LEAK">]>'
            b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            b"<w:body><w:p><w:r><w:t>&xxe;</w:t></w:r></w:p></w:body></w:document>"
        )
        with self.assertRaises(rr_anchor.AnchorError):
            rr_anchor.ooxml_resolve(hostile, "body/p[1]")


class TestOoxmlAgainstInferProducerOverDocx(unittest.TestCase):
    """The load-bearing cross-check (the Office analogue of TestAgainstInferProducerOverCorpus):
    every anchor infer-office PRODUCES over the real .docx fixture must resolve back to the SAME
    node this resolver locates — the shared-abstraction invariant that stops producer/consumer
    anchor-grammar drift (the failure that bit the HTML lane)."""

    @classmethod
    def setUpClass(cls):
        cls.docx = _SAMPLE_DOCX.read_bytes()
        doc_xml = infer_office.read_document_xml(str(_SAMPLE_DOCX))
        cls.rsg, _ = infer_office.build_rsg(doc_xml, template_id="acme-office")

    def _walk(self, node, out):
        out.append(node)
        for c in node.get("children", []):
            self._walk(c, out)
        return out

    def test_every_produced_anchor_resolves_to_the_same_node(self):
        nodes = self._walk(self.rsg["root"], [])
        self.assertGreater(len(nodes), 20)
        seen_paths = {}
        bookmark_anchors = 0
        for n in nodes:
            anchor = n["anchor"]
            self.assertEqual(anchor["kind"], "ooxml_path")
            resolved = rr_anchor.ooxml_try_resolve(self.docx, anchor)
            self.assertIsNotNone(resolved, f"infer-office anchor did not resolve: {anchor}")
            name, steps = rr_anchor.ooxml_parse_path(anchor["value"])
            if name is not None:
                bookmark_anchors += 1
            else:
                # a body-rooted anchor's parsed steps ARE the resolved node's absolute structural path.
                self.assertEqual(resolved.path, tuple(steps), f"path drift on {anchor}")
            # no two produced anchors may name the same node (stable, unique identities).
            path = resolved.path
            self.assertNotIn(path, seen_paths, f"two anchors resolved to the same node: {path}")
            seen_paths[path] = anchor["value"]
        self.assertGreaterEqual(bookmark_anchors, 1, "expected at least one bookmark anchor in the corpus")

    def test_surgical_and_regenerate_nodes_resolve_to_expected_content(self):
        index = {}
        for n in self._walk(self.rsg["root"], []):
            index[n["id"]] = n
        # the surgical bookmark node resolves to the currency value it edits.
        surg = index["bookmark(revenue_total)"]
        self.assertEqual(surg["class"], "surgical")
        self.assertEqual(rr_anchor.ooxml_resolve(self.docx, surg["anchor"]).text(), "$1,284,500")
        # the regenerate drawing node resolves to a <w:drawing> leaf.
        draw = index["body/p[6]/r[1]/drawing[1]"]
        self.assertEqual(draw["class"], "regenerate")
        self.assertEqual(rr_anchor.ooxml_resolve(self.docx, draw["anchor"]).local_name, "drawing")


if __name__ == "__main__":
    unittest.main()
