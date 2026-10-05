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

import sweep as sweep_module  # noqa: E402
from sweep import SweepBlindError, sweep  # noqa: E402

PAGES = {
    "overview": "Welcome to the tool\nHooks run before a tool call\n",
    "excluded-changelog": "# Changelog\nAdded the sandbox setting\nFixed a bug\n",
    "reference": "Settings\r\nsandbox: true\r\nhooks: []\r\n",
}


class SweepTests(unittest.TestCase):
    def test_a_positive_control_absent_from_the_corpus_raises(self):
        with self.assertRaises(SweepBlindError) as ctx:
            sweep(PAGES, ["sandbox"], "no-such-control-term")
        self.assertIn("could not have returned anything", str(ctx.exception))

    def test_a_blind_probe_never_returns_a_zero_hit_result(self):
        with self.assertRaises(SweepBlindError):
            sweep(PAGES, ["term-with-no-hits"], "no-such-control-term")

    def test_zero_hits_with_a_live_control_is_a_valid_result(self):
        result = sweep(PAGES, ["telemetry"], "hooks")
        self.assertEqual(result["hit_count"], 0)
        self.assertEqual(result["hits"], [])
        self.assertEqual(result["positive_control_hits"], 2)
        self.assertEqual(result["positive_control_term"], "hooks")
        self.assertEqual(result["terms"], ["telemetry"])
        self.assertEqual(result["pages_scanned"], 3)

    def test_excluded_pages_are_scanned_like_any_other(self):
        result = sweep(PAGES, ["bug"], "welcome")
        self.assertEqual(
            result["hits"], [{"page": "excluded-changelog", "line": 3, "text": "Fixed a bug"}]
        )

    def test_a_control_found_only_on_an_excluded_page_still_counts(self):
        result = sweep({"kept": "nothing here", "excluded": "the control word"}, ["x"], "control")
        self.assertEqual(result["positive_control_hits"], 1)

    def test_hit_lines_are_one_based_sorted_and_cleaned(self):
        result = sweep(PAGES, ["sandbox", "^hooks"], "welcome")
        self.assertEqual(
            [(h["page"], h["line"], h["text"]) for h in result["hits"]],
            [
                ("excluded-changelog", 2, "Added the sandbox setting"),
                ("overview", 2, "Hooks run before a tool call"),
                ("reference", 2, "sandbox: true"),
                ("reference", 3, "hooks: []"),
            ],
        )
        self.assertEqual(result["hit_count"], 4)

    def test_a_line_matching_two_terms_counts_once(self):
        result = sweep({"p": "alpha beta\nalpha\n"}, ["alpha", "beta"], "alpha")
        self.assertEqual(result["hit_count"], 2)

    def test_terms_are_case_insensitive_regexes(self):
        result = sweep({"p": "Alpha-1\nALPHA-22\nbeta\n"}, [r"alpha-\d+"], "BETA")
        self.assertEqual(result["hit_count"], 2)

    def test_the_hit_list_is_capped_but_the_count_is_not(self):
        pages = {"big": "match\n" * 450, "other": "match\n" * 50 + "control\n"}
        result = sweep(pages, ["match"], "control")
        self.assertEqual(len(result["hits"]), 200)
        self.assertEqual(result["hit_count"], 500)
        self.assertEqual({h["page"] for h in result["hits"]}, {"big"})

    def test_hit_text_is_clipped_to_200_characters(self):
        result = sweep({"p": "needle " + "x" * 500 + "\ncontrol\n"}, ["needle"], "control")
        self.assertEqual(len(result["hits"][0]["text"]), 200)

    def test_a_match_deep_in_a_long_line_stays_in_the_hit_text(self):
        line = "x" * 1000 + " needle " + "y" * 1000
        result = sweep({"p": line + "\ncontrol\n"}, ["needle"], "control")
        text = result["hits"][0]["text"]
        self.assertEqual(len(text), 200)
        self.assertIn("needle", text)
        self.assertEqual(text.index("needle"), 60)

    def test_a_crlf_page_matches_a_dollar_anchored_term(self):
        crlf = sweep({"p": "vendor docs\r\nfeature sandbox\r\n"}, ["sandbox$"], "vendor")
        lf = sweep({"p": "vendor docs\nfeature sandbox\n"}, ["sandbox$"], "vendor")
        self.assertEqual(crlf["hit_count"], 1)
        self.assertEqual(crlf["hits"], [{"page": "p", "line": 2, "text": "feature sandbox"}])
        self.assertEqual(crlf["hits"], lf["hits"])

    def test_a_dollar_anchored_control_is_found_on_a_crlf_page(self):
        result = sweep({"p": "vendor docs\r\nfeature\r\n"}, ["feature"], "docs$")
        self.assertEqual(result["positive_control_hits"], 1)

    def test_lines_split_on_line_feed_only(self):
        result = sweep({"p": "a\rb sandbox\nvendor\n"}, ["sandbox"], "vendor")
        self.assertEqual([(h["line"], h["text"]) for h in result["hits"]], [(1, "a\rb sandbox")])

    def test_a_control_that_matches_the_empty_string_raises(self):
        for control in ("", "x*", "$", "(?:)", "a?", "^"):
            with self.assertRaises(ValueError, msg=repr(control)):
                sweep({"p": "zzz\n"}, ["zzz"], control)

    def test_a_control_that_needs_text_is_still_accepted(self):
        self.assertEqual(sweep({"p": "zzz\n"}, ["zzz"], "z+")["positive_control_hits"], 1)

    def test_invalid_regex_raises_value_error(self):
        with self.assertRaises(ValueError):
            sweep(PAGES, ["(unclosed"], "hooks")
        with self.assertRaises(ValueError):
            sweep(PAGES, ["hooks"], "[bad")

    def test_corpus_hash_is_stable_order_independent_and_sensitive(self):
        first = sweep(PAGES, ["bug"], "hooks")["corpus_sha256"]
        again = sweep(dict(reversed(list(PAGES.items()))), ["other"], "hooks")["corpus_sha256"]
        self.assertEqual(first, again)
        changed = {**PAGES, "overview": PAGES["overview"] + "x"}
        self.assertNotEqual(first, sweep(changed, ["bug"], "hooks")["corpus_sha256"])
        renamed = {("renamed" if k == "overview" else k): v for k, v in PAGES.items()}
        self.assertNotEqual(first, sweep(renamed, ["bug"], "hooks")["corpus_sha256"])

    def test_corpus_hash_follows_the_documented_construction(self):
        pages = {"b": "two", "a": "one"}
        lines = [
            f"{pid}\0{hashlib.sha256(text.encode()).hexdigest()}\n"
            for pid, text in sorted(pages.items())
        ]
        expected = hashlib.sha256("".join(lines).encode()).hexdigest()
        self.assertEqual(sweep_module.corpus_digest(pages), expected)


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOLS / "sweep.py"), *args],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "ATLAS_TEST_ALLOW_ANY_TREE": "1"},
        )

    def test_selftest_prints_ok(self):
        out = self.run_cli("--selftest")
        self.assertEqual((out.returncode, out.stdout.strip()), (0, "OK"), out.stderr)

    def test_cli_sweeps_a_directory_and_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            mirror = tmp / "mirror"
            mirror.mkdir()
            for pid, text in PAGES.items():
                (mirror / f"{pid}.md").write_bytes(text.encode("utf-8"))
            out = self.run_cli(
                "--pages-dir", str(mirror), "--term", "sandbox", "--term", "telemetry",
                "--control", "hooks", "--out", str(tmp / "sweep.json"),
            )  # fmt: skip
            self.assertEqual(out.returncode, 0, out.stderr)
            result = json.loads((tmp / "sweep.json").read_text("utf-8"))
        self.assertEqual(result["hit_count"], 2)
        self.assertEqual(result["terms"], ["sandbox", "telemetry"])
        self.assertEqual(result["pages_scanned"], 3)

    def test_cli_exits_nonzero_and_writes_nothing_on_a_blind_probe(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "p.md").write_text("some text\n", encoding="utf-8")
            out_path = tmp / "sweep.json"
            out = self.run_cli(
                "--pages-dir", str(tmp), "--term", "x", "--control", "absent-control",
                "--out", str(out_path),
            )  # fmt: skip
            self.assertNotEqual(out.returncode, 0)
            self.assertIn("BLIND PROBE", out.stderr)
            self.assertFalse(out_path.exists())

    def test_cli_rejects_a_non_utf8_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "p.md").write_bytes(b"caf\xe9\n")
            out = self.run_cli(
                "--pages-dir", str(tmp), "--term", "x", "--control", "caf",
                "--out", str(tmp / "o.json"),
            )  # fmt: skip
            self.assertEqual(out.returncode, 2)


if __name__ == "__main__":
    unittest.main()
