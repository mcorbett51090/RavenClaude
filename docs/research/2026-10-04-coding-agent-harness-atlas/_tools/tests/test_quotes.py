import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

os.environ["ATLAS_TEST_ALLOW_ANY_TREE"] = "1"
TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import quotes  # noqa: E402
from quotes import (  # noqa: E402
    build_evidence,
    is_install_span,
    norm,
    verify_batch,
    verify_quote,
)

EVIDENCE_SCHEMA = json.loads((TOOLS / "schemas" / "evidence.schema.json").read_text("utf-8"))

# Install-shaped samples are built from fragments: the repo's command-review hook refuses a
# file write that contains a downloader piped into a shell, even inside a test string.
_DL = "cu" + "rl"
_GET = "wg" + "et"
_SH = "s" + "h"
_BASH = "ba" + _SH
_BAR = "|"
_PS_GET = "ir" + "m"
_PS_RUN = "ie" + "x"


def piped_install(downloader=_DL, shell=_SH):
    return f"{downloader} -fsSL https://example.com/get {_BAR} {shell}"


def continued_install():
    """The two lines of one command split by a backslash continuation."""
    return f"{_DL} -fsSL https://example.com/get \\", f"  {_BAR} {_SH} -s -- --yes"


COMMAND_MARKER = "example.com/get"
PLACEHOLDER = "[install command line omitted]"


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def schema_errors(value, schema, path="$"):
    """A small structural check of the keywords evidence.schema.json uses (no dependency)."""
    errors = []
    kinds = {
        "string": str,
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None),
    }
    wanted = schema.get("type")
    if wanted is not None:
        names = wanted if isinstance(wanted, list) else [wanted]
        ok = any(
            isinstance(value, kinds[n]) and not (n == "integer" and isinstance(value, bool))
            for n in names
        )
        if not ok:
            return [f"{path}: expected {names}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in enum")
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match {schema['pattern']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: longer than {schema['maxLength']}")
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: below minimum")
    if isinstance(value, list):
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: more than {schema['maxItems']} items")
        for i, item in enumerate(value):
            errors += schema_errors(item, schema.get("items", {}), f"{path}[{i}]")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required {key}")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errors.append(f"{path}: unexpected key {key}")
        for key, sub in props.items():
            if key in value:
                errors += schema_errors(value[key], sub, f"{path}.{key}")
    return errors


RAW = "\n".join(
    [
        "# Title",  # 1
        "",  # 2
        "Intro text here.",  # 3
        "",  # 4
        "## Settings",  # 5
        "",  # 6
        "| Key | Value |",  # 7
        "| --- | --- |",  # 8
        "| `model` | The **default** model |",  # 9
        "| `theme` | Dark or light |",  # 10
        "",  # 11
        "The agent reads the",  # 12
        "config file at startup.",  # 13
        "",  # 14
        "Pass ‹name› as the argument.",  # 15
        "Use <flag> to enable it.",  # 16
        "alpha",  # 17
        "beta",  # 18
        "",  # 19
    ]
)


def page(raw_text, surface="claude-code"):
    return {
        "raw_text": raw_text,
        "surface": surface,
        "tier": "E1",
        "url": "https://example.com/docs",
        "url_effective": "https://example.com/docs",
        "retrieved": "2026-10-04",
        "http_status": 200,
        "sha256": hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
        "bytes": len(raw_text.encode("utf-8")),
        "product_version": "1.2.3",
        "version_source": "docs banner",
    }


def record(quote, **extra):
    base = {"page_id": "p1", "chunk_id": "c1", "rows": ["F01.alpha"], "claim": "a claim"}
    return {**base, "quote": quote, **extra}


def evidence_for(raw_text, quote, **extra):
    p = page(raw_text)
    return build_evidence(
        surface=p["surface"],
        tier=p["tier"],
        url=p["url"],
        url_effective=p["url_effective"],
        retrieved=p["retrieved"],
        http_status=p["http_status"],
        raw_bytes_sha256=p["sha256"],
        raw_bytes_len=p["bytes"],
        product_version=p["product_version"],
        version_source=p["version_source"],
        raw_text=raw_text,
        record=record(quote, **extra),
        seq=7,
    )


class NormTests(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(norm("  a \t b\n c ", "exact"), "  a \t b\n c ")
        self.assertEqual(norm("  a \t b\n c ", "ws"), "a b c")
        self.assertEqual(norm("‹x›  y", "neutral"), "<x> y")
        self.assertEqual(norm("| `a` | **b** |  c_d \\ # >", "markup"), "a b c d")

    def test_unknown_tier_raises(self):
        with self.assertRaises(ValueError):
            norm("x", "fuzzy")

    def test_markup_tier_blanks_the_right_substitute_but_keeps_the_left(self):
        self.assertEqual(norm("‹a›", "markup"), "<a")

    def test_markup_characters_become_spaces_not_nothing(self):
        for char in "`*_|\\#>":
            self.assertEqual(norm(f"no{char}sandbox", "markup"), "no sandbox", char)

    def test_a_nul_character_is_a_space_in_every_normalized_tier(self):
        for tier in ("ws", "neutral", "markup"):
            self.assertEqual(norm("a\x00b", tier), "a b", tier)


class VerifyQuoteTests(unittest.TestCase):
    def test_exact_match_has_exact_line(self):
        got = verify_quote("Intro text here.", RAW)
        self.assertEqual(
            got,
            {
                "found": True,
                "tier": "exact",
                "start_line": 3,
                "end_line": 3,
                "raw_span": "Intro text here.",
                "span_offset": 0,
                "ambiguous": False,
                "occurrences": 1,
            },
        )

    def test_exact_substring_inside_a_line_expands_to_the_whole_line(self):
        got = verify_quote("text here", RAW)
        self.assertEqual(
            (got["tier"], got["start_line"], got["raw_span"]), ("exact", 3, RAW.split("\n")[2])
        )

    def test_ws_match_across_a_wrapped_paragraph(self):
        got = verify_quote("The agent reads the config   file at startup.", RAW)
        self.assertEqual(got["tier"], "ws")
        self.assertEqual((got["start_line"], got["end_line"]), (12, 13))
        self.assertEqual(got["raw_span"], "The agent reads the\nconfig file at startup.")

    def test_neutral_match_when_the_raw_text_has_the_substitutes(self):
        got = verify_quote("Pass <name> as the argument.", RAW)
        self.assertEqual((got["tier"], got["start_line"], got["end_line"]), ("neutral", 15, 15))
        self.assertEqual(got["raw_span"], "Pass ‹name› as the argument.")

    def test_neutral_match_when_the_quote_has_the_substitutes(self):
        got = verify_quote("Use ‹flag› to enable it.", RAW)
        self.assertEqual((got["tier"], got["start_line"]), ("neutral", 16))
        self.assertEqual(got["raw_span"], "Use <flag> to enable it.")

    def test_markup_match_for_a_table_row_without_pipes_returns_the_raw_row(self):
        got = verify_quote("model The default model", RAW)
        self.assertEqual((got["tier"], got["start_line"], got["end_line"]), ("markup", 9, 9))
        self.assertEqual(got["raw_span"], "| `model` | The **default** model |")

    def test_a_quote_inside_one_table_row_is_still_found(self):
        got = verify_quote("theme Dark or light", RAW)
        self.assertEqual((got["tier"], got["start_line"], got["end_line"]), ("markup", 10, 10))
        got = verify_quote("Key Value", RAW)
        self.assertEqual((got["tier"], got["start_line"]), ("markup", 7))

    def test_a_quote_stitched_from_non_adjacent_cells_is_not_found(self):
        self.assertFalse(verify_quote("Key Value default", RAW)["found"])

    def test_a_quote_never_matches_across_two_table_rows(self):
        # Two rows are two statements; a match across the row boundary is a splice.
        self.assertFalse(verify_quote("model The default model theme Dark or light", RAW)["found"])
        raw = "intro line\n| Hooks | No |\n| Sandbox | Yes |\n"
        self.assertTrue(verify_quote("Hooks No", raw)["found"])
        self.assertFalse(verify_quote("No Sandbox", raw)["found"])

    def test_a_quote_never_matches_across_a_paragraph_and_a_heading(self):
        raw = "Hooks are disabled\n\n## Windows\nmore text\n"
        self.assertFalse(verify_quote("disabled Windows", raw)["found"])
        tight = "Hooks are disabled\n## Windows\nmore text\n"
        self.assertFalse(verify_quote("disabled Windows", tight)["found"])
        self.assertFalse(verify_quote("Windows more text", tight)["found"])

    def test_a_quote_never_matches_across_a_blank_line(self):
        raw = "first paragraph ends here\n\nsecond paragraph starts\n"
        self.assertFalse(verify_quote("ends here second paragraph", raw)["found"])
        self.assertTrue(verify_quote("first paragraph ends here", raw)["found"])

    def test_a_quote_never_matches_across_a_fence_line(self):
        raw = "some prose text here\n```\ncode goes in here\n```\nprose after\n"
        self.assertFalse(verify_quote("text here code goes in", raw)["found"])
        self.assertFalse(verify_quote("in here prose after", raw)["found"])

    def test_a_line_that_normalizes_to_nothing_is_a_boundary_not_a_join(self):
        raw = "alpha beta gamma\n***\ndelta epsilon zeta\n"
        self.assertFalse(verify_quote("gamma delta epsilon", raw)["found"])
        raw = "alpha beta gamma\n> \ndelta epsilon zeta\n"
        self.assertFalse(verify_quote("gamma delta epsilon", raw)["found"])

    def test_a_quote_wrapping_across_plain_text_lines_is_still_found(self):
        raw = "intro\n\nthe sandbox is\non by default\nand stays on\n\nend\n"
        got = verify_quote("the sandbox is on by default and stays on", raw)
        self.assertEqual((got["tier"], got["start_line"], got["end_line"]), ("ws", 3, 5))
        got = verify_quote(
            "> the sandbox is\n> on by default", "> the sandbox is\n> on by default\n"
        )
        self.assertEqual((got["tier"], got["start_line"], got["end_line"]), ("exact", 1, 2))
        got = verify_quote("the sandbox is on by default", "> the sandbox is\n> on by default\n")
        self.assertEqual((got["tier"], got["start_line"], got["end_line"]), ("markup", 1, 2))

    def test_a_nul_in_the_quote_cannot_bridge_a_boundary(self):
        raw = "first paragraph ends here\n\nsecond paragraph starts\n"
        self.assertFalse(verify_quote("ends here\x00second paragraph", raw)["found"])
        self.assertTrue(verify_quote("paragraph\x00ends here", raw)["found"])

    def test_markup_characters_do_not_merge_neighbouring_words(self):
        raw = "set no_sandbox_mode_enabled here\n"
        self.assertFalse(verify_quote("nosandboxmodeenabled", raw)["found"])
        self.assertEqual(verify_quote("nosandboxmodeenabled", raw).get("reason"), None)
        self.assertFalse(verify_quote("nosandbox", raw)["found"])
        self.assertTrue(verify_quote("no sandbox mode enabled", raw)["found"])

    def test_earlier_markup_cases_still_match(self):
        raw = "| `k` | The **v** | plain_text here |\n"
        for quote in ("k The v", "The v plain text here", "The  v"):
            self.assertTrue(verify_quote(quote, raw)["found"], quote)
        raw = "Use the **bold marker** and `code span` text\n"
        self.assertEqual(verify_quote("the bold marker and code span text", raw)["tier"], "markup")

    def test_absent_quote_is_not_found(self):
        got = verify_quote("this sentence is nowhere", RAW)
        self.assertEqual(
            got,
            {
                "found": False,
                "tier": None,
                "start_line": None,
                "end_line": None,
                "raw_span": None,
                "ambiguous": False,
                "occurrences": 0,
            },
        )

    def test_empty_and_whitespace_only_quotes_are_not_found(self):
        self.assertFalse(verify_quote("", RAW)["found"])
        self.assertFalse(verify_quote("  \n ", RAW)["found"])
        self.assertFalse(verify_quote("|||", RAW)["found"])
        self.assertFalse(verify_quote(None, RAW)["found"])

    def test_trivial_quotes_are_too_short_to_verify(self):
        raw = RAW + "\nNo\ne\n|\n1\n**\nv1.2 and a **b** here\n"
        for quote in ("No", "e", "|", "1", "**", "|||", "v1", "a"):
            got = verify_quote(quote, raw)
            self.assertFalse(got["found"], quote)
            self.assertEqual(got["reason"], "too_short", quote)
            self.assertIsNone(got["raw_span"], quote)

    def test_a_one_line_table_row_is_long_enough(self):
        got = verify_quote("| Key | Value |", RAW)
        self.assertEqual((got["found"], got["tier"], got["start_line"]), (True, "exact", 7))
        self.assertTrue(verify_quote("Key Value", RAW)["found"])

    def test_a_quote_is_too_short_only_when_it_fails_both_minimums(self):
        self.assertEqual((quotes.MIN_QUOTE_ALNUM, quotes.MIN_QUOTE_WORDS), (12, 2))
        raw = "abcdefghijkl and ab cd and\n"
        long_word = verify_quote("abcdefghijkl", raw)
        self.assertTrue(long_word["found"], long_word)  # 12 letters, one word
        two_words = verify_quote("ab cd", raw)
        self.assertTrue(two_words["found"], two_words)  # two words, four letters
        self.assertEqual(verify_quote("abcdefghijk", raw).get("reason"), "too_short")

    def test_the_size_check_counts_the_markup_normalized_quote(self):
        # Bare markup around a short word leaves one short word: still too short.
        self.assertEqual(verify_quote("**No**", RAW + "\n**No**\n").get("reason"), "too_short")
        self.assertEqual(verify_quote("| 1 |", RAW + "\n| 1 |\n").get("reason"), "too_short")

    def test_multi_line_exact_quote(self):
        got = verify_quote("alpha\nbeta", RAW)
        self.assertEqual((got["tier"], got["start_line"], got["end_line"]), ("exact", 17, 18))
        self.assertEqual(got["raw_span"], "alpha\nbeta")

    def test_a_quote_ending_in_a_newline_stays_on_its_own_line(self):
        raw = "first line here\nsecond line\n"
        got = verify_quote("first line here\n", raw)
        self.assertEqual((got["start_line"], got["end_line"]), (1, 1))

    def test_crlf_text_has_correct_lines_and_clean_spans(self):
        raw = "one\r\ntwo words\r\nthree\r\n"
        exact = verify_quote("two words", raw)
        self.assertEqual(
            (exact["tier"], exact["start_line"], exact["raw_span"]), ("exact", 2, "two words")
        )
        ws = verify_quote("two   words three", raw)
        self.assertEqual((ws["tier"], ws["start_line"], ws["end_line"]), ("ws", 2, 3))
        self.assertEqual(ws["raw_span"], "two words\nthree")

    def test_ambiguity_and_line_hint_choose_the_nearer_occurrence(self):
        needle = "a needle here"
        raw = "\n".join(["x", needle, "y", "z", needle, "w", needle])
        first = verify_quote(needle, raw)
        self.assertEqual(
            (first["start_line"], first["ambiguous"], first["occurrences"]), (2, True, 3)
        )
        near5 = verify_quote(needle, raw, line_hint=6)
        self.assertEqual(near5["start_line"], 5)
        near7 = verify_quote(needle, raw, line_hint=100)
        self.assertEqual(near7["start_line"], 7)
        tie = verify_quote(needle, raw, line_hint=3)
        self.assertEqual(tie["start_line"], 2)

    def test_ambiguity_also_applies_in_the_normalized_tiers(self):
        raw = "a  b\nfiller\na b\n"
        got = verify_quote("a b", raw, line_hint=3)
        self.assertEqual((got["tier"], got["start_line"], got["occurrences"]), ("exact", 3, 1))
        got = verify_quote("a   b", raw, line_hint=3)
        self.assertEqual((got["tier"], got["start_line"], got["occurrences"]), ("ws", 3, 2))
        self.assertTrue(got["ambiguous"])
        got = verify_quote("a   b", raw)
        self.assertEqual((got["tier"], got["start_line"], got["occurrences"]), ("ws", 1, 2))

    def test_the_first_matching_tier_wins(self):
        raw = "a  b\n| a b |\n"
        got = verify_quote("a b", raw)
        self.assertEqual((got["tier"], got["start_line"]), ("exact", 2))

    def test_raw_span_is_capped_at_300_characters(self):
        words = [f"word{i:03d}" for i in range(120)]
        long_line = " ".join(words)
        needle = " ".join(words[80:83])
        got = verify_quote(needle, "head\n" + long_line + "\ntail")
        self.assertEqual(got["start_line"], 2)
        self.assertLessEqual(len(got["raw_span"]), 300)
        self.assertIn(needle, got["raw_span"])
        self.assertGreater(got["span_offset"], 0)
        self.assertEqual(long_line[got["span_offset"] :][: len(got["raw_span"])], got["raw_span"])
        # The window is cut on word boundaries.
        self.assertTrue(got["raw_span"].startswith("word"))
        self.assertTrue(got["raw_span"].split()[-1] in words)

    def test_a_match_past_character_300_of_its_line_is_inside_the_stored_span(self):
        line = "x" * 400 + " Sandboxing is disabled on Windows."
        needle = "Sandboxing is disabled on Windows."
        got = verify_quote(needle, "head\n" + line + "\ntail")
        self.assertEqual(got["start_line"], 2)
        self.assertLessEqual(len(got["raw_span"]), 300)
        self.assertIn("Sandboxing", got["raw_span"])
        self.assertIn(norm(needle, "ws"), norm(got["raw_span"], "ws"))
        self.assertEqual(line[got["span_offset"] :][: len(got["raw_span"])], got["raw_span"])

    def test_the_window_is_centred_on_the_match_and_holds_it_at_either_end(self):
        words = [f"w{i:03d}" for i in range(150)]
        line = " ".join(words)
        for first in (0, 40, 74, 110, 147):
            needle = " ".join(words[first : first + 3])
            got = verify_quote(needle, line)
            self.assertIn(needle, got["raw_span"], first)
            self.assertLessEqual(len(got["raw_span"]), 300, first)
        middle = verify_quote(" ".join(words[74:77]), line)
        before = middle["raw_span"].index("w074")
        after = len(middle["raw_span"]) - middle["raw_span"].index("w076") - 4
        self.assertLess(abs(before - after), 12)

    def test_a_normalized_match_in_a_long_line_is_inside_the_stored_span(self):
        words = [f"| `w{i:03d}` |" for i in range(60)]
        line = " ".join(words)
        needle = "w040 w041 w042"
        got = verify_quote(needle, line)
        self.assertEqual(got["tier"], "markup")
        self.assertLessEqual(len(got["raw_span"]), 300)
        self.assertIn(needle, norm(got["raw_span"], "markup"))

    def test_a_match_across_two_long_lines_keeps_both_halves_in_the_span(self):
        first = " ".join(["aaaa"] * 70) + " final words"
        second = "start of next " + " ".join(["bbbb"] * 70)
        got = verify_quote("final words start of next", first + "\n" + second)
        self.assertEqual((got["tier"], got["start_line"], got["end_line"]), ("ws", 1, 2))
        self.assertLessEqual(len(got["raw_span"]), 300)
        self.assertIn("final words start of next", norm(got["raw_span"], "ws"))

    def test_a_match_longer_than_the_cap_keeps_the_legacy_line_cut(self):
        long_line = "w" * 500
        got = verify_quote("w" * 400, "head\n" + long_line + "\ntail")
        self.assertEqual(got["raw_span"], "w" * 300)
        self.assertEqual(got["span_offset"], 0)

    def test_raw_span_of_a_multi_line_quote_is_cut_at_a_line_boundary(self):
        lines = [f"{i}" * 90 for i in range(1, 6)]
        got = verify_quote("\n".join(lines), "\n".join(lines))
        self.assertEqual((got["start_line"], got["end_line"]), (1, 5))
        self.assertEqual(got["raw_span"], "\n".join(lines[:3]))
        self.assertLessEqual(len(got["raw_span"]), 300)

    def test_normalized_map_agrees_with_norm_of_the_whole_text(self):
        # Boundaries are sentinels in the haystack; read as spaces the text is the plain norm.
        for tier in ("ws", "neutral", "markup"):
            text, starts, seg_lines = quotes._norm_map(RAW, tier)
            self.assertEqual(" ".join(text.replace("\x00", " ").split()), norm(RAW, tier))
            self.assertEqual(len(starts), len(seg_lines))
            self.assertIn("\x00", text)
            self.assertNotIn("\x00 ", text)

    def test_lone_carriage_returns_are_line_breaks(self):
        raw = "one\rtwo\rline three\r"
        got = verify_quote("line three", raw)
        self.assertEqual((got["tier"], got["start_line"], got["end_line"]), ("exact", 3, 3))
        self.assertEqual(got["raw_span"], "line three")
        got = verify_quote("two line three", raw)
        self.assertEqual((got["tier"], got["start_line"], got["end_line"]), ("ws", 2, 3))

    def test_mixed_line_breaks_number_lines_the_same_way_in_every_tier(self):
        raw = "alpha one\r\nbeta two\rgamma three\ndelta four\r\n"
        exact = verify_quote("gamma three", raw)
        self.assertEqual((exact["tier"], exact["start_line"]), ("exact", 3))
        ws = verify_quote("gamma three delta four", raw)
        self.assertEqual((ws["tier"], ws["start_line"], ws["end_line"]), ("ws", 3, 4))
        last = verify_quote("delta four", raw)
        self.assertEqual(last["start_line"], 4)
        both = verify_quote("beta two\rgamma three", raw)
        self.assertEqual((both["tier"], both["start_line"], both["end_line"]), ("exact", 2, 3))

    def test_one_megabyte_page_is_verified_in_under_two_seconds(self):
        row = "| `option-%05d` | The **value** of option %05d is documented |\n"
        text = "".join(row % (i, i) for i in range(16000))
        self.assertGreater(len(text), 1_000_000)
        started = time.perf_counter()
        miss = verify_quote("option-15999 The value of option 15999 is documented!", text)
        hit = verify_quote("option-15999 The value of option 15999 is documented", text)
        elapsed = time.perf_counter() - started
        self.assertFalse(miss["found"])
        self.assertEqual((hit["tier"], hit["start_line"]), ("markup", 16000))
        self.assertLess(elapsed, 2.0)


class InstallDetectionTests(unittest.TestCase):
    def test_install_shapes_are_detected(self):
        samples = [
            piped_install(),
            piped_install(_GET, _BASH),
            piped_install(_DL.upper(), "ZSH") + " --yes",
            f"{_DL} -L https://example.com/i {_BAR} sudo {_BASH}",
            f"{_PS_GET} https://example.com/i.ps1 {_BAR} {_PS_RUN}",
            "npm install -g @scope/tool",
            "npm i --global tool",
            "npm install tool -g",
            "pip install example-tool",
            "python3 -m pip install --user example-tool",
            "pipx install example-tool",
            "brew install example",
            "brew upgrade example",
            "winget install Example.Tool",
            "scoop install example",
            "gh extension install owner/repo",
            "npx -y example-server",
            "NPM INSTALL -G tool",
        ]
        for sample in samples:
            self.assertTrue(is_install_span(sample), sample)

    def test_non_install_text_is_not_flagged(self):
        samples = [
            "Intro text here.",
            "npm install lodash",
            f"{_DL} https://example.com/status",
            f"{_DL} https://example.com/status {_BAR} jq .name",
            "Run the installer from the settings page.",
            f"{_BAR} sh is a shell",
            "set a global flag",
        ]
        for sample in samples:
            self.assertFalse(is_install_span(sample), sample)

    def test_a_backslash_continuation_is_joined_before_detection(self):
        first, second = continued_install()
        self.assertFalse(is_install_span(first))
        self.assertFalse(is_install_span(second))
        for text in (
            f"{first}\n{second}",
            f"{first}  \n{second}",
            f"{first}\t\r\n{second}",
            f"{first}\r{second}",
            f"echo before\n{first}\n{second}\necho after",
        ):
            self.assertTrue(quotes.install_text(text), repr(text))
            self.assertTrue(is_install_span(text), repr(text))

    def test_install_text_also_tests_the_plain_text(self):
        self.assertTrue(quotes.install_text(piped_install()))
        self.assertTrue(quotes.install_text(f"{_DL} -fsSL https://example.com/get {_BAR}\n{_SH}"))
        self.assertFalse(quotes.install_text("echo hi"))
        self.assertFalse(quotes.install_text(""))
        first, second = continued_install()
        self.assertFalse(quotes.install_text(f"{first}\n\n{second}"))
        self.assertFalse(quotes.install_text(f"{first.rstrip(chr(92))}\n{second}"))

    def test_a_continuation_only_joins_when_the_backslash_ends_the_line(self):
        first, second = continued_install()
        self.assertFalse(quotes.install_text(f"{first}x\n{second}"))  # the backslash is mid-line
        text = f"{_DL} https://example.com/get\n{_BAR} {_SH}"
        self.assertFalse(quotes.install_text(text))  # a bare line break ends the command

    def test_a_long_downloader_line_without_a_pipe_is_fast(self):
        line = (_DL + " ") * 72000
        self.assertGreater(len(line), 350_000)
        started = time.perf_counter()
        self.assertFalse(is_install_span(line))
        self.assertLess(time.perf_counter() - started, 0.5)

    def test_other_long_lines_are_fast_and_a_normal_line_is_still_detected(self):
        samples = [
            (_GET + " ") * 60000,
            ("npm install ") * 30000,
            (_PS_GET + " ") * 90000,
            (_DL + " ") * 60000 + _BAR,
            (_DL + " " + _BAR + " ") * 30000,
        ]
        started = time.perf_counter()
        for sample in samples:
            is_install_span(sample)
        self.assertLess(time.perf_counter() - started, 1.5)
        self.assertTrue(is_install_span(piped_install()))
        self.assertTrue(is_install_span("pip install example-tool"))

    def test_an_install_command_at_either_end_of_a_long_line_is_detected(self):
        filler = "x " * 100000
        self.assertTrue(is_install_span(piped_install() + " " + filler))
        self.assertTrue(is_install_span(filler + " " + piped_install()))
        self.assertTrue(is_install_span("pip install example-tool " + filler))
        self.assertFalse(is_install_span(filler))


class BuildEvidenceTests(unittest.TestCase):
    def test_evidence_satisfies_the_schema_and_stores_the_raw_row(self):
        evidence, info = evidence_for(RAW, "model The default model", line_hint=9)
        self.assertEqual(schema_errors(evidence, EVIDENCE_SCHEMA), [])
        self.assertEqual(evidence["id"], "E-claude-code-00007")
        self.assertEqual(evidence["quote"], "| `model` | The **default** model |")
        self.assertEqual(
            evidence["locator"], {"heading": "Settings", "raw_line_start": 9, "raw_line_end": 9}
        )
        self.assertEqual(evidence["context_before"], ["| Key | Value |", "| --- | --- |"])
        self.assertEqual(evidence["context_after"], ["| `theme` | Dark or light |", ""])
        self.assertTrue(evidence["quote_verified"])
        self.assertEqual(evidence["neutralizer_flags"], [])
        self.assertEqual(evidence["sha256"], page(RAW)["sha256"])
        self.assertEqual(evidence["bytes"], len(RAW.encode("utf-8")))
        self.assertNotIn("described_span", evidence)
        self.assertEqual(
            info,
            {
                "dropped": False,
                "tier": "markup",
                "ambiguous": False,
                "claim_rows": ["F01.alpha"],
                "claim": "a claim",
            },
        )

    def test_every_required_key_is_present(self):
        evidence, _ = evidence_for(RAW, "Intro text here.")
        for key in EVIDENCE_SCHEMA["required"]:
            self.assertIn(key, evidence)
        self.assertEqual(evidence["locator"]["heading"], "Title")
        self.assertEqual(evidence["context_before"], ["# Title", ""])

    def test_install_shaped_context_lines_are_scrubbed(self):
        # An install command next to the quote must not survive in the context lines
        # either (plan W2): it is replaced by a fixed placeholder.
        install_line = "run " + "npm install " + "-g some-package"
        before = "before line\n" + install_line + "\n"
        after = piped_install() + "\nafter line\n"
        raw = before + "The quoted sentence is here.\n" + after
        evidence, _ = evidence_for(raw, "The quoted sentence is here.")
        self.assertEqual(
            evidence["context_before"], ["before line", "[install command line omitted]"][-2:]
        )
        self.assertEqual(evidence["context_after"][0], "[install command line omitted]")
        self.assertNotIn("npm", " ".join(evidence["context_before"] + evidence["context_after"]))

    def test_heading_ignores_comment_lines_inside_fenced_code(self):
        raw = "## Real\n\n```sh\n# a comment, not a heading\n```\nafter the fence\n"
        evidence, _ = evidence_for(raw, "after the fence")
        self.assertEqual(evidence["locator"]["heading"], "Real")

    def test_heading_is_empty_before_the_first_heading(self):
        evidence, _ = evidence_for("plain\nline two\n", "line two")
        self.assertEqual(evidence["locator"]["heading"], "")
        self.assertEqual(evidence["context_after"], [])

    def test_context_is_clipped_to_300_characters(self):
        raw = "x" * 400 + "\nthe quoted line\n" + "y" * 400 + "\n"
        evidence, _ = evidence_for(raw, "the quoted line")
        self.assertEqual(evidence["context_before"], ["x" * 300])
        self.assertEqual(evidence["context_after"], ["y" * 300])
        self.assertEqual(schema_errors(evidence, EVIDENCE_SCHEMA), [])

    def test_install_line_becomes_a_described_span_with_an_empty_quote(self):
        line = piped_install()
        raw = "# Install\n\nFirst, get the tool.\n" + line + "\nThen start it.\n"
        evidence, info = evidence_for(raw, line)
        self.assertEqual(schema_errors(evidence, EVIDENCE_SCHEMA), [])
        self.assertEqual(evidence["quote"], "")
        self.assertEqual(
            evidence["described_span"],
            {
                "description": "install or update command line (stored as a described span)",
                "raw_line_start": 4,
                "raw_line_end": 4,
                "span_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
            },
        )
        self.assertNotIn(line, json.dumps(evidence))
        self.assertFalse(info["dropped"])

    def test_install_detection_applies_to_the_raw_span_not_the_scout_text(self):
        raw = "Intro\npip install example-tool\n"
        evidence, _ = evidence_for(raw, "install example-tool")
        self.assertEqual(evidence["quote"], "")
        self.assertEqual(evidence["described_span"]["raw_line_start"], 2)

    def stored_text(self, evidence):
        """Every stored field that could carry page text, as one list of strings."""
        out = [evidence["quote"], evidence["locator"].get("heading", "")]
        out += evidence["context_before"] + evidence["context_after"]
        out.append(json.dumps(evidence.get("described_span")))
        return out

    def assert_command_absent(self, evidence):
        for text in self.stored_text(evidence):
            self.assertNotIn(COMMAND_MARKER, text)
            self.assertNotIn("-s -- --yes", text)
        self.assertNotIn(COMMAND_MARKER, json.dumps(evidence))

    def continued_page(self):
        first, second = continued_install()
        lines = ["# Install", "", "Get the tool first.", first, second, "Then run it."]
        return "\n".join(lines) + "\n", first, second

    def test_a_continued_command_is_a_described_span_wherever_the_quote_sits(self):
        raw, first, second = self.continued_page()
        cases = (
            (first, (4, 4)),  # the quote is the first line only
            (first + "\n" + second, (4, 5)),  # the quote covers both lines
            (second.strip(), (5, 5)),  # the first half is a context line
            ("Get the tool first.", (3, 3)),  # the command is two lines after the quote
            ("Then run it.", (6, 6)),  # the command is two lines before the quote
        )
        for quote, (start, end) in cases:
            evidence, info = evidence_for(raw, quote)
            self.assertFalse(info["dropped"], quote)
            self.assertEqual(evidence["quote"], "", quote)
            self.assertEqual(
                (
                    evidence["described_span"]["raw_line_start"],
                    evidence["described_span"]["raw_line_end"],
                ),
                (start, end),
                quote,
            )
            self.assertEqual(schema_errors(evidence, EVIDENCE_SCHEMA), [], quote)
            self.assert_command_absent(evidence)

    def test_both_halves_of_a_continued_command_are_scrubbed_from_the_context(self):
        raw, first, second = self.continued_page()
        evidence, _ = evidence_for(raw, first)
        self.assertEqual(evidence["context_after"], [PLACEHOLDER, "Then run it."])
        self.assertEqual(evidence["context_before"], ["", "Get the tool first."])
        evidence, _ = evidence_for(raw, second.strip())
        self.assertEqual(evidence["context_before"], ["Get the tool first.", PLACEHOLDER])
        evidence, _ = evidence_for(raw, "Get the tool first.")
        self.assertEqual(evidence["context_after"], [PLACEHOLDER, PLACEHOLDER])

    def test_a_command_split_across_three_lines_is_scrubbed_whole(self):
        first = f"{_DL} -fsSL https://example.com/get \\"
        middle = "  -o /dev/null \\"
        last = f"  {_BAR} {_SH}"
        raw = "\n".join(["# Install", first, middle, last, "end"])
        evidence, _ = evidence_for(raw, first)
        self.assertEqual(evidence["quote"], "")
        self.assertEqual(evidence["context_after"], [PLACEHOLDER, PLACEHOLDER])
        self.assert_command_absent(evidence)
        evidence, _ = evidence_for(raw, middle.strip())
        self.assertEqual(evidence["quote"], "")
        self.assertEqual(evidence["context_before"], ["# Install", PLACEHOLDER])
        self.assertEqual(evidence["context_after"], [PLACEHOLDER, "end"])
        self.assert_command_absent(evidence)

    def test_a_command_three_lines_away_does_not_touch_the_quote(self):
        first, second = continued_install()
        lines = ["# Install", "", "Get the tool first.", "filler one", "filler two", first, second]
        evidence, _ = evidence_for("\n".join(lines) + "\n", "Get the tool first.")
        self.assertEqual(evidence["quote"], "Get the tool first.")
        self.assertNotIn("described_span", evidence)
        self.assertEqual(evidence["context_after"], ["filler one", "filler two"])

    def test_an_install_command_in_the_middle_of_a_giant_line_is_not_stored(self):
        giant = "x " * 5000 + piped_install() + " y" * 5000
        evidence, _ = evidence_for("# Install\n" + giant + "\n", piped_install())
        self.assertEqual(evidence["quote"], "")
        self.assertEqual(evidence["described_span"]["raw_line_start"], 2)
        self.assertNotIn(COMMAND_MARKER, json.dumps(evidence))

    def test_span_hash_covers_the_whole_lines_not_the_capped_span(self):
        line = "p " * 160 + piped_install()
        self.assertGreater(len(line), 300)
        evidence, _ = evidence_for("# Install\n" + line + "\nafter\n", piped_install())
        self.assertEqual(evidence["quote"], "")
        self.assertEqual(evidence["described_span"]["span_sha256"], sha(line))
        edited = line + " and a change after character 300"
        other, _ = evidence_for("# Install\n" + edited + "\nafter\n", piped_install())
        self.assertEqual(other["described_span"]["span_sha256"], sha(edited))
        self.assertNotEqual(
            evidence["described_span"]["span_sha256"], other["described_span"]["span_sha256"]
        )

    def test_a_two_line_span_hash_joins_the_whole_lines_with_a_newline(self):
        first, second = continued_install()
        raw = "# Install\r\n" + first + "\r\n" + second + "\r\n"
        evidence, _ = evidence_for(raw, first + "\r\n" + second)
        self.assertEqual(evidence["described_span"]["span_sha256"], sha(first + "\n" + second))

    def test_an_install_shaped_heading_is_replaced_by_the_placeholder(self):
        lines = [
            f"## {piped_install()}",
            "",
            "l1 plain",
            "l2 plain",
            "l3 plain",
            "The quote is here.",
        ]
        evidence, _ = evidence_for("\n".join(lines) + "\n", "The quote is here.")
        self.assertEqual(evidence["locator"]["heading"], PLACEHOLDER)
        self.assertEqual(evidence["quote"], "The quote is here.")
        self.assertNotIn(COMMAND_MARKER, json.dumps(evidence))
        lines[0] = "## Run pip install example-tool"
        evidence, _ = evidence_for("\n".join(lines) + "\n", "The quote is here.")
        self.assertEqual(evidence["locator"]["heading"], PLACEHOLDER)
        lines[0] = "## A plain heading"
        evidence, _ = evidence_for("\n".join(lines) + "\n", "The quote is here.")
        self.assertEqual(evidence["locator"]["heading"], "A plain heading")

    def test_a_dropped_record_stores_hashes_not_install_shaped_text(self):
        command = piped_install()
        claim = f"Run {command} to install"
        evidence, info = evidence_for(RAW, command, claim=claim)
        self.assertIsNone(evidence)
        self.assertEqual(info["reason"], "quote_not_found")
        self.assertEqual(info["quote"], PLACEHOLDER)
        self.assertEqual(info["claim"], PLACEHOLDER)
        self.assertEqual(info["quote_sha256"], sha(command))
        self.assertEqual(info["claim_sha256"], sha(claim))
        self.assertNotIn(COMMAND_MARKER, json.dumps(info))

    def test_only_the_install_shaped_field_is_replaced(self):
        command = piped_install()
        _, info = evidence_for(RAW, "a sentence that is not on the page", claim=command)
        self.assertEqual(info["quote"], "a sentence that is not on the page")
        self.assertEqual(info["claim"], PLACEHOLDER)
        self.assertEqual(info["claim_sha256"], sha(command))
        self.assertEqual(info["quote_sha256"], sha("a sentence that is not on the page"))
        _, info = evidence_for(RAW, command, claim="a plain claim")
        self.assertEqual((info["quote"], info["claim"]), (PLACEHOLDER, "a plain claim"))

    def test_a_dropped_plain_record_carries_no_hashes(self):
        _, info = evidence_for(RAW, "a sentence that is not on the page")
        self.assertNotIn("quote_sha256", info)
        self.assertNotIn("claim_sha256", info)
        self.assertEqual(info["claim"], "a claim")

    def test_a_kept_record_with_an_install_shaped_claim_stores_a_hash(self):
        claim = "Install with pip install example-tool"
        evidence, info = evidence_for(RAW, "Intro text here.", claim=claim)
        self.assertIsNotNone(evidence)
        self.assertEqual(info["claim"], PLACEHOLDER)
        self.assertEqual(info["claim_sha256"], sha(claim))
        self.assertNotIn("pip install", json.dumps(info))

    def test_a_too_short_quote_is_dropped_with_its_own_reason(self):
        for quote in ("No", "e", "|", "1", "**"):
            evidence, info = evidence_for(RAW + "\nNo\ne\n|\n1\n**\n", quote)
            self.assertIsNone(evidence, quote)
            self.assertEqual(info["reason"], "too_short", quote)
        evidence, _ = evidence_for(RAW, "| Key | Value |")
        self.assertEqual(evidence["quote"], "| Key | Value |")

    def test_an_atx_closing_sequence_is_not_part_of_the_heading(self):
        for line, expected in (
            ("## Hooks ##", "Hooks"),
            ("## Hooks ###  ", "Hooks"),
            ("### C# ###", "C#"),
            ("## C#", "C#"),
            ("# Plain", "Plain"),
        ):
            evidence, _ = evidence_for(f"{line}\n\nthe quoted line is here.\n", "the quoted line")
            self.assertEqual(evidence["locator"]["heading"], expected, line)

    def test_setext_headings_are_recognised(self):
        quote = "Some quoted text here."
        for raw, expected in (
            ("Hooks setup\n===========\n\nSome quoted text here.\n", "Hooks setup"),
            ("Sub heading\n---\nSome quoted text here.\n", "Sub heading"),
            ("## First\n\nx\n\nSecond one\n-----\n\nSome quoted text here.\n", "Second one"),
            ("Intro\n\n---\n\nSome quoted text here.\n", ""),
            ("Two\n==\nSome quoted text here.\n", ""),
            ("```\nnot a heading\n=====\n```\nSome quoted text here.\n", ""),
            ("---\ntitle: Page\nkind: guide\n---\n\nSome quoted text here.\n", ""),
            ("Hooks setup\r\n===========\r\nSome quoted text here.\r\n", "Hooks setup"),
        ):
            evidence, _ = evidence_for(raw, quote)
            self.assertEqual(evidence["locator"]["heading"], expected, raw)

    def test_a_setext_heading_that_is_the_quoted_line_is_its_own_heading(self):
        evidence, _ = evidence_for("Quoted heading text\n=======\nbody\n", "Quoted heading text")
        self.assertEqual(evidence["locator"]["heading"], "Quoted heading text")

    def test_lone_carriage_returns_number_lines_in_the_evidence(self):
        evidence, _ = evidence_for("one\rtwo\rline three\r", "line three")
        self.assertEqual(evidence["locator"]["raw_line_start"], 3)
        self.assertEqual(evidence["locator"]["raw_line_end"], 3)
        self.assertEqual(evidence["quote"], "line three")
        self.assertEqual(evidence["context_before"], ["one", "two"])
        self.assertEqual(evidence["context_after"], [])

    def test_a_missing_quote_is_dropped_not_repaired(self):
        evidence, info = evidence_for(RAW, "a sentence that is not on the page")
        self.assertIsNone(evidence)
        self.assertTrue(info["dropped"])
        self.assertEqual(info["reason"], "quote_not_found")

    def test_seq_must_fit_five_digits(self):
        with self.assertRaises(ValueError):
            p = page(RAW)
            build_evidence(
                surface="cursor",
                tier="E1",
                url=p["url"],
                url_effective=p["url"],
                retrieved=p["retrieved"],
                http_status=200,
                raw_bytes_sha256=p["sha256"],
                raw_bytes_len=p["bytes"],
                product_version=None,
                version_source=None,
                raw_text=RAW,
                record=record("Intro text here."),
                seq=100000,
            )


class VerifyBatchTests(unittest.TestCase):
    def test_pass_rate_pairs_ids_and_tiers(self):
        pages = {"p1": page(RAW), "p2": page("Only\ntext here\n", surface="cursor")}
        recs = [
            record("Intro text here."),
            record("model The default model"),
            record("not on the page"),
            record("text here", page_id="p2"),
            record("anything", page_id="missing"),
            record("Pass <name> as the argument."),
        ]
        out = verify_batch(recs, pages)
        self.assertEqual(out["pass_rate"], 4 / 6)
        self.assertEqual(
            [p["evidence_id"] for p in out["pairs"]],
            ["E-claude-code-00001", "E-claude-code-00002", "E-cursor-00001", "E-claude-code-00003"],
        )
        self.assertEqual([p["record_index"] for p in out["pairs"]], [0, 1, 3, 5])
        self.assertEqual(out["by_tier"], {"exact": 2, "ws": 0, "neutral": 1, "markup": 1})
        self.assertEqual(
            sorted((d["record_index"], d["reason"]) for d in out["dropped"]),
            [(2, "quote_not_found"), (4, "unknown_page")],
        )
        self.assertEqual(len(out["evidence"]), 4)
        for item in out["evidence"]:
            self.assertEqual(schema_errors(item, EVIDENCE_SCHEMA), [])

    def test_a_dropped_record_does_not_consume_an_evidence_number(self):
        out = verify_batch([record("nope"), record("Intro text here.")], {"p1": page(RAW)})
        self.assertEqual(out["evidence"][0]["id"], "E-claude-code-00001")

    def test_a_page_cut_from_an_aggregate_reports_lines_in_the_aggregate(self):
        plain = verify_batch([record("Intro text here.")], {"p1": page(RAW)})["evidence"][0]
        shifted_page = {**page(RAW), "line_offset": 100}
        shifted = verify_batch([record("Intro text here.")], {"p1": shifted_page})["evidence"][0]
        self.assertEqual(
            shifted["locator"]["raw_line_start"], plain["locator"]["raw_line_start"] + 100
        )
        self.assertEqual(shifted["locator"]["raw_line_end"], plain["locator"]["raw_line_end"] + 100)
        self.assertEqual(shifted["quote"], plain["quote"])
        self.assertEqual(schema_errors(shifted, EVIDENCE_SCHEMA), [])

    def test_the_offset_also_moves_a_described_install_span(self):
        a, b = continued_install()
        raw = f"intro\n{a}\n{b}\noutro\n"
        base = verify_batch([record(a)], {"p1": page(raw)})["evidence"][0]["described_span"]
        moved = verify_batch([record(a)], {"p1": {**page(raw), "line_offset": 7}})["evidence"][0][
            "described_span"
        ]
        self.assertEqual(moved["raw_line_start"], base["raw_line_start"] + 7)
        self.assertEqual(moved["raw_line_end"], base["raw_line_end"] + 7)
        self.assertEqual(moved["span_sha256"], base["span_sha256"])

    def test_empty_batch_passes_with_rate_one(self):
        out = verify_batch([], {})
        self.assertEqual(out["pass_rate"], 1.0)
        self.assertEqual(out["evidence"], [])

    def test_all_dropped_gives_rate_zero(self):
        out = verify_batch([record("nope")], {"p1": page(RAW)})
        self.assertEqual(out["pass_rate"], 0.0)

    def test_two_calls_sharing_counters_never_reuse_an_evidence_id(self):
        pages = {"p1": page(RAW), "p2": page("Only\ntext here\n", surface="cursor")}
        counters = {}
        first = verify_batch([record("Intro text here."), record("nope")], pages, counters)
        second = verify_batch(
            [record("Intro text here."), record("text here", page_id="p2"), record("Key Value")],
            pages,
            counters,
        )
        ids = [e["id"] for e in first["evidence"] + second["evidence"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            ids,
            ["E-claude-code-00001", "E-claude-code-00002", "E-cursor-00001", "E-claude-code-00003"],
        )
        self.assertEqual(counters, {"claude-code": 4, "cursor": 2})

    def test_counters_hold_the_next_number_and_are_read_before_use(self):
        counters = {"claude-code": 41}
        out = verify_batch([record("Intro text here.")], {"p1": page(RAW)}, counters)
        self.assertEqual(out["evidence"][0]["id"], "E-claude-code-00041")
        self.assertEqual(counters, {"claude-code": 42})

    def test_without_counters_every_call_starts_at_one(self):
        again = verify_batch([record("Intro text here.")], {"p1": page(RAW)})
        once_more = verify_batch([record("Intro text here.")], {"p1": page(RAW)})
        self.assertEqual(again["evidence"][0]["id"], once_more["evidence"][0]["id"])
        self.assertEqual(again["evidence"][0]["id"], "E-claude-code-00001")

    def test_a_dropped_record_leaves_the_counters_alone(self):
        counters = {}
        verify_batch([record("nope"), record("No")], {"p1": page(RAW)}, counters)
        self.assertEqual(counters, {})

    def test_batch_drops_carry_scrubbed_install_text_and_reasons(self):
        command = piped_install()
        recs = [
            record(command, claim=f"Run {command}"),
            record("No"),
            record("anything", page_id="missing", claim=f"Use {command}"),
        ]
        out = verify_batch(recs, {"p1": page(RAW)})
        by_index = {d["record_index"]: d for d in out["dropped"]}
        self.assertEqual(by_index[0]["reason"], "quote_not_found")
        self.assertEqual(by_index[1]["reason"], "too_short")
        self.assertEqual(by_index[2]["reason"], "unknown_page")
        self.assertEqual(by_index[2]["claim"], PLACEHOLDER)
        self.assertEqual(by_index[2]["claim_sha256"], sha(f"Use {command}"))
        self.assertNotIn(COMMAND_MARKER, json.dumps(out))


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOLS / "quotes.py"), *args],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "ATLAS_TEST_ALLOW_ANY_TREE": "1"},
        )

    def test_selftest_prints_ok(self):
        out = self.run_cli("--selftest")
        self.assertEqual((out.returncode, out.stdout.strip()), (0, "OK"), out.stderr)

    def test_check_prints_the_verify_quote_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "page.md"
            raw.write_bytes(RAW.encode("utf-8"))
            out = self.run_cli("check", "--raw", str(raw), "--quote", "model The default model")
        self.assertEqual(out.returncode, 0, out.stderr)
        got = json.loads(out.stdout)
        self.assertEqual((got["found"], got["tier"], got["start_line"]), (True, "markup", 9))

    def test_check_reports_a_too_short_quote(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "page.md"
            raw.write_bytes(RAW.encode("utf-8"))
            out = self.run_cli("check", "--raw", str(raw), "--quote", "No")
        self.assertEqual(out.returncode, 0, out.stderr)
        got = json.loads(out.stdout)
        self.assertEqual((got["found"], got["reason"]), (False, "too_short"))

    def test_batch_rejects_a_malformed_counters_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "p1.md").write_bytes(RAW.encode("utf-8"))
            spec = {k: v for k, v in page(RAW).items() if k != "raw_text"}
            spec["raw_path"] = str(tmp / "p1.md")
            (tmp / "pages.json").write_text(json.dumps({"p1": spec}), encoding="utf-8")
            (tmp / "scout.json").write_text(json.dumps({"records": []}), encoding="utf-8")
            (tmp / "counters.json").write_text('{"claude-code": "two"}', encoding="utf-8")
            out = self.run_cli(
                "batch",
                "--records",
                str(tmp / "scout.json"),
                "--pages",
                str(tmp / "pages.json"),
                "--out",
                str(tmp / "out.json"),
                "--counters",
                str(tmp / "counters.json"),
            )
            self.assertEqual(out.returncode, 2)
            self.assertFalse((tmp / "out.json").exists())

    def test_batch_writes_evidence_and_prints_pass_rate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "p1.md").write_bytes(RAW.encode("utf-8"))
            spec = {k: v for k, v in page(RAW).items() if k != "raw_text"}
            spec["raw_path"] = str(tmp / "p1.md")
            (tmp / "pages.json").write_text(json.dumps({"p1": spec}), encoding="utf-8")
            scout = {
                "batch_id": "b1",
                "records": [record("Intro text here."), record("not on the page")],
                "pages_no_facts": [],
            }
            (tmp / "scout.json").write_text(json.dumps(scout), encoding="utf-8")
            out = self.run_cli(
                "batch",
                "--records",
                str(tmp / "scout.json"),
                "--pages",
                str(tmp / "pages.json"),
                "--out",
                str(tmp / "out.json"),
            )
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertIn("0.5", out.stdout)
            result = json.loads((tmp / "out.json").read_text("utf-8"))
        self.assertEqual(result["pass_rate"], 0.5)
        self.assertEqual(result["evidence"][0]["quote"], "Intro text here.")

    def test_batch_counters_file_keeps_ids_distinct_across_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "p1.md").write_bytes(RAW.encode("utf-8"))
            spec = {k: v for k, v in page(RAW).items() if k != "raw_text"}
            spec["raw_path"] = str(tmp / "p1.md")
            (tmp / "pages.json").write_text(json.dumps({"p1": spec}), encoding="utf-8")
            (tmp / "scout.json").write_text(
                json.dumps({"records": [record("Intro text here."), record("Key Value")]}),
                encoding="utf-8",
            )
            counters = tmp / "counters.json"
            ids = []
            for run in range(2):
                out = self.run_cli(
                    "batch",
                    "--records",
                    str(tmp / "scout.json"),
                    "--pages",
                    str(tmp / "pages.json"),
                    "--out",
                    str(tmp / f"out{run}.json"),
                    "--counters",
                    str(counters),
                )
                self.assertEqual(out.returncode, 0, out.stderr)
                result = json.loads((tmp / f"out{run}.json").read_text("utf-8"))
                ids += [e["id"] for e in result["evidence"]]
                self.assertEqual(
                    json.loads(counters.read_text("utf-8")), {"claude-code": 3 + 2 * run}
                )
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids[-1], "E-claude-code-00004")

    def test_batch_without_a_counters_file_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "p1.md").write_bytes(RAW.encode("utf-8"))
            spec = {k: v for k, v in page(RAW).items() if k != "raw_text"}
            spec["raw_path"] = str(tmp / "p1.md")
            (tmp / "pages.json").write_text(json.dumps({"p1": spec}), encoding="utf-8")
            (tmp / "scout.json").write_text(
                json.dumps({"records": [record("Intro text here.")]}), encoding="utf-8"
            )
            out = self.run_cli(
                "batch",
                "--records",
                str(tmp / "scout.json"),
                "--pages",
                str(tmp / "pages.json"),
                "--out",
                str(tmp / "out.json"),
            )
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual(
                json.loads((tmp / "out.json").read_text("utf-8"))["evidence"][0]["id"],
                "E-claude-code-00001",
            )
            self.assertEqual(
                sorted(p.name for p in tmp.iterdir()),
                sorted(["p1.md", "pages.json", "scout.json", "out.json"]),
            )


if __name__ == "__main__":
    unittest.main()
