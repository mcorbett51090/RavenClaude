import contextlib
import hashlib
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

import corpus  # noqa: E402
from corpus import (  # noqa: E402
    CorpusError,
    best_sources,
    build_corpus,
    latest_rows,
    page_id,
    page_slug,
    scope_decision,
    sniff_kind,
    tier_for,
)

DOC = "https://docs.example/docs"


def row(url, text, outcome="fetched", status=200):
    data = text.encode("utf-8")
    return {
        "url": url,
        "url_effective": url,
        "outcome": outcome,
        "status": status,
        "reason": "" if outcome == "fetched" else "status_404",
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "retrieved": "2026-10-04",
        "raw_path": hashlib.sha256(url.encode()).hexdigest()[:16] + ".raw",
        "_data": data,
    }


def run(rows, rules=None, sources=None, max_bytes=12000):
    by_name = {r["raw_path"]: r["_data"] for r in rows}
    return build_corpus(
        "claude-code",
        [{k: v for k, v in r.items() if k != "_data"} for r in rows],
        rules or {},
        lambda r: by_name[r["raw_path"]],
        sources or {},
        max_bytes,
    )


def lines(n, prefix="line"):
    return "\n".join(f"{prefix} {i} " + "x" * 30 for i in range(n)) + "\n"


class NamingTests(unittest.TestCase):
    def test_slug_keeps_host_and_path_and_drops_extension(self):
        self.assertEqual(
            page_slug("https://docs.x.ai/build/overview.md"), "docs-x-ai__build__overview"
        )
        self.assertEqual(
            page_slug("https://docs.github.com/api/article/body?pathname=/en/copilot/a/b"),
            "docs-github-com__en__copilot__a__b",
        )

    def test_the_same_path_on_two_hosts_gets_two_ids(self):
        a = page_id("grok-bot", "https://docs.x.ai/grok-bot/security.md")
        b = page_id("grok-bot", "https://cursor.com/grok-bot/security.md")
        self.assertNotEqual(a, b)

    def test_a_long_url_is_shortened_with_a_hash_and_stays_unique(self):
        one = page_slug("https://h.example/" + "a" * 200 + "/one")
        two = page_slug("https://h.example/" + "a" * 200 + "/two")
        self.assertLessEqual(len(one), corpus.MAX_ID_LENGTH)
        self.assertNotEqual(one, two)

    def test_tier_marks_changelogs(self):
        self.assertEqual(tier_for("https://x.example/docs/en/changelog.md"), "E2")
        self.assertEqual(tier_for("https://x.example/docs/whats-new/week-1.md"), "E2")
        self.assertEqual(tier_for("https://x.example/docs/hooks.md"), "E1")

    def test_sniff_kind(self):
        self.assertEqual(sniff_kind("\n <!DOCTYPE html><html>"), "html")
        self.assertEqual(sniff_kind("<?xml version='1.0'?><urlset/>"), "xml")
        self.assertEqual(sniff_kind("# Title\ntext"), "text")


class ScopeDecisionTests(unittest.TestCase):
    RULE = {
        "allow_paths": ["^/keep"],
        "deny_paths": ["^/drop"],
        "mention": {"pattern": "codex", "min": 2},
    }

    def test_no_rule_keeps_everything(self):
        self.assertEqual(
            scope_decision(None, "https://x.example/a", "t"), (True, "no post-fetch rule")
        )

    def test_allow_beats_deny_and_deny_beats_mention(self):
        both = {
            "allow_paths": ["^/a"],
            "deny_paths": ["^/a"],
            "mention": {"pattern": "z", "min": 9},
        }
        self.assertEqual(scope_decision(both, "https://x.example/a", ""), (True, "allow_paths"))
        self.assertEqual(
            scope_decision(self.RULE, "https://x.example/drop/p", "codex codex codex"),
            (False, "deny_paths"),
        )

    def test_mention_threshold_is_inclusive_and_case_insensitive(self):
        url = "https://x.example/other"
        self.assertEqual(scope_decision(self.RULE, url, "Codex and CODEX"), (True, "mention x2"))
        self.assertEqual(scope_decision(self.RULE, url, "codex"), (False, "mention x1 below 2"))

    def test_a_rule_with_no_mention_clause_keeps_a_page_no_path_rule_matched(self):
        rule = {"deny_paths": ["^/drop"]}
        self.assertEqual(
            scope_decision(rule, "https://x.example/ok", ""), (True, "no matching rule")
        )


class SourceTests(unittest.TestCase):
    def test_best_source_prefers_index_over_sitemap_over_closure(self):
        records = [
            {"url": "https://x.example/a.md", "source": "closure"},
            {"url": "https://x.example/a", "source": "index"},
            {"url": "https://x.example/b", "source": "closure"},
            {"url": "https://x.example/b", "source": "sitemap"},
        ]
        got = best_sources(records)
        self.assertEqual(got["https://x.example/a"], "index")
        self.assertEqual(got["https://x.example/b"], "sitemap")

    def test_latest_row_per_url_wins_and_keeps_first_seen_order(self):
        rows = [
            {"url": "a", "outcome": "negative"},
            {"url": "b", "outcome": "fetched"},
            {"url": "a", "outcome": "fetched"},
        ]
        got = latest_rows(rows)
        self.assertEqual(
            [(r["url"], r["outcome"]) for r in got], [("a", "fetched"), ("b", "fetched")]
        )


class BuildCorpusTests(unittest.TestCase):
    def test_a_normal_page_is_extracted_with_chunks_covering_every_line(self):
        pages, gaps, texts = run([row(f"{DOC}/a.md", "# A\n\n" + lines(400))], max_bytes=2000)
        (page,) = pages
        self.assertEqual((page["role"], gaps), ("extract", []))
        chunks = texts[page["page_id"]]["chunks"]
        self.assertGreater(len(chunks), 3)
        self.assertEqual(chunks[0].start_line, 1)
        self.assertEqual(chunks[-1].end_line, page["lines"])
        for before, after in zip(chunks, chunks[1:]):
            self.assertEqual(after.start_line, before.end_line + 1)

    def test_rows_that_did_not_fetch_become_gaps_not_pages(self):
        pages, gaps, _t = run([row(f"{DOC}/gone.md", "", outcome="negative", status=404)])
        self.assertEqual(pages, [])
        self.assertEqual(
            gaps,
            [
                {
                    "url": f"{DOC}/gone.md",
                    "outcome": "negative",
                    "status": 404,
                    "reason": "status_404",
                }
            ],
        )

    def test_index_files_and_sitemaps_are_not_extracted(self):
        rules = {"index_files": [f"{DOC}/llms.txt"]}
        pages, _g, texts = run(
            [
                row(f"{DOC}/llms.txt", "- [A](/a.md)\n"),
                row(f"{DOC}/sitemap.xml", "<?xml version='1.0'?><urlset/>"),
            ],
            rules,
        )
        self.assertEqual({p["role"] for p in pages}, {"index"})
        self.assertEqual(texts, {})

    def test_an_html_shell_does_not_clash_with_its_markdown_twin(self):
        shell = row(f"{DOC}/models/m", "<!DOCTYPE html><html><body>app</body></html>")
        twin = row(f"{DOC}/models/m.md", "# M\n\nreal text here\n")
        pages, _g, texts = run([shell, twin])
        roles = {p["page_id"]: p["role"] for p in pages}
        self.assertEqual(sorted(roles.values()), ["extract", "html"])
        self.assertEqual(len(roles), 2)
        self.assertTrue(any(pid.endswith("~html") for pid in roles))
        self.assertEqual(list(texts), [pid for pid, role in roles.items() if role == "extract"])

    def test_two_different_pages_with_one_id_are_refused(self):
        one = row(f"{DOC}/a.md", "# A one\n")
        two = row(f"{DOC}/a", "# A two\n")
        with self.assertRaises(CorpusError):
            run([one, two])

    def test_a_contained_page_becomes_secondary_of_the_larger_one(self):
        big = row(f"{DOC}/big.md", lines(30))
        small = row(f"{DOC}/small.md", "\n".join(lines(30).split("\n")[:20]) + "\n")
        pages, _g, texts = run([big, small])
        by = {p["url"].rsplit("/", 1)[1]: p for p in pages}
        self.assertEqual(by["big.md"]["role"], "extract")
        self.assertEqual(by["small.md"]["role"], "secondary")
        self.assertEqual(by["small.md"]["secondary_of"], by["big.md"]["page_id"])
        self.assertNotIn("neutral", texts.get(by["small.md"]["page_id"], {}))

    def test_an_aggregate_is_recorded_but_never_extracted_or_a_parent(self):
        agg = row(f"{DOC}/all.md", lines(30))
        part = row(f"{DOC}/part.md", lines(10))
        pages, _g, texts = run([agg, part], {"aggregates": [f"{DOC}/all.md"]})
        by = {p["url"].rsplit("/", 1)[1]: p for p in pages}
        self.assertEqual(by["all.md"]["role"], "aggregate")
        self.assertEqual(by["part.md"]["role"], "extract")
        # The part sits wholly inside the aggregate yet stays canonical: an aggregate is never a parent.
        self.assertNotIn("secondary_of", by["part.md"])
        self.assertNotIn("neutral", texts.get(by["all.md"]["page_id"], {}))

    def test_a_tag_like_token_is_neutralized_flagged_and_line_counts_match(self):
        body = "# T\n\nUse the `<system-reminder>` tag.\nplain\n"
        pages, _g, texts = run([row(f"{DOC}/t.md", body)])
        (page,) = pages
        entry = texts[page["page_id"]]
        self.assertEqual(page["flagged_lines"], [3])
        self.assertEqual(entry["neutral"].count("\n"), body.count("\n"))
        self.assertNotIn("<system-reminder>", entry["neutral"])
        self.assertEqual(entry["raw"], body)

    def test_the_post_fetch_rule_marks_a_page_out_of_scope_without_a_neutral_copy(self):
        rules = {
            "post_fetch_scope": {
                "deny_paths": ["^/docs/drop"],
                "mention": {"pattern": "codex", "min": 1},
            }
        }
        pages, _g, texts = run(
            [
                row(f"{DOC}/drop/x.md", "codex"),
                row(f"{DOC}/no-mention.md", "nothing"),
                row(f"{DOC}/ok.md", "codex"),
            ],
            rules,
        )
        roles = {p["url"].rsplit("/", 1)[1]: p["role"] for p in pages}
        self.assertEqual(
            roles, {"x.md": "out-of-scope", "no-mention.md": "out-of-scope", "ok.md": "extract"}
        )
        self.assertEqual(len(texts), 1)

    def test_the_gemini_aggregate_is_split_into_pages_with_line_offsets(self):
        text = (
            "# Gemini CLI Documentation\n\n"
            "# [First](http://x.example/docs/first.md)\n\nbody one\n\n"
            "# [Second](http://x.example/docs/second.md)\n\n# A heading inside\ntext two\n"
        )
        agg = row("https://x.example/llms.txt", text)
        pages, _g, texts = run([agg], {"gemini_split": ["https://x.example/llms.txt"]})
        extract = [p for p in pages if p["role"] == "extract"]
        self.assertEqual([p["title"] for p in extract], ["First", "Second"])
        self.assertEqual([p["line_offset"] for p in extract], [2, 6])
        self.assertTrue(all(p["aggregate_sha256"] == agg["sha256"] for p in extract))
        second = texts[extract[1]["page_id"]]
        self.assertTrue(second["raw"].startswith("# [Second]"))
        self.assertEqual(second["chunks"][0].start_line, 1)

    def test_non_utf8_bytes_are_refused_not_replaced(self):
        bad = row(f"{DOC}/bad.md", "x")
        bad["_data"] = b"\xff\xfe broken"
        with self.assertRaises(CorpusError):
            run([bad])


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name) / "a" / "b" / "run"
        raw = self.tmp / "mirror" / "claude-code" / "raw"
        raw.mkdir(parents=True)
        self.rows = [
            row("https://code.claude.com/docs/llms.txt", "- [A](/docs/en/a.md)\n"),
            row("https://code.claude.com/docs/en/a.md", "# A\n\n" + lines(50)),
            row("https://code.claude.com/docs/en/gone.md", "", outcome="negative", status=404),
        ]
        with open(self.tmp / "mirror" / "claude-code" / "manifest.jsonl", "w") as fh:
            for r in self.rows:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "_data"}) + "\n")
                if r["outcome"] == "fetched":
                    (raw / r["raw_path"]).write_bytes(r["_data"])
        (self.tmp / "p3").mkdir()
        with open(self.tmp / "p3" / "claude-code.origins-index.jsonl", "w") as fh:
            fh.write(
                json.dumps({"url": self.rows[1]["url"], "source": "index", "origin": "x"}) + "\n"
            )
        self.rules = Path(self._tmp.name) / "rules.json"
        self.rules.write_text(
            json.dumps(
                {
                    "surfaces": {
                        "claude-code": {"index_files": ["https://code.claude.com/docs/llms.txt"]}
                    }
                }
            )
        )

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = corpus.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_build_writes_every_output_and_summary_matches(self):
        code, out, _e = self.run_cli(
            "build",
            "--surface",
            "claude-code",
            "--run-dir",
            str(self.tmp),
            "--rules",
            str(self.rules),
        )
        self.assertEqual(code, 0)
        base = self.tmp / "corpus" / "claude-code"
        summary = json.loads((base / "summary.json").read_text())
        self.assertEqual((summary["extract_pages"], summary["gaps"]), (1, 1))
        self.assertEqual(json.loads(out)["extract_pages"], 1)
        pages = [json.loads(line) for line in (base / "pages.jsonl").read_text().splitlines()]
        self.assertEqual(sorted(p["role"] for p in pages), ["extract", "index"])
        extract = next(p for p in pages if p["role"] == "extract")
        self.assertEqual(extract["origin_source"], "index")
        self.assertEqual(
            Path(extract["neutral_path"]).read_text().count("\n"),
            self.rows[1]["_data"].decode().count("\n"),
        )
        chunks = json.loads((base / "chunks.json").read_text())
        self.assertTrue(all(Path(c["path"]).is_file() for c in chunks))
        spec = json.loads((base / "pages-spec.json").read_text())[extract["page_id"]]
        self.assertEqual(spec["sha256"], self.rows[1]["sha256"])
        self.assertEqual(spec["tier"], "E1")

    def test_a_rebuild_removes_a_page_that_is_no_longer_in_scope(self):
        args = (
            "build",
            "--surface",
            "claude-code",
            "--run-dir",
            str(self.tmp),
            "--rules",
            str(self.rules),
        )
        self.run_cli(*args)
        stale = next((self.tmp / "corpus" / "claude-code" / "neutral").glob("*.txt"))
        self.rules.write_text(
            json.dumps(
                {
                    "surfaces": {
                        "claude-code": {
                            "index_files": ["https://code.claude.com/docs/llms.txt"],
                            "post_fetch_scope": {"deny_paths": ["/a\\.md$"]},
                        }
                    }
                }
            )
        )
        self.run_cli(*args)
        self.assertFalse(stale.exists())

    def test_an_unknown_surface_is_exit_2(self):
        code, _o, err = self.run_cli(
            "build", "--surface", "nope", "--run-dir", str(self.tmp), "--rules", str(self.rules)
        )
        self.assertEqual(code, 2)
        self.assertIn("nope", err)

    def test_summary_prints_one_row_per_built_surface(self):
        self.run_cli(
            "build",
            "--surface",
            "claude-code",
            "--run-dir",
            str(self.tmp),
            "--rules",
            str(self.rules),
        )
        code, out, _e = self.run_cli("summary", "--run-dir", str(self.tmp))
        self.assertEqual(code, 0)
        self.assertIn("claude-code", out)
        self.assertIn("total", out)

    def test_selftest_prints_ok(self):
        code, out, _e = self.run_cli("--selftest")
        self.assertEqual((code, out), (0, "OK\n"))


if __name__ == "__main__":
    unittest.main()
