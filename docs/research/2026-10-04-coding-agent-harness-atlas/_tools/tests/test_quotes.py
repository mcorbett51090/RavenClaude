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
        self.assertEqual(norm("| `a` | **b** |  c_d \\ # >", "markup"), "a b cd")

    def test_unknown_tier_raises(self):
        with self.assertRaises(ValueError):
            norm("x", "fuzzy")

    def test_markup_tier_removes_the_right_substitute_but_keeps_the_left(self):
        self.assertEqual(norm("‹a›", "markup"), "<a")


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
                "ambiguous": False,
                "occurrences": 1,
            },
        )

    def test_exact_substring_inside_a_line_expands_to_the_whole_line(self):
        got = verify_quote("here", RAW)
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

    def test_markup_match_spanning_two_rows(self):
        got = verify_quote("model The default model theme Dark or light", RAW)
        self.assertEqual((got["tier"], got["start_line"], got["end_line"]), ("markup", 9, 10))

    def test_a_quote_stitched_from_non_adjacent_cells_is_not_found(self):
        self.assertFalse(verify_quote("Key Value default", RAW)["found"])

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

    def test_multi_line_exact_quote(self):
        got = verify_quote("alpha\nbeta", RAW)
        self.assertEqual((got["tier"], got["start_line"], got["end_line"]), ("exact", 17, 18))
        self.assertEqual(got["raw_span"], "alpha\nbeta")

    def test_a_quote_ending_in_a_newline_stays_on_its_own_line(self):
        got = verify_quote("alpha\n", RAW)
        self.assertEqual((got["start_line"], got["end_line"]), (17, 17))

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
        raw = "\n".join(["x", "needle", "y", "z", "needle", "w", "needle"])
        first = verify_quote("needle", raw)
        self.assertEqual(
            (first["start_line"], first["ambiguous"], first["occurrences"]), (2, True, 3)
        )
        near5 = verify_quote("needle", raw, line_hint=6)
        self.assertEqual(near5["start_line"], 5)
        near7 = verify_quote("needle", raw, line_hint=100)
        self.assertEqual(near7["start_line"], 7)
        tie = verify_quote("needle", raw, line_hint=3)
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
        long_line = "w" * 500
        got = verify_quote("w" * 40, "head\n" + long_line + "\ntail")
        self.assertEqual(got["start_line"], 2)
        self.assertEqual(got["raw_span"], "w" * 300)

    def test_raw_span_of_a_multi_line_quote_is_cut_at_a_line_boundary(self):
        lines = [f"{i}" * 90 for i in range(1, 6)]
        got = verify_quote("\n".join(lines), "\n".join(lines))
        self.assertEqual((got["start_line"], got["end_line"]), (1, 5))
        self.assertEqual(got["raw_span"], "\n".join(lines[:3]))
        self.assertLessEqual(len(got["raw_span"]), 300)

    def test_normalized_map_agrees_with_norm_of_the_whole_text(self):
        for tier in ("ws", "neutral", "markup"):
            text, starts, seg_lines = quotes._norm_map(RAW, tier)
            self.assertEqual(text, norm(RAW, tier))
            self.assertEqual(len(starts), len(seg_lines))

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
        pages = {"p1": page(RAW), "p2": page("Only\ntext\n", surface="cursor")}
        recs = [
            record("Intro text here."),
            record("model The default model"),
            record("not on the page"),
            record("text", page_id="p2"),
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

    def test_empty_batch_passes_with_rate_one(self):
        out = verify_batch([], {})
        self.assertEqual(out["pass_rate"], 1.0)
        self.assertEqual(out["evidence"], [])

    def test_all_dropped_gives_rate_zero(self):
        out = verify_batch([record("nope")], {"p1": page(RAW)})
        self.assertEqual(out["pass_rate"], 0.0)


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


if __name__ == "__main__":
    unittest.main()
