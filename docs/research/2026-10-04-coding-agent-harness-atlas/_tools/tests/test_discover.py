import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ["ATLAS_TEST_ALLOW_ANY_TREE"] = "1"
TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import discover  # noqa: E402
from atlas_common import load_json  # noqa: E402
from discover import (  # noqa: E402
    apply_scope,
    canonical,
    closure_candidates,
    extract_links,
    parse_llms_txt,
    parse_sitemap,
    provenance,
    url_set_digest,
)

HOST = "docs.example"
BASE = "https://docs.example/docs/llms.txt"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def lines(*parts):
    return "\n".join(parts) + "\n"


class CanonicalTests(unittest.TestCase):
    def test_each_normalisation(self):
        cases = {
            "https://example.com/a#frag": "https://example.com/a",
            "https://example.com/a?x=1&y=2": "https://example.com/a",
            "https://example.com/a.md": "https://example.com/a",
            "https://example.com/a.html": "https://example.com/a",
            "https://example.com/a/": "https://example.com/a",
            "https://example.com:443/a": "https://example.com/a",
            "HTTPS://Example.COM/a": "https://example.com/a",
            "https://example.com/": "https://example.com",
            "https://example.com": "https://example.com",
            "https://example.com/a.md/": "https://example.com/a",
            "https://example.com/a.md?x=1#y": "https://example.com/a",
            "https://example.com/a/b.html": "https://example.com/a/b",
        }
        for given, want in cases.items():
            with self.subTest(given=given):
                self.assertEqual(canonical(given), want)

    def test_things_that_must_not_change(self):
        for url in (
            "https://example.com/Docs/Page",  # path case is significant
            "https://example.com:8443/a",  # a non-default port is a different origin
            "https://example.com/a.mdx",
            "https://example.com/amd",
            "https://example.com/a.markdown",
            "http://example.com:443/a",  # 443 is not the default port of http
        ):
            with self.subTest(url=url):
                self.assertEqual(canonical(url), url)

    def test_spellings_of_one_page_compare_equal(self):
        spellings = [
            "https://docs.example/docs/a",
            "https://docs.example/docs/a.md",
            "https://DOCS.example/docs/a/",
            "https://docs.example:443/docs/a.html#top",
            "https://docs.example/docs/a?utm=1",
        ]
        self.assertEqual({canonical(u) for u in spellings}, {"https://docs.example/docs/a"})


class ParseLlmsTxtTests(unittest.TestCase):
    def test_sections_relative_links_and_bare_url(self):
        text = lines(
            "# Product docs",
            "",
            "> A summary with [a quoted link](https://docs.example/docs/summary).",
            "",
            "## Getting started",
            "- [Install](/docs/install.md): how to install",
            "- [Quickstart](quickstart.md)",
            "https://docs.example/docs/bare-line",
            "",
            "### Not a section heading",
            "- [Deep](../up/deep.md)",
            "",
            "## Reference",
            "- [API](https://docs.example/docs/api#auth) and [CLI](/docs/cli)",
        )
        entries = parse_llms_txt(text, BASE)
        self.assertEqual(
            [(e["url"], e["title"], e["section"]) for e in entries],
            [
                ("https://docs.example/docs/summary", "a quoted link", ""),
                ("https://docs.example/docs/install.md", "Install", "Getting started"),
                ("https://docs.example/docs/quickstart.md", "Quickstart", "Getting started"),
                ("https://docs.example/docs/bare-line", "", "Getting started"),
                ("https://docs.example/up/deep.md", "Deep", "Getting started"),
                ("https://docs.example/docs/api", "API", "Reference"),
                ("https://docs.example/docs/cli", "CLI", "Reference"),
            ],
        )

    def test_bullet_prefixed_bare_url_is_found(self):
        entries = parse_llms_txt("## S\n- https://docs.example/docs/x\n", BASE)
        self.assertEqual([e["url"] for e in entries], ["https://docs.example/docs/x"])

    def test_fenced_blocks_are_ignored_and_do_not_change_the_section(self):
        text = lines(
            "## Real",
            "```",
            "- [Fenced](/docs/fenced)",
            "## NotASection",
            "```",
            "- [After](/docs/after)",
            "~~~md",
            "- [Tilde](/docs/tilde)",
            "~~~",
            "- [Last](/docs/last)",
        )
        entries = parse_llms_txt(text, BASE)
        self.assertEqual(
            [(e["url"], e["section"]) for e in entries],
            [
                ("https://docs.example/docs/after", "Real"),
                ("https://docs.example/docs/last", "Real"),
            ],
        )

    def test_an_unclosed_fence_swallows_the_rest(self):
        entries = parse_llms_txt("- [A](/docs/a)\n```\n- [B](/docs/b)\n", BASE)
        self.assertEqual([e["url"] for e in entries], ["https://docs.example/docs/a"])

    def test_a_shorter_fence_does_not_close_a_longer_one(self):
        text = lines("````", "```", "- [In](/docs/in)", "````", "- [Out](/docs/out)")
        entries = parse_llms_txt(text, BASE)
        self.assertEqual([e["url"] for e in entries], ["https://docs.example/docs/out"])

    def test_non_http_links_are_ignored(self):
        text = lines(
            "- [Mail](mailto:someone@docs.example)",
            "- [Js](javascript:void(0))",
            "- [Ftp](ftp://docs.example/file)",
            "- [Ok](/docs/ok)",
        )
        entries = parse_llms_txt(text, BASE)
        self.assertEqual([e["url"] for e in entries], ["https://docs.example/docs/ok"])

    def test_spellings_that_differ_only_by_md_are_kept_once_first_wins(self):
        text = lines(
            "## One",
            "- [A](/docs/a.md)",
            "## Two",
            "- [A again](/docs/a)",
            "- [A third](https://DOCS.example/docs/a/#x)",
        )
        entries = parse_llms_txt(text, BASE)
        self.assertEqual(len(entries), 1)
        self.assertEqual(
            (entries[0]["url"], entries[0]["title"], entries[0]["section"]),
            ("https://docs.example/docs/a.md", "A", "One"),
        )

    def test_title_attribute_and_angle_brackets(self):
        text = '- [T](/docs/t.md "A title") [U](</docs/u.md>)\n'
        entries = parse_llms_txt(text, BASE)
        self.assertEqual(
            [e["url"] for e in entries],
            ["https://docs.example/docs/t.md", "https://docs.example/docs/u.md"],
        )

    def test_empty_target_is_skipped(self):
        self.assertEqual(parse_llms_txt("- [Nothing]()\n", BASE), [])


class ParseSitemapTests(unittest.TestCase):
    def test_urlset(self):
        xml = (
            "<urlset>"
            "<url><loc>https://docs.example/a</loc></url>"
            "<url><loc> https://docs.example/b </loc><lastmod>2026-01-01</lastmod></url>"
            "</urlset>"
        )
        self.assertEqual(
            parse_sitemap(xml),
            {"urls": ["https://docs.example/a", "https://docs.example/b"], "sitemaps": []},
        )

    def test_sitemapindex(self):
        xml = (
            "<sitemapindex>"
            "<sitemap><loc>https://docs.example/sitemap-0.xml</loc></sitemap>"
            "<sitemap><loc>https://docs.example/sitemap-1.xml</loc></sitemap>"
            "</sitemapindex>"
        )
        self.assertEqual(
            parse_sitemap(xml),
            {
                "urls": [],
                "sitemaps": [
                    "https://docs.example/sitemap-0.xml",
                    "https://docs.example/sitemap-1.xml",
                ],
            },
        )

    def test_namespaced_documents(self):
        urlset = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="{SITEMAP_NS}">'
            "<url><loc>https://docs.example/a</loc></url></urlset>"
        )
        index = (
            f'<sm:sitemapindex xmlns:sm="{SITEMAP_NS}">'
            "<sm:sitemap><sm:loc>https://docs.example/child.xml</sm:loc></sm:sitemap>"
            "</sm:sitemapindex>"
        )
        self.assertEqual(parse_sitemap(urlset)["urls"], ["https://docs.example/a"])
        self.assertEqual(parse_sitemap(index)["sitemaps"], ["https://docs.example/child.xml"])

    def test_leading_bom_and_whitespace_are_tolerated(self):
        xml = "﻿\n  <urlset><url><loc>https://docs.example/a</loc></url></urlset>"
        self.assertEqual(parse_sitemap(xml)["urls"], ["https://docs.example/a"])

    def test_declared_non_utf8_encoding_on_a_str_is_tolerated(self):
        xml = '<?xml version="1.0" encoding="ISO-8859-1"?><urlset><url><loc>https://docs.example/é</loc></url></urlset>'
        self.assertEqual(parse_sitemap(xml)["urls"], ["https://docs.example/é"])

    def test_only_a_loc_directly_under_url_is_read(self):
        xml = (
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
            "<url><loc>https://docs.example/page</loc>"
            "<image:image><image:loc>https://cdn.example/pic.png</image:loc></image:image></url>"
            "</urlset>"
        )
        self.assertEqual(parse_sitemap(xml)["urls"], ["https://docs.example/page"])

    def test_a_doctype_or_entity_is_refused(self):
        bodies = [
            "<!DOCTYPE urlset><urlset><url><loc>https://docs.example/a</loc></url></urlset>",
            "<!doctype urlset><urlset/>",
            '<!DOCTYPE urlset [<!ENTITY x SYSTEM "file:///etc/passwd">]><urlset>&x;</urlset>',
            '<urlset><!ENTITY x "y"></urlset>',
            '<!DOCTYPE lolz [<!ENTITY a "aaaa"><!ENTITY b "&a;&a;&a;&a;">]><urlset>&b;</urlset>',
        ]
        for body in bodies:
            with self.subTest(body=body[:40]):
                with self.assertRaises(ValueError) as caught:
                    parse_sitemap(body)
                self.assertIn("DOCTYPE or ENTITY", str(caught.exception))

    def test_malformed_xml_and_foreign_roots_raise_value_error(self):
        for body in ("", "<urlset><url>", "<html><body>Not found</body></html>", "<a/>"):
            with self.subTest(body=body):
                with self.assertRaises(ValueError):
                    parse_sitemap(body)


class ExtractLinksTests(unittest.TestCase):
    PAGE = "https://docs.example/docs/guide/page.md"

    def test_markdown_and_both_html_quote_styles(self):
        text = lines(
            "See [one](https://docs.example/docs/one) and",
            '<a href="https://docs.example/docs/two">two</a> and',
            "<a class='x' href='https://docs.example/docs/three'>three</a>.",
        )
        self.assertEqual(
            extract_links(text, self.PAGE),
            [
                "https://docs.example/docs/one",
                "https://docs.example/docs/two",
                "https://docs.example/docs/three",
            ],
        )

    def test_relative_links_resolve_against_the_page_and_fragments_are_stripped(self):
        text = "[a](sibling.md#part) [b](../up) [c](/root/x) [d](//other.example/y) [e](#self)"
        self.assertEqual(
            extract_links(text, self.PAGE),
            [
                "https://docs.example/docs/guide/sibling.md",
                "https://docs.example/docs/up",
                "https://docs.example/root/x",
                "https://other.example/y",
                "https://docs.example/docs/guide/page.md",
            ],
        )

    def test_order_of_first_appearance_across_markdown_and_html(self):
        text = '<a href="/z">z</a> [m](/m) <a href="/a">a</a>'
        self.assertEqual(
            extract_links(text, self.PAGE),
            ["https://docs.example/z", "https://docs.example/m", "https://docs.example/a"],
        )

    def test_deduplicated_by_canonical_first_spelling_kept(self):
        text = "[a](/docs/x.md) [b](/docs/x) [c](https://DOCS.example/docs/x/) <a href='/docs/x#y'>"
        self.assertEqual(extract_links(text, self.PAGE), ["https://docs.example/docs/x.md"])

    def test_code_spans_and_fences_are_ignored(self):
        text = lines(
            "Real [one](/real/one) and `[span](/code/span)` and ``[double `tick`](/code/two)``.",
            "```html",
            '<a href="/code/fenced">x</a> [f](/code/f)',
            "```",
            "~~~",
            "[t](/code/tilde)",
            "~~~",
            "Then [two](/real/two) and <code>text</code>.",
        )
        self.assertEqual(
            extract_links(text, self.PAGE),
            ["https://docs.example/real/one", "https://docs.example/real/two"],
        )

    def test_an_unmatched_backtick_does_not_hide_later_links(self):
        text = "A stray ` tick on this line\n[after](/real/after)\n"
        self.assertEqual(extract_links(text, self.PAGE), ["https://docs.example/real/after"])

    def test_non_http_schemes_are_dropped(self):
        text = '[m](mailto:a@b.example) [j](javascript:x) <a href="tel:123">t</a> [ok](/ok)'
        self.assertEqual(extract_links(text, self.PAGE), ["https://docs.example/ok"])

    def test_images_are_not_links_but_a_link_wrapping_an_image_is(self):
        text = "![logo](/img/logo.png) [![badge](/img/badge.svg)](/real/target)"
        self.assertEqual(extract_links(text, self.PAGE), ["https://docs.example/real/target"])

    def test_html_entities_in_href_are_unescaped(self):
        text = '<a href="/docs/search?a=1&amp;b=2">s</a>'
        self.assertEqual(
            extract_links(text, self.PAGE), ["https://docs.example/docs/search?a=1&b=2"]
        )

    def test_title_attribute_and_parentheses_in_target(self):
        text = '[t](/docs/t "Title") [p](/docs/wiki_(thing)) [after](/docs/after)'
        self.assertEqual(
            extract_links(text, self.PAGE),
            [
                "https://docs.example/docs/t",
                "https://docs.example/docs/wiki_(thing)",
                "https://docs.example/docs/after",
            ],
        )

    def test_no_links_gives_an_empty_list(self):
        self.assertEqual(extract_links("plain text, no links", self.PAGE), [])


class ApplyScopeTests(unittest.TestCase):
    def test_every_drop_reason(self):
        urls = [
            "https://docs.example/docs/ok",
            "http://docs.example/docs/plain-http",
            "https://elsewhere.example/docs/x",
            "https://docs.example/blog/post",
            "https://docs.example/docs/old/page",
        ]
        kept, dropped = apply_scope(urls, [HOST], include=[r"^/docs/"], exclude=[r"^/docs/old/"])
        self.assertEqual(kept, ["https://docs.example/docs/ok"])
        self.assertEqual(
            dropped,
            [
                {"url": "http://docs.example/docs/plain-http", "reason": "not_https"},
                {"url": "https://elsewhere.example/docs/x", "reason": "off_allow_list"},
                {"url": "https://docs.example/blog/post", "reason": "not_included"},
                {"url": "https://docs.example/docs/old/page", "reason": "excluded"},
            ],
        )

    def test_sections_filter_is_case_insensitive_and_exempts_items_without_a_section(self):
        items = [
            {"url": "https://docs.example/a", "section": "Core"},
            {"url": "https://docs.example/b", "section": "Extras"},
            {"url": "https://docs.example/c", "section": ""},
            {"url": "https://docs.example/d"},
            "https://docs.example/e",
        ]
        kept, dropped = apply_scope(items, [HOST], sections={"core"})
        self.assertEqual(
            [i if isinstance(i, str) else i["url"] for i in kept],
            [
                "https://docs.example/a",
                "https://docs.example/d",
                "https://docs.example/e",
            ],
        )
        self.assertEqual(
            dropped,
            [
                {"url": "https://docs.example/b", "reason": "wrong_section"},
                {"url": "https://docs.example/c", "reason": "wrong_section"},
            ],
        )

    def test_sections_none_means_no_section_filter(self):
        items = [{"url": "https://docs.example/a", "section": "Anything"}]
        self.assertEqual(apply_scope(items, [HOST], sections=None), (items, []))

    def test_kept_items_are_the_original_objects_in_order(self):
        items = [
            {"url": "https://docs.example/b", "title": "B", "section": "S"},
            {"url": "https://docs.example/a", "title": "A", "section": "S"},
        ]
        kept, dropped = apply_scope(items, [HOST])
        self.assertEqual(kept, items)
        self.assertIs(kept[0], items[0])
        self.assertEqual(dropped, [])

    def test_host_match_is_exact_and_case_insensitive(self):
        kept, dropped = apply_scope(
            [
                "https://DOCS.Example/a",
                "https://sub.docs.example/a",
                "https://docs.example.evil.example/a",
                "https://evil.example/a",
            ],
            ["Docs.EXAMPLE"],
        )
        self.assertEqual(kept, ["https://DOCS.Example/a"])
        self.assertEqual({d["reason"] for d in dropped}, {"off_allow_list"})
        self.assertEqual(len(dropped), 3)

    def test_userinfo_cannot_smuggle_an_allowed_host(self):
        kept, dropped = apply_scope(["https://docs.example@evil.example/a"], [HOST])
        self.assertEqual(kept, [])
        self.assertEqual(dropped[0]["reason"], "off_allow_list")

    def test_a_non_default_port_is_off_the_allow_list(self):
        kept, dropped = apply_scope(
            [
                "https://docs.example:8443/a",
                "https://docs.example:443/a",
                "https://docs.example:x/a",
            ],
            [HOST],
        )
        self.assertEqual(kept, ["https://docs.example:443/a"])
        self.assertEqual([d["reason"] for d in dropped], ["off_allow_list", "off_allow_list"])

    def test_include_matches_when_any_pattern_matches_and_matches_the_path_only(self):
        urls = [
            "https://docs.example/docs/en/a",
            "https://docs.example/docs/fr/a",
            "https://docs.example/other?next=/docs/en/",
        ]
        kept, dropped = apply_scope(urls, [HOST], include=[r"^/docs/en/", r"^/docs/fr/"])
        self.assertEqual(kept, urls[:2])
        self.assertEqual(dropped, [{"url": urls[2], "reason": "not_included"}])

    def test_exclude_wins_over_include(self):
        kept, dropped = apply_scope(
            ["https://docs.example/docs/en/changelog"],
            [HOST],
            include=[r"^/docs/"],
            exclude=[r"changelog"],
        )
        self.assertEqual((kept, [d["reason"] for d in dropped]), ([], ["excluded"]))

    def test_a_bare_string_is_one_pattern_not_a_set_of_characters(self):
        kept, _ = apply_scope(["https://docs.example/docs/a"], HOST, include="^/docs/")
        self.assertEqual(kept, ["https://docs.example/docs/a"])

    def test_drop_reason_order_is_https_then_host_then_include_then_exclude_then_section(self):
        item = {"url": "http://elsewhere.example/blog/old", "section": "Nope"}
        _, dropped = apply_scope(
            [item], [HOST], include=[r"^/docs/"], exclude=[r"old"], sections={"core"}
        )
        self.assertEqual(dropped[0]["reason"], "not_https")
        item["url"] = "https://elsewhere.example/blog/old"
        _, dropped = apply_scope(
            [item], [HOST], include=[r"^/docs/"], exclude=[r"old"], sections={"core"}
        )
        self.assertEqual(dropped[0]["reason"], "off_allow_list")
        item["url"] = "https://docs.example/blog/old"
        _, dropped = apply_scope(
            [item], [HOST], include=[r"^/docs/"], exclude=[r"old"], sections={"core"}
        )
        self.assertEqual(dropped[0]["reason"], "not_included")
        item["url"] = "https://docs.example/docs/old"
        _, dropped = apply_scope(
            [item], [HOST], include=[r"^/docs/"], exclude=[r"old"], sections={"core"}
        )
        self.assertEqual(dropped[0]["reason"], "excluded")
        item["url"] = "https://docs.example/docs/new"
        _, dropped = apply_scope(
            [item], [HOST], include=[r"^/docs/"], exclude=[r"old"], sections={"core"}
        )
        self.assertEqual(dropped[0]["reason"], "wrong_section")

    def test_an_unparseable_url_is_dropped_not_raised(self):
        kept, dropped = apply_scope(["https://[bad/a"], [HOST])
        self.assertEqual((kept, dropped[0]["reason"]), ([], "not_https"))


class ClosureCandidatesTests(unittest.TestCase):
    A = "https://docs.example/docs/a.md"
    B = "https://docs.example/docs/b"

    def test_finds_exactly_the_links_absent_from_the_known_set(self):
        pages = {
            self.A: lines(
                "[b](/docs/b.md) [c](/docs/c) <a href='/docs/d'>d</a>",
                "[off](https://elsewhere.example/e) [mail](mailto:x@y.example)",
            )
        }
        found = closure_candidates([self.A, self.B], pages, [HOST])
        self.assertEqual(
            found,
            [
                {"url": "https://docs.example/docs/c", "sources": [self.A]},
                {"url": "https://docs.example/docs/d", "sources": [self.A]},
            ],
        )

    def test_lists_every_linking_page_sorted_and_the_result_is_sorted_by_url(self):
        pages = {
            self.B: "[z](/docs/z) [c](/docs/c)",
            self.A: "[c](/docs/c.md) [z](/docs/z/) [only](/docs/only-a)",
        }
        found = closure_candidates([], pages, [HOST])
        # The spelling kept is the first one met, scanning pages in sorted order (A before B).
        self.assertEqual(
            found,
            [
                {"url": "https://docs.example/docs/c.md", "sources": [self.A, self.B]},
                {"url": "https://docs.example/docs/only-a", "sources": [self.A]},
                {"url": "https://docs.example/docs/z/", "sources": [self.A, self.B]},
            ],
        )

    def test_one_url_linked_from_two_pages_is_one_candidate_with_both_sources(self):
        pages = {self.B: "[c](/docs/c)", self.A: "[c](/docs/c.md)"}
        found = closure_candidates([self.A, self.B], pages, [HOST])
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["sources"], sorted([self.A, self.B]))

    def test_known_urls_are_compared_by_canonical_form(self):
        pages = {self.A: "[x](/docs/x)"}
        self.assertEqual(
            closure_candidates(["https://DOCS.example/docs/x.md#f"], pages, [HOST]), []
        )

    def test_scope_is_applied_to_candidates(self):
        pages = {self.A: "[a](/docs/en/a) [b](/blog/b) [c](/docs/en/old/c)"}
        found = closure_candidates([], pages, [HOST], include=[r"^/docs/en/"], exclude=[r"/old/"])
        self.assertEqual([f["url"] for f in found], ["https://docs.example/docs/en/a"])

    def test_no_pages_means_no_candidates(self):
        self.assertEqual(closure_candidates([self.A], {}, [HOST]), [])


class DigestTests(unittest.TestCase):
    def test_order_and_spelling_do_not_matter(self):
        one = ["https://docs.example/y/", "https://docs.example/x.md#f", "https://docs.example/x"]
        two = ["https://docs.example/x", "https://docs.example/y"]
        self.assertEqual(url_set_digest(one), url_set_digest(two))
        self.assertEqual(url_set_digest(two), url_set_digest(list(reversed(two))))

    def test_value_is_sha256_of_the_sorted_newline_joined_canonical_forms(self):
        want = hashlib.sha256(b"https://docs.example/x\nhttps://docs.example/y").hexdigest()
        got = url_set_digest(["https://docs.example/y/", "https://docs.example/x.md"])
        self.assertEqual(got, want)

    def test_adding_or_changing_a_url_changes_the_digest(self):
        base = ["https://docs.example/x"]
        self.assertNotEqual(url_set_digest(base), url_set_digest(base + ["https://docs.example/y"]))
        self.assertNotEqual(url_set_digest(base), url_set_digest(["https://docs.example/X"]))

    def test_empty_set(self):
        self.assertEqual(url_set_digest([]), hashlib.sha256(b"").hexdigest())


class ProvenanceTests(unittest.TestCase):
    @staticmethod
    def row(url, outcome="fetched", effective=None):
        return {"url": url, "url_effective": effective or url, "outcome": outcome}

    @staticmethod
    def origin(url, source, origin="https://docs.example/where"):
        return {"url": url, "source": source, "origin": origin}

    def test_flags_a_fetched_url_with_no_origin_and_counts_sources(self):
        rows = [
            self.row("https://docs.example/a.md"),
            self.row("https://docs.example/b"),
            self.row("https://docs.example/c"),
            self.row("https://docs.example/ghost"),
        ]
        origins = [
            self.origin("https://docs.example/a", "index"),
            self.origin("https://docs.example/b", "sitemap"),
            self.origin("https://docs.example/c", "closure"),
        ]
        self.assertEqual(
            provenance(rows, origins),
            {
                "rows": 4,
                "traced": 3,
                "untraced": ["https://docs.example/ghost"],
                "by_source": {"index": 1, "sitemap": 1, "closure": 1},
            },
        )

    def test_only_fetched_rows_need_an_origin(self):
        rows = [
            self.row("https://docs.example/a"),
            self.row("https://docs.example/missing", outcome="negative"),
            self.row("https://docs.example/blocked", outcome="refused"),
            self.row("https://docs.example/later", outcome="indeterminate"),
        ]
        report = provenance(rows, [self.origin("https://docs.example/a", "index")])
        self.assertEqual((report["rows"], report["traced"], report["untraced"]), (1, 1, []))

    def test_the_requested_url_is_traced_not_the_redirect_target(self):
        rows = [
            self.row(
                "https://docs.example/unpublished",
                effective="https://docs.example/published",
            )
        ]
        report = provenance(rows, [self.origin("https://docs.example/published", "index")])
        self.assertEqual(report["untraced"], ["https://docs.example/unpublished"])
        self.assertEqual(report["traced"], 0)

    def test_a_url_with_several_origins_is_counted_once_under_the_strongest(self):
        rows = [self.row("https://docs.example/a")]
        origins = [
            self.origin("https://docs.example/a", "closure", "https://docs.example/p1"),
            self.origin("https://docs.example/a", "sitemap"),
            self.origin("https://docs.example/a", "closure", "https://docs.example/p2"),
        ]
        report = provenance(rows, origins)
        self.assertEqual(report["by_source"], {"index": 0, "sitemap": 1, "closure": 0})
        self.assertEqual(sum(report["by_source"].values()), report["traced"])

    def test_rows_always_equal_traced_plus_untraced(self):
        rows = [self.row(f"https://docs.example/{n}") for n in "abcde"]
        origins = [self.origin(f"https://docs.example/{n}", "index") for n in "ac"]
        report = provenance(rows, origins)
        self.assertEqual(report["rows"], report["traced"] + len(report["untraced"]))
        self.assertEqual(report["untraced"], [f"https://docs.example/{n}" for n in "bde"])

    def test_no_origins_means_every_fetched_row_is_untraced(self):
        report = provenance([self.row("https://docs.example/a")], [])
        self.assertEqual((report["traced"], len(report["untraced"])), (0, 1))

    def test_an_unknown_source_is_an_error_not_a_silent_pass(self):
        with self.assertRaises(ValueError):
            provenance([], [self.origin("https://docs.example/a", "guess")])


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        data = self.tmp / "data"
        data.mkdir()
        (data / "surfaces.json").write_text(
            json.dumps({"surfaces": [{"id": "demo", "docs_hosts": [HOST]}]}), encoding="utf-8"
        )
        patcher = mock.patch.object(discover, "DATA_DIR", data)
        patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, name, text):
        path = self.tmp / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return str(path)

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = discover.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def read_jsonl(self, path):
        with open(path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    INDEX_TEXT = lines(
        "# Docs",
        "## Core",
        "- [A](/docs/a.md)",
        "- [B](/docs/b)",
        "- [Ext](https://elsewhere.example/x)",
        "## Extra",
        "- [C](/docs/c)",
        "- [Old](/docs/old/z)",
        "- [A dup](/docs/a)",
    )

    def test_index_writes_origins_dropped_and_digest(self):
        llms = self.write("llms.txt", self.INDEX_TEXT)
        out_path = str(self.tmp / "out" / "index.jsonl")
        dropped_path = str(self.tmp / "out" / "dropped.json")
        code, out, _err = self.run_cli(
            "index", "--surface", "demo", "--file", llms, "--base", BASE,
            "--include", "^/docs/", "--exclude", "^/docs/old/",
            "--out", out_path, "--dropped", dropped_path,
        )  # fmt: skip
        self.assertEqual(code, 0)
        kept = [
            "https://docs.example/docs/a.md",
            "https://docs.example/docs/b",
            "https://docs.example/docs/c",
        ]
        self.assertEqual(
            self.read_jsonl(out_path),
            [{"url": u, "source": "index", "origin": BASE} for u in kept],
        )
        self.assertEqual(
            load_json(dropped_path),
            [
                {"url": "https://elsewhere.example/x", "reason": "off_allow_list"},
                {"url": "https://docs.example/docs/old/z", "reason": "excluded"},
            ],
        )
        self.assertEqual(out.strip(), url_set_digest(kept))

    def test_index_section_filter(self):
        llms = self.write("llms.txt", self.INDEX_TEXT)
        out_path = str(self.tmp / "index.jsonl")
        code, _out, _err = self.run_cli(
            "index", "--surface", "demo", "--file", llms, "--base", BASE,
            "--section", "core", "--out", out_path,
            "--dropped", str(self.tmp / "dropped.json"),
        )  # fmt: skip
        self.assertEqual(code, 0)
        urls = [r["url"] for r in self.read_jsonl(out_path)]
        self.assertEqual(urls, ["https://docs.example/docs/a.md", "https://docs.example/docs/b"])
        reasons = {d["url"]: d["reason"] for d in load_json(self.tmp / "dropped.json")}
        self.assertEqual(reasons["https://docs.example/docs/c"], "wrong_section")

    def test_include_and_exclude_accept_several_values_either_way(self):
        llms = self.write("llms.txt", "- [A](/a/1)\n- [B](/b/1)\n- [C](/c/1)\n- [D](/a/skip)\n")
        for flags in (
            ["--include", "^/a/", "^/b/", "--exclude", "skip"],
            ["--include", "^/a/", "--include", "^/b/", "--exclude", "skip"],
        ):
            out_path = str(self.tmp / "index.jsonl")
            code, _o, _e = self.run_cli(
                "index", "--surface", "demo", "--file", llms, "--base", BASE, *flags,
                "--out", out_path, "--dropped", str(self.tmp / "dropped.json"),
            )  # fmt: skip
            self.assertEqual(code, 0)
            self.assertEqual(
                [r["url"] for r in self.read_jsonl(out_path)],
                ["https://docs.example/a/1", "https://docs.example/b/1"],
            )

    def test_unknown_surface_is_exit_2_and_writes_nothing(self):
        llms = self.write("llms.txt", self.INDEX_TEXT)
        out_path = self.tmp / "index.jsonl"
        code, _out, err = self.run_cli(
            "index", "--surface", "nope", "--file", llms, "--base", BASE,
            "--out", str(out_path), "--dropped", str(self.tmp / "d.json"),
        )  # fmt: skip
        self.assertEqual(code, 2)
        self.assertIn("unknown surface", err)
        self.assertFalse(out_path.exists())

    def test_missing_input_file_is_exit_2(self):
        code, _out, err = self.run_cli(
            "index", "--surface", "demo", "--file", str(self.tmp / "absent.txt"),
            "--base", BASE, "--out", str(self.tmp / "o.jsonl"),
            "--dropped", str(self.tmp / "d.json"),
        )  # fmt: skip
        self.assertEqual(code, 2)
        self.assertIn("discover:", err)

    def test_missing_required_argument_is_a_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            discover.main(["index", "--surface", "demo"])
        self.assertEqual(caught.exception.code, 2)

    def test_sitemap_writes_origins_and_prints_child_sitemaps(self):
        sitemap = self.write(
            "sitemap.xml",
            f'<urlset xmlns="{SITEMAP_NS}">'
            "<url><loc>https://docs.example/docs/a</loc></url>"
            "<url><loc>https://docs.example/docs/a.md</loc></url>"
            "<url><loc>https://docs.example/blog/p</loc></url>"
            "<url><loc>https://elsewhere.example/docs/q</loc></url>"
            "</urlset>",
        )
        out_path = str(self.tmp / "sitemap.jsonl")
        base = "https://docs.example/sitemap.xml"
        code, out, _err = self.run_cli(
            "sitemap", "--surface", "demo", "--file", sitemap, "--base", base,
            "--include", "^/docs/", "--out", out_path,
        )  # fmt: skip
        self.assertEqual(code, 0)
        self.assertEqual(
            self.read_jsonl(out_path),
            [{"url": "https://docs.example/docs/a", "source": "sitemap", "origin": base}],
        )
        self.assertEqual(out.splitlines(), [url_set_digest(["https://docs.example/docs/a"])])

    def test_sitemap_index_lists_only_allow_listed_children(self):
        sitemap = self.write(
            "index.xml",
            f'<sitemapindex xmlns="{SITEMAP_NS}">'
            "<sitemap><loc>https://docs.example/sitemap-0.xml</loc></sitemap>"
            "<sitemap><loc>https://elsewhere.example/sitemap-1.xml</loc></sitemap>"
            "<sitemap><loc>https://docs.example/sitemap-2.xml</loc></sitemap>"
            "</sitemapindex>",
        )
        out_path = str(self.tmp / "sitemap.jsonl")
        code, out, err = self.run_cli(
            "sitemap", "--surface", "demo", "--file", sitemap,
            "--base", "https://docs.example/sitemap.xml", "--out", out_path,
        )  # fmt: skip
        self.assertEqual(code, 0)
        self.assertEqual(
            [line for line in out.splitlines() if line.startswith("CHILD ")],
            [
                "CHILD https://docs.example/sitemap-0.xml",
                "CHILD https://docs.example/sitemap-2.xml",
            ],
        )
        self.assertIn("elsewhere.example/sitemap-1.xml", err)
        self.assertEqual(self.read_jsonl(out_path), [])

    def test_sitemap_with_a_doctype_is_refused_with_exit_2(self):
        sitemap = self.write(
            "bad.xml",
            '<!DOCTYPE urlset [<!ENTITY x "y">]><urlset><url><loc>https://docs.example/a</loc></url></urlset>',
        )
        out_path = self.tmp / "sitemap.jsonl"
        code, _out, err = self.run_cli(
            "sitemap", "--surface", "demo", "--file", sitemap,
            "--base", "https://docs.example/sitemap.xml", "--out", str(out_path),
        )  # fmt: skip
        self.assertEqual(code, 2)
        self.assertIn("DOCTYPE", err)
        self.assertFalse(out_path.exists())

    def known_file(self, *urls):
        return self.write(
            "known.jsonl",
            "".join(json.dumps({"url": u, "source": "index", "origin": BASE}) + "\n" for u in urls),
        )

    def test_closure_writes_one_record_per_linking_page(self):
        page_a = "https://docs.example/docs/a.md"
        page_b = "https://docs.example/docs/b"
        known = self.known_file(page_a, page_b)
        self.write(
            "pages/a.txt", "[b](/docs/b.md) [c](/docs/c) [d](/docs/d) [off](https://x.example/o)"
        )
        self.write("pages/b.txt", "[c](/docs/c.md) [a](/docs/a)")
        page_map = self.write("pagemap.json", json.dumps({page_a: "a.txt", page_b: "b.txt"}))
        out_path = str(self.tmp / "closure.jsonl")
        code, _out, _err = self.run_cli(
            "closure", "--surface", "demo", "--known", known,
            "--pages-dir", str(self.tmp / "pages"), "--page-map", page_map, "--out", out_path,
        )  # fmt: skip
        self.assertEqual(code, 0)
        records = self.read_jsonl(out_path)
        # /docs/c and /docs/c.md are one page: one url, one record per page that links to it.
        self.assertEqual(
            [(r["url"], r["origin"]) for r in records],
            [
                ("https://docs.example/docs/c", page_a),
                ("https://docs.example/docs/c", page_b),
                ("https://docs.example/docs/d", page_a),
            ],
        )
        self.assertEqual({r["source"] for r in records}, {"closure"})

    def test_closure_missing_page_file_is_exit_2_not_a_silent_skip(self):
        page_a = "https://docs.example/docs/a.md"
        page_map = self.write("pagemap.json", json.dumps({page_a: "absent.txt"}))
        out_path = self.tmp / "closure.jsonl"
        code, _out, err = self.run_cli(
            "closure", "--surface", "demo", "--known", self.known_file(page_a),
            "--pages-dir", str(self.tmp / "pages"), "--page-map", page_map, "--out", str(out_path),
        )  # fmt: skip
        self.assertEqual(code, 2)
        self.assertIn("absent.txt", err)
        self.assertFalse(out_path.exists())

    def test_closure_refuses_a_page_file_outside_the_pages_dir(self):
        page_a = "https://docs.example/docs/a.md"
        self.write("secret.txt", "[x](/docs/x)")
        (self.tmp / "pages").mkdir()
        for name in ("../secret.txt", str(self.tmp / "secret.txt")):
            page_map = self.write("pagemap.json", json.dumps({page_a: name}))
            out_path = self.tmp / "closure.jsonl"
            code, _out, err = self.run_cli(
                "closure", "--surface", "demo", "--known", self.known_file(page_a),
                "--pages-dir", str(self.tmp / "pages"), "--page-map", page_map,
                "--out", str(out_path),
            )  # fmt: skip
            self.assertEqual(code, 2, name)
            self.assertIn("outside --pages-dir", err)
            self.assertFalse(out_path.exists())

    def manifest_file(self, *rows):
        return self.write("manifest.jsonl", "".join(json.dumps(r) + "\n" for r in rows) + "\n")

    def test_provenance_exits_nonzero_on_an_untraced_row_and_writes_the_report(self):
        manifest = self.manifest_file(
            {"url": "https://docs.example/docs/a.md", "url_effective": "x", "outcome": "fetched"},
            {"url": "https://docs.example/docs/c", "url_effective": "x", "outcome": "fetched"},
            {"url": "https://docs.example/docs/ghost", "url_effective": "x", "outcome": "fetched"},
            {"url": "https://docs.example/docs/gone", "url_effective": "x", "outcome": "negative"},
        )
        first = self.write(
            "o1.jsonl",
            json.dumps({"url": "https://docs.example/docs/a", "source": "index", "origin": BASE})
            + "\n",
        )
        second = self.write(
            "o2.jsonl",
            json.dumps({"url": "https://docs.example/docs/c", "source": "closure", "origin": "p"})
            + "\n",
        )
        report_path = str(self.tmp / "report.json")
        code, _out, err = self.run_cli(
            "provenance", "--manifest", manifest, "--origins", first, "--origins", second,
            "--out", report_path,
        )  # fmt: skip
        self.assertEqual(code, 1)
        self.assertIn("https://docs.example/docs/ghost", err)
        self.assertEqual(
            load_json(report_path),
            {
                "rows": 3,
                "traced": 2,
                "untraced": ["https://docs.example/docs/ghost"],
                "by_source": {"index": 1, "sitemap": 0, "closure": 1},
            },
        )
        third = self.write(
            "o3.jsonl",
            json.dumps(
                {"url": "https://docs.example/docs/ghost", "source": "sitemap", "origin": "s"}
            )
            + "\n",
        )
        code, _out, _err = self.run_cli(
            "provenance", "--manifest", manifest, "--origins", first, second, third,
            "--out", report_path,
        )  # fmt: skip
        self.assertEqual(code, 0)
        self.assertEqual(load_json(report_path)["untraced"], [])

    def test_provenance_malformed_json_line_is_exit_2_with_the_line_number(self):
        manifest = self.write("manifest.jsonl", '{"url": "a", "outcome": "fetched"}\n{not json\n')
        origins = self.write("o.jsonl", "")
        code, _out, err = self.run_cli(
            "provenance", "--manifest", manifest, "--origins", origins,
            "--out", str(self.tmp / "r.json"),
        )  # fmt: skip
        self.assertEqual(code, 2)
        self.assertIn("manifest.jsonl:2", err)

    def test_index_closure_provenance_round_trip(self):
        llms = self.write("llms.txt", "- [A](/docs/a.md)\n- [B](/docs/b)\n")
        index_out = str(self.tmp / "index.jsonl")
        code, _o, _e = self.run_cli(
            "index", "--surface", "demo", "--file", llms, "--base", BASE,
            "--out", index_out, "--dropped", str(self.tmp / "dropped.json"),
        )  # fmt: skip
        self.assertEqual(code, 0)
        page_a = "https://docs.example/docs/a.md"
        self.write("pages/a.md", "Also see [hidden](/docs/hidden) and [b](/docs/b).")
        page_map = self.write("pagemap.json", json.dumps({page_a: "a.md"}))
        closure_out = str(self.tmp / "closure.jsonl")
        code, _o, _e = self.run_cli(
            "closure", "--surface", "demo", "--known", index_out,
            "--pages-dir", str(self.tmp / "pages"), "--page-map", page_map, "--out", closure_out,
        )  # fmt: skip
        self.assertEqual(code, 0)
        self.assertEqual(
            [(r["url"], r["origin"]) for r in self.read_jsonl(closure_out)],
            [("https://docs.example/docs/hidden", page_a)],
        )
        fetched = [
            "https://docs.example/docs/a.md",
            "https://docs.example/docs/b",
            "https://docs.example/docs/hidden",
        ]
        manifest = self.manifest_file(
            *({"url": u, "url_effective": u, "outcome": "fetched"} for u in fetched)
        )
        args = ("--origins", index_out, "--origins", closure_out, "--out", str(self.tmp / "r.json"))
        code, _o, _e = self.run_cli("provenance", "--manifest", manifest, *args)
        self.assertEqual(code, 0)
        self.assertEqual(
            load_json(self.tmp / "r.json")["by_source"], {"index": 2, "sitemap": 0, "closure": 1}
        )
        sneaky = self.manifest_file(
            *({"url": u, "url_effective": u, "outcome": "fetched"} for u in fetched),
            {"url": "https://docs.example/docs/constructed", "outcome": "fetched"},
        )
        code, _o, _e = self.run_cli("provenance", "--manifest", sneaky, *args)
        self.assertEqual(code, 1)

    def test_selftest_prints_ok(self):
        code, out, _err = self.run_cli("--selftest")
        self.assertEqual((code, out), (0, "OK\n"))

    def test_the_worktree_check_runs_before_anything_else(self):
        refuse = mock.patch.object(discover, "assert_worktree", side_effect=SystemExit("refused"))
        out = io.StringIO()
        with refuse, contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            discover.main(["--selftest"])
        self.assertEqual(out.getvalue(), "")


class RealDataShapeTests(unittest.TestCase):
    def test_every_surface_in_the_real_surfaces_file_yields_docs_hosts(self):
        surfaces = load_json(discover.DATA_DIR / "surfaces.json")["surfaces"]
        self.assertTrue(surfaces)
        for surface in surfaces:
            with self.subTest(surface=surface["id"]):
                hosts = discover._surface_hosts(surface["id"])
                self.assertTrue(hosts)
                self.assertTrue(all(isinstance(h, str) and h for h in hosts))


class OutsideTheWorktreeTests(unittest.TestCase):
    COMMANDS = {
        "index": [
            "index", "--surface", "demo", "--file", "f", "--base", BASE,
            "--out", "o", "--dropped", "d",
        ],
        "sitemap": ["sitemap", "--surface", "demo", "--file", "f", "--base", BASE, "--out", "o"],
        "closure": [
            "closure", "--surface", "demo", "--known", "k", "--pages-dir", "p",
            "--page-map", "m", "--out", "o",
        ],
        "provenance": ["provenance", "--manifest", "m", "--origins", "o", "--out", "r"],
        "selftest": ["--selftest"],
    }  # fmt: skip

    @staticmethod
    def run_tool(argv, bypass):
        env = {k: v for k, v in os.environ.items() if k != "ATLAS_TEST_ALLOW_ANY_TREE"}
        if bypass:
            env["ATLAS_TEST_ALLOW_ANY_TREE"] = "1"
        return subprocess.run(
            [sys.executable, str(TOOLS / "discover.py"), *argv],
            cwd="/tmp",
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_every_command_refuses_to_run_outside_the_forge_worktree(self):
        for name, argv in self.COMMANDS.items():
            with self.subTest(command=name):
                done = self.run_tool(argv, bypass=False)
                self.assertNotEqual(done.returncode, 0)
                self.assertIn("refusing to run", done.stderr)
                self.assertEqual(done.stdout, "")

    def test_the_same_subprocess_runs_when_the_test_bypass_is_set(self):
        done = self.run_tool(["--selftest"], bypass=True)
        self.assertEqual((done.returncode, done.stdout.strip()), (0, "OK"))


if __name__ == "__main__":
    unittest.main()
