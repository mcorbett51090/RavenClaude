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

import dedupe  # noqa: E402
from dedupe import line_containment, mark_secondary, norm_line  # noqa: E402


def lines(prefix, count):
    return [f"{prefix} fact number {i}" for i in range(count)]


def roles(result):
    return {pid: (r["role"], r["secondary_of"]) for pid, r in result.items()}


class NormAndContainmentTests(unittest.TestCase):
    def test_norm_line_strips_collapses_and_lowercases(self):
        self.assertEqual(norm_line("  Hello \t  WORLD \r"), "hello world")
        self.assertEqual(norm_line("   "), "")

    def test_containment_is_the_fraction_of_a_found_in_b(self):
        a = ["one", "two", "three", "four"]
        b = ["ONE", "  two ", "x"]
        self.assertEqual(line_containment(a, b), 0.5)
        self.assertEqual(line_containment(b, a), 2 / 3)

    def test_blank_lines_are_ignored_on_both_sides(self):
        a = ["one", "", "   ", "two", "\t"]
        b = ["", "one", "two", "", ""]
        self.assertEqual(line_containment(a, b), 1.0)
        self.assertEqual(line_containment(["", "  "], ["x"]), 0.0)
        self.assertEqual(line_containment([], ["x"]), 0.0)
        self.assertEqual(line_containment(["x"], ["", " "]), 0.0)

    def test_repeated_lines_in_a_count_each_time(self):
        self.assertEqual(line_containment(["x", "x", "y"], ["x"]), 2 / 3)


class MarkSecondaryTests(unittest.TestCase):
    def test_identical_pages_one_canonical_smaller_id_wins(self):
        same = lines("same", 10)
        result = mark_secondary({"b": list(same), "a": list(same)}, set())
        self.assertEqual(roles(result), {"a": ("canonical", None), "b": ("secondary", "a")})
        self.assertEqual(result["b"]["containment"], 1.0)
        self.assertEqual(result["a"]["containment"], 1.0)

    def test_three_identical_pages_collapse_onto_one_canonical(self):
        same = lines("same", 10)
        result = mark_secondary({"c": list(same), "a": list(same), "b": list(same)}, set())
        self.assertEqual(
            roles(result),
            {"a": ("canonical", None), "b": ("secondary", "a"), "c": ("secondary", "a")},
        )

    def test_mutual_containment_larger_page_is_canonical_even_with_larger_id(self):
        base = lines("base", 100)
        pages = {"a": base, "z": base + lines("extra", 5)}
        result = mark_secondary(pages, set())
        self.assertEqual(roles(result), {"a": ("secondary", "z"), "z": ("canonical", None)})
        self.assertGreaterEqual(result["z"]["containment"], 0.9)

    def test_95_percent_contained_page_is_secondary_of_the_larger_page(self):
        big = lines("big", 50)
        small = big[:19] + ["a line only the small page has"]
        result = mark_secondary({"big": big, "small": small}, set())
        self.assertEqual(roles(result), {"big": ("canonical", None), "small": ("secondary", "big")})
        self.assertEqual(result["small"]["containment"], 0.95)
        self.assertEqual(result["big"]["containment"], 19 / 50)

    def test_80_percent_contained_page_is_canonical(self):
        big = lines("big", 50)
        small = big[:16] + [f"unique small line {i}" for i in range(4)]
        result = mark_secondary({"big": big, "small": small}, set())
        self.assertEqual(roles(result), {"big": ("canonical", None), "small": ("canonical", None)})
        self.assertEqual(result["small"]["containment"], 0.8)

    def test_threshold_is_inclusive_and_adjustable(self):
        big = lines("big", 50)
        small = big[:16] + [f"unique small line {i}" for i in range(4)]
        low = mark_secondary({"big": big, "small": small}, set(), threshold=0.8)
        self.assertEqual(low["small"]["role"], "secondary")
        high = mark_secondary({"big": big, "small": big[:19] + ["u"]}, set(), threshold=0.96)
        self.assertEqual(high["small"]["role"], "canonical")

    def test_aggregate_is_never_canonical_and_never_a_parent(self):
        shared = lines("shared", 20)
        pages = {"agg": shared + lines("other", 80), "only": shared, "twin": list(shared)}
        result = mark_secondary(pages, {"agg"})
        self.assertEqual(
            result["agg"], {"role": "aggregate", "secondary_of": None, "containment": None}
        )
        self.assertEqual(result["only"]["role"], "canonical")
        self.assertEqual(result["only"]["secondary_of"], None)
        self.assertEqual(result["twin"]["role"], "secondary")
        self.assertEqual(result["twin"]["secondary_of"], "only")
        parents = {r["secondary_of"] for r in result.values()}
        self.assertNotIn("agg", parents)
        self.assertEqual(result["only"]["aggregate_containment"], {"agg": 1.0})

    def test_lone_page_beside_an_aggregate_is_canonical(self):
        shared = lines("shared", 10)
        result = mark_secondary({"agg": list(shared), "p": list(shared)}, {"agg"})
        self.assertEqual(result["p"]["role"], "canonical")
        self.assertEqual(result["p"]["containment"], 0.0)
        self.assertEqual(result["p"]["aggregate_containment"], {"agg": 1.0})

    def test_aggregate_containment_is_present_and_never_changes_roles(self):
        a = lines("a", 30)
        b = lines("b", 30)
        c = a[:29] + ["c only"]
        agg_lines = a + b
        without = mark_secondary({"a": a, "b": b, "c": c}, set())
        with_agg = mark_secondary({"a": a, "b": b, "c": c, "agg": agg_lines}, {"agg"})
        for pid in ("a", "b", "c"):
            self.assertEqual(without[pid]["role"], with_agg[pid]["role"])
            self.assertEqual(without[pid]["secondary_of"], with_agg[pid]["secondary_of"])
            self.assertEqual(without[pid]["containment"], with_agg[pid]["containment"])
            self.assertIn("aggregate_containment", with_agg[pid])
        self.assertEqual(with_agg["a"]["aggregate_containment"], {"agg": 1.0})
        self.assertEqual(with_agg["b"]["aggregate_containment"], {"agg": 1.0})
        self.assertEqual(with_agg["c"]["aggregate_containment"], {"agg": 29 / 30})
        self.assertEqual(with_agg["c"]["role"], "secondary")
        self.assertEqual(with_agg["c"]["secondary_of"], "a")

    def test_aggregate_containment_has_one_key_per_aggregate(self):
        pages = {"p": lines("p", 5), "g1": lines("p", 5), "g2": lines("q", 5)}
        result = mark_secondary(pages, {"g1", "g2"})
        self.assertEqual(result["p"]["aggregate_containment"], {"g1": 1.0, "g2": 0.0})
        self.assertEqual(result["p"]["role"], "canonical")

    def test_blank_and_whitespace_differences_do_not_affect_roles(self):
        a = ["Alpha", "", "beta   gamma", "   ", "delta"]
        b = ["alpha", "beta gamma", "", "", "DELTA", ""]
        result = mark_secondary({"a": a, "b": b}, set())
        self.assertEqual(roles(result), {"a": ("canonical", None), "b": ("secondary", "a")})
        self.assertEqual(result["a"]["containment"], 1.0)

    def test_page_with_only_blank_lines_is_not_marked_secondary(self):
        result = mark_secondary({"blank": ["", "  "], "real": lines("r", 5)}, set())
        self.assertEqual(result["blank"]["role"], "canonical")
        self.assertEqual(result["blank"]["containment"], 0.0)

    def test_empty_input(self):
        self.assertEqual(mark_secondary({}, set()), {})


class CliTests(unittest.TestCase):
    def test_cli_reads_md_files_and_writes_mapping(self):
        shared = "\n".join(lines("shared", 10))
        with tempfile.TemporaryDirectory() as tmp:
            pages_dir = Path(tmp) / "pages"
            pages_dir.mkdir()
            (pages_dir / "alpha.md").write_text(shared, encoding="utf-8")
            (pages_dir / "beta.md").write_text(shared + "\n\n", encoding="utf-8")
            (pages_dir / "everything.md").write_text(
                shared + "\n" + "\n".join(lines("more", 30)), encoding="utf-8"
            )
            (pages_dir / "ignored.txt").write_text("not a page", encoding="utf-8")
            out = Path(tmp) / "out" / "dedupe.json"
            code = dedupe.main(
                ["--pages-dir", str(pages_dir), "--aggregate", "everything", "--out", str(out)]
            )
            self.assertEqual(code, 0)
            mapping = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(sorted(mapping), ["alpha", "beta", "everything"])
            self.assertEqual(mapping["everything"]["role"], "aggregate")
            self.assertEqual(mapping["alpha"]["role"], "canonical")
            self.assertEqual(mapping["beta"]["role"], "secondary")
            self.assertEqual(mapping["beta"]["secondary_of"], "alpha")
            self.assertEqual(mapping["beta"]["aggregate_containment"], {"everything": 1.0})

    def test_cli_rejects_unknown_aggregate_and_missing_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            pages_dir = Path(tmp) / "pages"
            pages_dir.mkdir()
            (pages_dir / "a.md").write_text("x", encoding="utf-8")
            out = Path(tmp) / "out.json"
            code = dedupe.main(
                ["--pages-dir", str(pages_dir), "--aggregate", "typo", "--out", str(out)]
            )
            self.assertEqual(code, 2)
            self.assertFalse(out.exists())
            code = dedupe.main(["--pages-dir", str(Path(tmp) / "nope"), "--out", str(out)])
            self.assertEqual(code, 2)

    def test_cli_rejects_invalid_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            pages_dir = Path(tmp) / "pages"
            pages_dir.mkdir()
            (pages_dir / "a.md").write_bytes(b"bad \xff\n")
            out = Path(tmp) / "out.json"
            code = dedupe.main(["--pages-dir", str(pages_dir), "--out", str(out)])
            self.assertEqual(code, 2)
            self.assertFalse(out.exists())

    def test_cli_selftest_prints_ok(self):
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "dedupe.py"), "--selftest"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "OK")


if __name__ == "__main__":
    unittest.main()
