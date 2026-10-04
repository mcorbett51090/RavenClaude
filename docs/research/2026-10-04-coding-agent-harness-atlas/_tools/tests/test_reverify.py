import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

os.environ["ATLAS_TEST_ALLOW_ANY_TREE"] = "1"
TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import quotes  # noqa: E402
from reverify import addition_drift, check_quote_presence, scan_changelog  # noqa: E402

URL = "https://example.com/docs"
OLD = "# Docs\n\nThe sandbox is on by default.\nHooks run before a tool call.\n"


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def quote_evidence(eid, quote, text=OLD, url=URL):
    return {"id": eid, "url": url, "sha256": sha(text), "quote": quote}


def span_evidence(eid, text, start, end, url=URL):
    lines = text.split("\n")[start - 1 : end]
    return {
        "id": eid,
        "url": url,
        "sha256": sha(text),
        "quote": "",
        "described_span": {
            "description": "install or update command line (stored as a described span)",
            "raw_line_start": start,
            "raw_line_end": end,
            "span_sha256": sha("\n".join(lines)),
        },
    }


def fresh(text):
    return {URL: {"raw_text": text, "sha256": sha(text)}}


class PresenceTests(unittest.TestCase):
    def test_unchanged_page_is_ok(self):
        out = check_quote_presence([quote_evidence("E-a-00001", "sandbox is on")], fresh(OLD))
        self.assertEqual(out["counts"]["ok"], 1)
        self.assertEqual(out["drifted_ids"], [])
        self.assertEqual(out["page_missing_ids"], [])

    def test_changed_page_with_the_quote_still_present(self):
        new = OLD + "A new paragraph.\n"
        out = check_quote_presence(
            [quote_evidence("E-a-00001", "Hooks run before a tool call.")], fresh(new)
        )
        self.assertEqual(out["counts"]["quote_present"], 1)
        self.assertEqual(out["status_by_id"], {"E-a-00001": "quote_present"})
        self.assertEqual(out["drifted_ids"], [])

    def test_quote_still_present_after_a_line_shift_and_rewrap(self):
        new = "# Docs\n\nIntro added.\n\nThe sandbox is\non by default.\n"
        out = check_quote_presence(
            [quote_evidence("E-a-00001", "The sandbox is on by default.")], fresh(new)
        )
        self.assertEqual(out["counts"]["quote_present"], 1)

    def test_changed_page_without_the_quote_is_drifted(self):
        new = "# Docs\n\nThe sandbox is now off by default.\n"
        out = check_quote_presence(
            [quote_evidence("E-a-00001", "The sandbox is on by default.")], fresh(new)
        )
        self.assertEqual(out["counts"]["drifted"], 1)
        self.assertEqual(out["drifted_ids"], ["E-a-00001"])

    def test_missing_url_is_page_missing(self):
        ev = quote_evidence("E-a-00001", "x", url="https://example.com/gone")
        out = check_quote_presence([ev], fresh(OLD))
        self.assertEqual(out["counts"]["page_missing"], 1)
        self.assertEqual(out["page_missing_ids"], ["E-a-00001"])
        self.assertEqual(out["drifted_ids"], [])

    def test_described_span_unchanged_when_its_lines_still_hash_the_same(self):
        old = "# Install\nfirst\npip install example-tool\nlast\n"
        new = "# Install\nfirst\npip install example-tool\nlast\nappended note\n"
        ev = span_evidence("E-a-00002", old, 3, 3)
        out = check_quote_presence([ev], fresh(new))
        self.assertEqual(out["status_by_id"], {"E-a-00002": "span_unchanged"})
        self.assertEqual(out["counts"]["span_unchanged"], 1)
        self.assertEqual(out["drifted_ids"], [])

    def test_described_span_changed_when_the_lines_differ_or_move(self):
        old = "# Install\nfirst\npip install example-tool\nlast\n"
        edited = "# Install\nfirst\npip install other-tool\nlast\n"
        moved = "# Install\nnew line\nfirst\npip install example-tool\nlast\n"
        gone = "# Install\n"
        for new in (edited, moved, gone):
            out = check_quote_presence([span_evidence("E-a-00002", old, 3, 3)], fresh(new))
            self.assertEqual(out["status_by_id"], {"E-a-00002": "span_changed"}, new)
            self.assertEqual(out["drifted_ids"], ["E-a-00002"])

    def test_a_long_install_line_is_unchanged_until_a_character_past_300_changes(self):
        prefix = "p " * 160  # 320 characters, so the tail is past the 300-character cap
        old = f"# Install\n{prefix}pip install example-tool\nlast\n"
        ev = span_evidence("E-a-00004", old, 2, 2)
        appended = old + "appended note\n"
        out = check_quote_presence([ev], fresh(appended))
        self.assertEqual(out["status_by_id"], {"E-a-00004": "span_unchanged"})
        changed = f"# Install\n{prefix}pip install other-tool\nlast\n"
        out = check_quote_presence([ev], fresh(changed))
        self.assertEqual(out["status_by_id"], {"E-a-00004": "span_changed"})
        self.assertEqual(out["drifted_ids"], ["E-a-00004"])

    def test_the_span_hash_written_by_build_evidence_is_the_one_checked_here(self):
        prefix = "p " * 160
        old = f"# Install\n{prefix}pip install example-tool\r\nlast\n"
        ev, _ = quotes.build_evidence(
            surface="cursor",
            tier="E1",
            url=URL,
            url_effective=URL,
            retrieved="2026-10-04",
            http_status=200,
            raw_bytes_sha256=sha(old),
            raw_bytes_len=len(old),
            product_version=None,
            version_source=None,
            raw_text=old,
            record={"quote": "pip install example-tool", "claim": "c"},
            seq=1,
        )
        self.assertEqual(ev["quote"], "")
        appended = old + "appended note\n"
        out = check_quote_presence([ev], fresh(appended))
        self.assertEqual(out["status_by_id"], {ev["id"]: "span_unchanged"})
        changed = appended.replace("example-tool", "other-tool")
        out = check_quote_presence([ev], fresh(changed))
        self.assertEqual(out["status_by_id"], {ev["id"]: "span_changed"})

    def test_described_span_on_an_unchanged_page_is_ok(self):
        old = "a\nb\n"
        out = check_quote_presence([span_evidence("E-a-00003", old, 2, 2)], fresh(old))
        self.assertEqual(out["counts"]["ok"], 1)

    def test_counts_cover_every_status_and_sum_to_the_input(self):
        newer = OLD + "more\n"
        evidence = [
            quote_evidence("E-a-00001", "sandbox is on"),
            quote_evidence("E-a-00002", "sandbox is on"),
            quote_evidence("E-a-00003", "nothing like this"),
            quote_evidence("E-a-00004", "x", url="https://example.com/gone"),
        ]
        evidence[0]["sha256"] = sha(newer)
        out = check_quote_presence(evidence, fresh(newer))
        self.assertEqual(
            out["counts"],
            {
                "ok": 1,
                "quote_present": 1,
                "span_unchanged": 0,
                "span_changed": 0,
                "drifted": 1,
                "page_missing": 1,
            },
        )
        self.assertEqual(sum(out["counts"].values()), len(evidence))


class AdditionDriftTests(unittest.TestCase):
    def test_added_removed_and_digests(self):
        baseline = ["https://e.com/b", "https://e.com/a", "https://e.com/c"]
        current = ["https://e.com/d", "https://e.com/a", "https://e.com/c"]
        out = addition_drift(baseline, current)
        self.assertEqual(out["added"], ["https://e.com/d"])
        self.assertEqual(out["removed"], ["https://e.com/b"])
        self.assertEqual(out["baseline_sha256"], sha("\n".join(sorted(baseline))))
        self.assertEqual(out["current_sha256"], sha("\n".join(sorted(current))))

    def test_identical_sets_in_any_order_have_equal_digests_and_no_changes(self):
        out = addition_drift(["b", "a"], ["a", "b", "a"])
        self.assertEqual((out["added"], out["removed"]), ([], []))
        self.assertEqual(out["baseline_sha256"], out["current_sha256"])

    def test_added_and_removed_are_sorted(self):
        out = addition_drift(["z", "y"], ["m", "c"])
        self.assertEqual(out["added"], ["c", "m"])
        self.assertEqual(out["removed"], ["y", "z"])


CHANGELOG = """\
Intro text before any dated line mentions sandbox.

## 1.0.0 (2025-12-31)
- old hooks work

## 2026-01-15
- Added sandbox mode
- more detail

- January 20, 2026: hooks now support timeouts
* 3 February 2026 - Fixed a bug in the sandbox
### 2.0.0 (Mar 4, 2026)
Reworked everything about plugins

### 2.1.0 (5th March 2026)
Nothing relevant here
"""


# A bullet that merely mentions a date must not start an entry (review 2, finding 7).
TRAP = """\
## 2026-09-01
- Removed the flag that was deprecated on 2025-01-01
- New hooks API for tool calls
## 2025-06-01
- Superseded by the roadmap item for 2027-01-01
"""


class ChangelogTests(unittest.TestCase):
    def dates(self, since, terms):
        return [
            (e["date"], e["start_line"], e["end_line"])
            for e in scan_changelog(CHANGELOG, since, terms)
        ]

    def test_all_three_date_forms_and_the_version_heading_are_recognized(self):
        self.assertEqual(
            self.dates("2025-12-31", [".*"]),
            [
                ("2026-01-15", 6, 9),
                ("2026-01-20", 10, 10),
                ("2026-02-03", 11, 11),
                ("2026-03-04", 12, 14),
                ("2026-03-05", 15, 16),
            ],
        )

    def test_lines_before_the_first_dated_line_belong_to_no_entry(self):
        entries = scan_changelog(CHANGELOG, "2000-01-01", ["sandbox"])
        self.assertNotIn(1, [e["start_line"] for e in entries])
        self.assertEqual([e["date"] for e in entries], ["2026-01-15", "2026-02-03"])

    def test_an_entry_exactly_on_since_date_is_excluded(self):
        self.assertEqual(self.dates("2026-01-15", ["sandbox"]), [("2026-02-03", 11, 11)])
        self.assertEqual(self.dates("2026-01-14", ["sandbox"])[0][0], "2026-01-15")

    def test_only_newer_entries_with_a_matching_term_are_returned(self):
        self.assertEqual(self.dates("2026-01-15", ["plugins"]), [("2026-03-04", 12, 14)])
        self.assertEqual(self.dates("2026-01-15", ["no such term"]), [])

    def test_result_fields_and_matched_terms(self):
        entries = scan_changelog(CHANGELOG, "2026-01-15", ["SANDBOX", "bug", "timeouts"])
        self.assertEqual(
            entries,
            [
                {
                    "date": "2026-01-20",
                    "start_line": 10,
                    "end_line": 10,
                    "matched_terms": ["timeouts"],
                    "first_line": "- January 20, 2026: hooks now support timeouts",
                },
                {
                    "date": "2026-02-03",
                    "start_line": 11,
                    "end_line": 11,
                    "matched_terms": ["SANDBOX", "bug"],
                    "first_line": "* 3 February 2026 - Fixed a bug in the sandbox",
                },
            ],
        )

    def test_entry_runs_to_the_next_dated_line_including_undated_lines(self):
        entries = scan_changelog(CHANGELOG, "2026-01-01", ["more detail"])
        self.assertEqual([(e["start_line"], e["end_line"]) for e in entries], [(6, 9)])

    def test_the_last_entry_ends_at_the_last_line_without_a_phantom_line(self):
        entries = scan_changelog("# 2026-05-01\nbody\nlast\n", "2026-01-01", ["last"])
        self.assertEqual([(e["start_line"], e["end_line"]) for e in entries], [(1, 3)])

    def test_an_invalid_calendar_date_does_not_start_an_entry(self):
        text = "## 2026-13-45\nsandbox\n## 2026-02-01\nsandbox\n"
        entries = scan_changelog(text, "2026-01-01", ["sandbox"])
        self.assertEqual(
            [(e["date"], e["start_line"], e["end_line"]) for e in entries], [("2026-02-01", 3, 4)]
        )

    def test_lone_carriage_returns_and_crlf_are_line_breaks(self):
        for text in ("# 2026-05-01\rbody\rlast\r", "# 2026-05-01\r\nbody\r\nlast\r\n"):
            entries = scan_changelog(text, "2026-01-01", ["last"])
            self.assertEqual([(e["start_line"], e["end_line"]) for e in entries], [(1, 3)], text)
            self.assertEqual(entries[0]["first_line"], "# 2026-05-01")
        mixed = "# 2026-01-01\rold\r\n# 2026-05-01\nnew sandbox\r"
        entries = scan_changelog(mixed, "2026-02-01", ["sandbox"])
        self.assertEqual([(e["date"], e["start_line"], e["end_line"]) for e in entries], [("2026-05-01", 3, 4)])

    def test_a_bullet_that_mentions_a_date_does_not_start_an_entry(self):
        entries = scan_changelog(TRAP, "2026-01-01", ["hooks"])
        self.assertEqual(
            [(e["date"], e["start_line"], e["end_line"]) for e in entries], [("2026-09-01", 1, 3)]
        )
        self.assertEqual(entries[0]["matched_terms"], ["hooks"])
        everything = scan_changelog(TRAP, "2000-01-01", [".*"])
        self.assertEqual(
            [(e["date"], e["start_line"], e["end_line"]) for e in everything],
            [("2026-09-01", 1, 3), ("2025-06-01", 4, 5)],
        )
        self.assertEqual(scan_changelog(TRAP, "2026-09-01", [".*"]), [])

    def test_a_date_that_leads_the_bullet_starts_an_entry(self):
        text = (
            "- v1.2.3 - 2026-09-01: sandbox mode\n"
            "- **2026-09-02** sandbox again\n"
            "1. September 3, 2026 sandbox third\n"
            "* 4 September 2026 - sandbox fourth\n"
            "- **v2.0** (2026-09-05) sandbox fifth\n"
            "- 1.2.3: 2026-09-06 sandbox sixth\n"
            "- Fixed a regression introduced on 2026-09-07 in the sandbox\n"
        )
        entries = scan_changelog(text, "2026-01-01", ["sandbox"])
        self.assertEqual(
            [(e["date"], e["start_line"], e["end_line"]) for e in entries],
            [
                ("2026-09-01", 1, 1),
                ("2026-09-02", 2, 2),
                ("2026-09-03", 3, 3),
                ("2026-09-04", 4, 4),
                ("2026-09-05", 5, 5),
                ("2026-09-06", 6, 7),
            ],
        )

    def test_a_word_before_the_date_in_a_bullet_is_a_mention_not_a_start(self):
        text = "## 2026-02-01\n- Released 2026-09-01 as planned\n- see 3 March 2026 notes\n"
        entries = scan_changelog(text, "2026-01-01", ["notes"])
        self.assertEqual([(e["date"], e["end_line"]) for e in entries], [("2026-02-01", 3)])

    def test_a_heading_with_a_date_anywhere_still_starts_an_entry(self):
        text = "## Release notes for the 2026-09-01 build\nsandbox\n"
        entries = scan_changelog(text, "2026-01-01", ["sandbox"])
        self.assertEqual([e["date"] for e in entries], ["2026-09-01"])

    def test_bare_date_lines_and_table_rows_start_entries(self):
        text = "**September 15, 2026**\nsandbox arrived\n| 2026-09-20 | sandbox fixed |\n"
        entries = scan_changelog(text, "2026-01-01", ["sandbox"])
        self.assertEqual([e["date"] for e in entries], ["2026-09-15", "2026-09-20"])

    def test_a_date_in_the_middle_of_a_prose_line_does_not_start_an_entry(self):
        text = "## 2026-02-01\nShipped on the way to 2026-06-01 as planned, sandbox.\n"
        entries = scan_changelog(text, "2026-01-01", ["sandbox"])
        self.assertEqual([(e["start_line"], e["end_line"]) for e in entries], [(1, 2)])

    def test_month_name_variants(self):
        for line, expected in (
            ("## Sept 9, 2026", "2026-09-09"),
            ("## 9 Sep 2026", "2026-09-09"),
            ("## December 1st, 2026", "2026-12-01"),
            ("- 31 JANUARY 2027", "2027-01-31"),
            ("- Feb. 2, 2026", "2026-02-02"),
        ):
            entries = scan_changelog(line + "\ntext\n", "2020-01-01", ["text"])
            self.assertEqual([e["date"] for e in entries], [expected], line)

    def test_invalid_inputs_raise_value_error(self):
        with self.assertRaises(ValueError):
            scan_changelog(CHANGELOG, "not-a-date", ["x"])
        with self.assertRaises(ValueError):
            scan_changelog(CHANGELOG, "2026-01-01", ["(unclosed"])


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOLS / "reverify.py"), *args],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "ATLAS_TEST_ALLOW_ANY_TREE": "1"},
        )

    def test_selftest_prints_ok(self):
        out = self.run_cli("--selftest")
        self.assertEqual((out.returncode, out.stdout.strip()), (0, "OK"), out.stderr)

    def test_presence_addition_and_changelog_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            new = OLD + "extra\n"
            (tmp / "page.md").write_bytes(new.encode("utf-8"))
            (tmp / "evidence.json").write_text(
                json.dumps([quote_evidence("E-a-00001", "sandbox is on")]), encoding="utf-8"
            )
            (tmp / "pages.json").write_text(
                json.dumps({URL: {"raw_path": str(tmp / "page.md")}}), encoding="utf-8"
            )
            presence = self.run_cli(
                "presence",
                "--evidence",
                str(tmp / "evidence.json"),
                "--pages",
                str(tmp / "pages.json"),
            )
            self.assertEqual(presence.returncode, 0, presence.stderr)
            self.assertEqual(json.loads(presence.stdout)["counts"]["quote_present"], 1)

            (tmp / "base.txt").write_text("https://a\nhttps://b\n", encoding="utf-8")
            (tmp / "cur.txt").write_text("https://b\n\nhttps://c\n", encoding="utf-8")
            addition = self.run_cli(
                "addition", "--baseline", str(tmp / "base.txt"), "--current", str(tmp / "cur.txt")
            )
            self.assertEqual(addition.returncode, 0, addition.stderr)
            got = json.loads(addition.stdout)
            self.assertEqual((got["added"], got["removed"]), (["https://c"], ["https://a"]))

            (tmp / "log.md").write_text(CHANGELOG, encoding="utf-8")
            changelog = self.run_cli(
                "changelog",
                "--raw",
                str(tmp / "log.md"),
                "--since",
                "2026-01-15",
                "--term",
                "plugins",
            )
            self.assertEqual(changelog.returncode, 0, changelog.stderr)
            self.assertEqual([e["date"] for e in json.loads(changelog.stdout)], ["2026-03-04"])

            bad = self.run_cli(
                "changelog", "--raw", str(tmp / "log.md"), "--since", "nope", "--term", "x"
            )
            self.assertEqual(bad.returncode, 2)


if __name__ == "__main__":
    unittest.main()
