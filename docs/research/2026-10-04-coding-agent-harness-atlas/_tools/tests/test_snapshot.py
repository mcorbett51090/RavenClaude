import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ["ATLAS_TEST_ALLOW_ANY_TREE"] = "1"
TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import snapshot  # noqa: E402
from discover import url_set_digest  # noqa: E402
from snapshot import (  # noqa: E402
    SnapshotError,
    collect_versions,
    compact_manifest,
    coverage_metrics,
    first_changelog_date,
    index_hashes,
    merged_origins,
    npm_version,
    split_origins,
    split_rows,
    unmatched_origins,
    url_set_for,
    vscode_version,
)


class VersionParsingTests(unittest.TestCase):
    def test_npm_version_keeps_only_the_named_tags(self):
        tags = '{"latest":"1.2.3","stable":"1.2.0","beta":"0.1","alpha":"0.2"}'
        version, kept = npm_version('{"version":"1.2.3"}', tags)
        self.assertEqual(version, "1.2.3")
        self.assertEqual(kept, {"latest": "1.2.3", "stable": "1.2.0"})

    def test_an_npm_answer_without_a_version_is_an_error(self):
        with self.assertRaises(SnapshotError):
            npm_version('{"name":"p"}', "{}")

    def test_vscode_version_comes_from_the_release_url_only(self):
        self.assertEqual(vscode_version("https://code.visualstudio.com/updates/v1_140"), "1.140")
        self.assertIsNone(vscode_version("https://code.visualstudio.com/updates"))
        self.assertIsNone(vscode_version(None))

    def test_the_first_changelog_date_ignores_script_and_markup(self):
        html = (
            "<script>var d='Jan 1, 2020'</script><h1>What&#x27;s new</h1>"
            "<p>Sep 23, 2026 &middot; Changelog</p><p>Aug 2, 2026</p>"
        )
        self.assertEqual(first_changelog_date(html), "2026-09-23")
        self.assertIsNone(first_changelog_date("<p>no dates here</p>"))


class UrlSetTests(unittest.TestCase):
    RULES = {
        "index_files": ["https://x.example/llms.txt"],
        "gemini_split": ["https://g.example/llms.txt"],
    }

    def row(self, url, effective=None):
        return {
            "url": url,
            "url_effective": effective or url,
            "outcome": "fetched",
            "raw_path": "r",
        }

    def test_each_file_shape_yields_its_urls(self):
        llms = "- [A](/a.md)\n- [B](https://x.example/b.md)\n"
        self.assertEqual(
            url_set_for(self.row("https://x.example/llms.txt"), llms, self.RULES),
            ["https://x.example/a.md", "https://x.example/b.md"],
        )
        xml = (
            '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>https://x.example/p</loc></url></urlset>"
        )
        self.assertEqual(
            url_set_for(self.row("https://x.example/sitemap.xml"), xml, self.RULES),
            ["https://x.example/p"],
        )
        page_list = "/en\n/en/a\nnot a path\n"
        self.assertEqual(
            url_set_for(self.row("https://d.example/api/pagelist/en/x"), page_list, self.RULES),
            ["https://d.example/en", "https://d.example/en/a"],
        )
        gemini = "# Doc\n\n# [One](http://g.example/docs/one.md)\n\ntext\n"
        self.assertEqual(
            url_set_for(self.row("https://g.example/llms.txt"), gemini, self.RULES),
            ["http://g.example/docs/one.md"],
        )

    def test_index_hashes_cover_index_and_sitemap_files_and_not_pages(self):
        files = {
            "llms": "- [A](/a.md)\n",
            "sm": '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/a</loc></url></urlset>',
            "page": "# A page\n",
        }
        rows = [
            {"url": "https://x.example/llms.txt", "outcome": "fetched", "raw_path": "llms"},
            {"url": "https://x.example/sitemap.xml", "outcome": "fetched", "raw_path": "sm"},
            {"url": "https://x.example/a.md", "outcome": "fetched", "raw_path": "page"},
            {"url": "https://x.example/gone", "outcome": "negative", "raw_path": ""},
        ]
        got = index_hashes("s", rows, self.RULES, lambda r: files[r["raw_path"]].encode())
        self.assertEqual(
            sorted(got), ["https://x.example/llms.txt", "https://x.example/sitemap.xml"]
        )
        self.assertEqual(
            got["https://x.example/llms.txt"]["sha256"], url_set_digest(["https://x.example/a.md"])
        )
        # the page and the sitemap name one page in two spellings: the digests agree
        self.assertEqual(
            got["https://x.example/llms.txt"]["sha256"],
            got["https://x.example/sitemap.xml"]["sha256"],
        )


class CoverageTests(unittest.TestCase):
    def test_pages_are_counted_by_their_origin_and_only_page_roles_count(self):
        roles = {
            r: {"pages": 0, "bytes": 0}
            for r in (
                "extract",
                "secondary",
                "aggregate",
                "index",
                "excluded",
                "html",
                "out-of-scope",
            )
        }
        roles["extract"] = {"pages": 2, "bytes": 4096}
        summary = {
            "roles": roles,
            "extract_pages": 2,
            "extract_bytes": 4096,
            "extract_chunks": 5,
            "flagged_lines": 1,
        }
        pages = [
            {"role": "extract", "origin_source": "index"},
            {"role": "extract", "origin_source": "closure"},
            {"role": "index", "origin_source": "index"},
            {"role": "html", "origin_source": "closure"},
            {"role": "aggregate", "origin_source": "index"},
        ]
        got = coverage_metrics(summary, pages, [{"url": "u"}], {"f": {}})
        self.assertEqual(got["pages found by index"], 1)
        self.assertEqual(got["pages found only by link closure"], 1)
        self.assertEqual(got["fetches that returned nothing usable"], 1)
        self.assertEqual(got["extraction text (KB)"], 4)


class CollectVersionsTests(unittest.TestCase):
    def test_every_source_kind_produces_a_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            surfaces = [
                {"id": "a", "version_source": {"kind": "npm", "package": "@v/a"}},
                {
                    "id": "b",
                    "version_source": {"kind": "release-notes", "url": "https://b.example/updates"},
                },
                {
                    "id": "c",
                    "version_source": {
                        "kind": "changelog-html",
                        "url": "https://c.example/changelog",
                    },
                },
                {"id": "d", "version_source": {"kind": "hosted-service"}},
                {"id": "e", "version_source": {"kind": "unknown"}},
            ]
            for entry in surfaces:
                (run / "mirror" / entry["id"] / "raw").mkdir(parents=True)
                (run / "mirror" / entry["id"] / "version").mkdir()
            (run / "mirror" / "a" / "version" / "npm-latest.json").write_text('{"version":"9.9.9"}')
            (run / "mirror" / "a" / "version" / "npm-dist-tags.json").write_text(
                '{"latest":"9.9.9"}'
            )
            (run / "mirror" / "c" / "raw" / "c.raw").write_text("<p>Sep 23, 2026</p>")
            manifests = {
                "a": [
                    {"url": "https://a.example/x", "outcome": "fetched", "retrieved": "2026-10-04"}
                ],
                "b": [
                    {
                        "url": "https://b.example/updates",
                        "url_effective": "https://b.example/updates/v1_140",
                        "outcome": "fetched",
                        "retrieved": "2026-10-04",
                    }
                ],
                "c": [
                    {
                        "url": "https://c.example/changelog",
                        "outcome": "fetched",
                        "raw_path": "c.raw",
                        "retrieved": "2026-10-03",
                    }
                ],
                "d": [],
                "e": [],
            }
            for sid, rows in manifests.items():
                (run / "mirror" / sid / "manifest.jsonl").write_text(
                    "".join(json.dumps(r) + "\n" for r in rows)
                )
            got = {r["surface"]: r for r in collect_versions(run, surfaces)}
            self.assertEqual(got["a"]["version"], "9.9.9")
            self.assertIn("@v/a", got["a"]["version_source"])
            self.assertEqual(got["b"]["version"], "1.140")
            self.assertEqual(got["c"]["version"], "changelog entry 2026-09-23")
            self.assertEqual(got["c"]["retrieved"], "2026-10-03")
            self.assertIsNone(got["d"]["version"])
            self.assertIn("hosted service", got["d"]["version_source"])
            self.assertIsNone(got["e"]["version"])
            self.assertIsNone(got["e"]["retrieved"])


class RecordTests(unittest.TestCase):
    def test_compact_manifest_drops_the_local_file_name_and_sorts_by_url(self):
        rows = [
            {"url": "https://b.example/", "outcome": "fetched", "raw_path": "x.raw", "sha256": "ab", "bytes": 1},
            {"url": "https://a.example/", "outcome": "negative", "raw_path": "", "status": 404},
        ]
        got = compact_manifest(rows)
        self.assertEqual([r["url"] for r in got], ["https://a.example/", "https://b.example/"])
        self.assertTrue(all("raw_path" not in r for r in got))
        self.assertEqual(got[1]["sha256"], "ab")

    def test_merged_origins_skips_work_files_and_removes_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            p3 = Path(tmp) / "p3"
            p3.mkdir()
            one = {"url": "https://x.example/a", "source": "index", "origin": "o"}
            two = {"url": "https://x.example/b", "source": "closure", "origin": "o"}
            (p3 / "s.origins-index.jsonl").write_text(json.dumps(one) + "\n")
            (p3 / "s.origins-closure.jsonl").write_text(json.dumps(one) + "\n" + json.dumps(two) + "\n")
            (p3 / "s.origins-closure-raw.jsonl").write_text(json.dumps({"url": "https://x.example/z", "source": "closure", "origin": "o"}) + "\n")
            (p3 / "s.origins-sitemap-all.jsonl").write_text(json.dumps({"url": "https://x.example/y", "source": "sitemap", "origin": "o"}) + "\n")
            got = merged_origins(tmp, "s")
        self.assertEqual([r["url"] for r in got], ["https://x.example/a", "https://x.example/b"])


class SplitAndCoverageTests(unittest.TestCase):
    PAGES = [
        {
            "page_id": "g__a",
            "aggregate_page_id": "g",
            "source_page_url": "http://g.example/docs/a.md",
            "url": "https://g.example/llms.txt",
            "bytes": 10,
            "slice_sha256": "ab" * 32,
            "retrieved": "2026-10-04",
        },
        {"page_id": "g", "url": "https://g.example/llms.txt", "bytes": 99},
    ]

    def test_split_pages_get_derived_rows_and_origins_on_the_https_url(self):
        (row,) = split_rows(self.PAGES)
        self.assertEqual(row["url"], "https://g.example/docs/a.md")
        self.assertEqual(row["listed_as"], "http://g.example/docs/a.md")
        self.assertEqual((row["outcome"], row["status"], row["sha256"]), ("split-from-aggregate", 200, "ab" * 32))
        (origin,) = split_origins(self.PAGES)
        self.assertEqual((origin["source"], origin["origin"]), ("index", "https://g.example/llms.txt"))

    def test_an_origin_without_a_manifest_row_is_reported_by_canonical_url(self):
        origins = [{"url": "https://x.example/a"}, {"url": "https://x.example/b/"}, {"url": "https://x.example/c"}]
        rows = [{"url": "https://x.example/a.md"}, {"url": "https://x.example/b"}]
        self.assertEqual(unmatched_origins(origins, rows), ["https://x.example/c"])


class CliTests(unittest.TestCase):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = snapshot.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_build_without_a_corpus_is_exit_2_and_names_the_missing_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            versions = Path(tmp) / "versions.json"
            versions.write_text(
                json.dumps(
                    {
                        "versions": [
                            {
                                "surface": s,
                                "retrieved": "2026-10-04",
                                "version": None,
                                "version_source": None,
                            }
                            for s in snapshot.SURFACE_IDS
                        ]
                    }
                )
            )
            code, _o, err = self.run_cli(
                "build", "--run-dir", tmp, "--versions", str(versions), "--out", str(Path(tmp) / "s.json"),
                "--enum-dir", str(Path(tmp) / "enum"),
            )  # fmt: skip
        self.assertEqual(code, 2)
        self.assertIn("corpus.py build", err)

    def test_selftest_prints_ok(self):
        code, out, _e = self.run_cli("--selftest")
        self.assertEqual((code, out), (0, "OK\n"))


if __name__ == "__main__":
    unittest.main()
