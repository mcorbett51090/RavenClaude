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

import chunk as chunk_tool  # noqa: E402
from chunk import Chunk, chunk_page, coverage_report, make_batches, split_gemini  # noqa: E402


def make_chunk(number, size):
    return Chunk(
        id=f"p#{number}",
        page_id="p",
        start_line=number,
        end_line=number,
        text="x" * size,
        bytes=size,
    )


class ChunkPageTests(unittest.TestCase):
    def assert_covers_once(self, text, chunks):
        lines = text.split("\n")
        seen = [0] * (len(lines) + 1)
        for c in chunks:
            self.assertEqual(c.text, "\n".join(lines[c.start_line - 1 : c.end_line]))
            self.assertEqual(c.bytes, len(c.text.encode("utf-8")))
            for n in range(c.start_line, c.end_line + 1):
                seen[n] += 1
        self.assertEqual(seen[1:], [1] * len(lines))
        expected = 1
        for c in chunks:
            self.assertEqual(c.start_line, expected)
            expected = c.end_line + 1
        self.assertEqual(expected, len(lines) + 1)
        self.assertEqual("\n".join(c.text for c in chunks), text)

    def test_300_line_page_with_four_sections_is_covered_once(self):
        lines = ["# Title", "intro"]
        for section in range(1, 5):
            body = 74 if section < 4 else 76
            lines.append(f"## Section {section}")
            lines += [f"s{section} line {i}" for i in range(body - 1)]
        text = "\n".join(lines)
        self.assertEqual(len(text.split("\n")), 300)
        chunks = chunk_page("pg", text)
        self.assertEqual([c.id for c in chunks], [f"pg#{n}" for n in range(1, 6)])
        self.assertEqual([c.start_line for c in chunks], [1, 3, 77, 151, 225])
        self.assertTrue(all(c.page_id == "pg" for c in chunks))
        self.assert_covers_once(text, chunks)

        everything = coverage_report(300, chunks, {c.id for c in chunks})
        self.assertEqual(everything["missing_ranges"], [])
        self.assertEqual(everything["lines_total"], 300)
        self.assertEqual(everything["lines_in_chunks"], 300)
        self.assertEqual(everything["lines_read"], 300)

        unread = chunks[2]
        partial = coverage_report(300, chunks, {c.id for c in chunks if c is not unread})
        self.assertEqual(partial["missing_ranges"], [[unread.start_line, unread.end_line]])
        self.assertEqual(partial["lines_read"], 300 - (unread.end_line - unread.start_line + 1))

        adjacent = coverage_report(300, chunks, {chunks[0].id, chunks[3].id, chunks[4].id})
        self.assertEqual(adjacent["missing_ranges"], [[chunks[1].start_line, chunks[2].end_line]])

    def test_coverage_report_counts_lines_in_no_chunk_as_missing(self):
        text = "\n".join(["## A", "a", "## B", "b", "## C", "c"])
        chunks = chunk_page("p", text)
        without_middle = [chunks[0], chunks[2]]
        report = coverage_report(6, without_middle, {c.id for c in without_middle})
        self.assertEqual(report["lines_in_chunks"], 4)
        self.assertEqual(report["lines_read"], 4)
        self.assertEqual(report["missing_ranges"], [[3, 4]])
        nothing = coverage_report(6, chunks, set())
        self.assertEqual(nothing["missing_ranges"], [[1, 6]])
        self.assertEqual(nothing["lines_read"], 0)

    def test_heading_inside_fenced_code_does_not_split(self):
        text = "\n".join(
            [
                "## One",
                "```python",
                "## not a heading",
                "```",
                "~~~",
                "## also not a heading",
                "~~~",
                "```inline```",
                "## Two",
                "tail",
            ]
        )
        chunks = chunk_page("p", text)
        self.assertEqual([(c.start_line, c.end_line) for c in chunks], [(1, 8), (9, 10)])
        self.assert_covers_once(text, chunks)

    def test_heading_after_fence_closes_still_splits(self):
        text = "\n".join(["```", "## inside", "```", "## outside", "x"])
        chunks = chunk_page("p", text)
        self.assertEqual([(c.start_line, c.end_line) for c in chunks], [(1, 3), (4, 5)])

    def test_only_level_two_headings_split(self):
        text = "\n".join(["# one", "### three", "##no space", "## two", "body"])
        chunks = chunk_page("p", text)
        self.assertEqual([(c.start_line, c.end_line) for c in chunks], [(1, 3), (4, 5)])

    def test_first_line_heading_does_not_make_an_empty_chunk(self):
        chunks = chunk_page("p", "## A\nx\n## B\ny")
        self.assertEqual([(c.start_line, c.end_line) for c in chunks], [(1, 2), (3, 4)])

    def test_40kb_section_splits_at_blank_lines_within_max_bytes(self):
        lines = ["## Big"]
        for i in range(400):
            lines.append(f"{i:04d} " + "w" * 95)
            if i % 10 == 9:
                lines.append("")
        text = "\n".join(lines)
        self.assertGreater(len(text.encode("utf-8")), 40000)
        chunks = chunk_page("p", text, max_bytes=12000)
        self.assertGreater(len(chunks), 3)
        self.assertTrue(all(c.bytes <= 12000 for c in chunks), [c.bytes for c in chunks])
        self.assert_covers_once(text, chunks)
        source = text.split("\n")
        for c in chunks[:-1]:
            self.assertEqual(source[c.end_line - 1], "", "cut was not at a blank line")

    def test_oversize_section_without_blank_lines_splits_at_line_boundaries(self):
        lines = ["## Big"] + [f"{i:04d} " + "w" * 95 for i in range(400)]
        text = "\n".join(lines)
        chunks = chunk_page("p", text, max_bytes=12000)
        self.assertTrue(all(c.bytes <= 12000 for c in chunks))
        self.assertGreater(len(chunks), 3)
        self.assert_covers_once(text, chunks)

    def test_oversize_single_line_stands_alone_and_rest_stays_bounded(self):
        huge = "z" * 30000
        lines = ["## Big", "short a", "", "short b", huge, "short c", "", "short d"]
        text = "\n".join(lines)
        chunks = chunk_page("p", text, max_bytes=12000)
        self.assert_covers_once(text, chunks)
        alone = [c for c in chunks if c.text == huge]
        self.assertEqual(len(alone), 1)
        self.assertEqual(alone[0].start_line, alone[0].end_line)
        self.assertTrue(all(c.bytes <= 12000 for c in chunks if c.text != huge))

    def test_page_whose_only_line_exceeds_max_bytes_is_one_chunk(self):
        text = "q" * 20000
        chunks = chunk_page("p", text, max_bytes=12000)
        self.assertEqual(len(chunks), 1)
        self.assertEqual((chunks[0].start_line, chunks[0].end_line), (1, 1))
        self.assertEqual(chunks[0].bytes, 20000)
        self.assertEqual(chunks[0].id, "p#1")

    def test_empty_page_is_one_empty_chunk_covering_line_one(self):
        chunks = chunk_page("p", "")
        self.assertEqual(len(chunks), 1)
        self.assertEqual((chunks[0].start_line, chunks[0].end_line), (1, 1))
        self.assertEqual((chunks[0].text, chunks[0].bytes), ("", 0))

    def test_page_without_headings_is_split_only_by_size(self):
        text = "\n".join("p" * 99 for _ in range(300))
        chunks = chunk_page("p", text, max_bytes=5000)
        self.assertTrue(all(c.bytes <= 5000 for c in chunks))
        self.assertGreater(len(chunks), 1)
        self.assert_covers_once(text, chunks)

    def test_multibyte_text_is_measured_in_utf8_bytes(self):
        line = "é" * 50  # 100 bytes
        text = "\n".join([line] * 200)
        chunks = chunk_page("p", text, max_bytes=1000)
        self.assertTrue(all(c.bytes <= 1000 for c in chunks))
        self.assertEqual(chunks[0].bytes, len(chunks[0].text.encode("utf-8")))
        self.assert_covers_once(text, chunks)

    def test_text_with_trailing_newline_keeps_the_empty_last_line(self):
        text = "## A\nx\n"
        chunks = chunk_page("p", text)
        self.assertEqual(chunks[-1].end_line, 3)
        self.assert_covers_once(text, chunks)


class SplitGeminiTests(unittest.TestCase):
    def test_only_title_link_lines_start_a_page(self):
        text = "\n".join(
            [
                "preamble line",
                "more preamble",
                "# [Title One](https://ai.example/one)",
                "# Plain heading inside page",
                "body one",
                "# [Title Two](https://ai.example/two)   ",
                "# Another plain heading",
                "text",
                "# plain third",
                "# [Title Three](http://ai.example/three)",
                "# plain four",
                "# plain five",
                "end",
            ]
        )
        pages = split_gemini(text)
        self.assertEqual(
            [p["title"] for p in pages], ["preamble", "Title One", "Title Two", "Title Three"]
        )
        self.assertEqual(pages[0]["url"], None)
        self.assertEqual(
            [p["url"] for p in pages[1:]],
            ["https://ai.example/one", "https://ai.example/two", "http://ai.example/three"],
        )
        self.assertEqual("\n".join(p["text"] for p in pages), text)
        self.assertEqual(
            [(p["start_line"], p["end_line"]) for p in pages],
            [(1, 2), (3, 5), (6, 9), (10, 13)],
        )
        for p in pages:
            self.assertEqual(
                p["text"], "\n".join(text.split("\n")[p["start_line"] - 1 : p["end_line"]])
            )

    def test_lines_that_only_look_like_titles_do_not_start_pages(self):
        text = "\n".join(
            [
                "# [T](not-a-url)",
                "# [T](https://x.example/a b)",
                "#  [T](https://x.example/a)",
                "## [T](https://x.example/a)",
                "# [T](https://x.example/a) trailing",
                "# [](https://x.example/a)",
            ]
        )
        pages = split_gemini(text)
        self.assertEqual([p["title"] for p in pages], ["preamble"])
        self.assertEqual(pages[0]["text"], text)

    def test_no_preamble_when_text_starts_with_a_title(self):
        pages = split_gemini("# [A](https://x.example/a)\nbody\n# [B](https://x.example/b)\nmore")
        self.assertEqual([p["title"] for p in pages], ["A", "B"])
        self.assertEqual(pages[0]["start_line"], 1)

    def test_blank_only_preamble_is_omitted(self):
        pages = split_gemini("\n\n# [A](https://x.example/a)\nbody")
        self.assertEqual([p["title"] for p in pages], ["A"])
        self.assertEqual(pages[0]["start_line"], 3)

    def test_empty_text_has_no_pages(self):
        self.assertEqual(split_gemini(""), [])


class MakeBatchesTests(unittest.TestCase):
    def test_respects_batch_bytes_and_keeps_order(self):
        sizes = [5000, 6000, 4000, 9000, 7000, 7000, 1000]
        chunks = [make_chunk(n, s) for n, s in enumerate(sizes, start=1)]
        batches = make_batches(chunks, batch_bytes=16000)
        self.assertEqual(batches, [["p#1", "p#2", "p#3"], ["p#4", "p#5"], ["p#6", "p#7"]])
        by_id = {c.id: c.bytes for c in chunks}
        for batch in batches:
            self.assertLessEqual(sum(by_id[i] for i in batch), 16000)
        self.assertEqual([i for b in batches for i in b], [c.id for c in chunks])

    def test_oversize_chunk_gets_its_own_batch(self):
        sizes = [3000, 20000, 3000, 3000]
        chunks = [make_chunk(n, s) for n, s in enumerate(sizes, start=1)]
        self.assertEqual(
            make_batches(chunks, batch_bytes=16000), [["p#1"], ["p#2"], ["p#3", "p#4"]]
        )

    def test_exact_fit_stays_in_one_batch_and_empty_input_gives_no_batches(self):
        chunks = [make_chunk(1, 8000), make_chunk(2, 8000)]
        self.assertEqual(make_batches(chunks, batch_bytes=16000), [["p#1", "p#2"]])
        self.assertEqual(make_batches([], batch_bytes=16000), [])

    def test_default_batch_size_is_16000(self):
        chunks = [make_chunk(1, 9000), make_chunk(2, 9000)]
        self.assertEqual(make_batches(chunks), [["p#1"], ["p#2"]])


class CliTests(unittest.TestCase):
    def test_cli_writes_exact_chunk_files_and_index(self):
        text = "\r\n".join(["intro", "## A", "a line", "## B", "b line", ""])
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.md"
            page.write_bytes(text.encode("utf-8"))
            out_dir = Path(tmp) / "chunks"
            code = chunk_tool.main(
                ["--page", str(page), "--page-id", "vendor-page", "--out-dir", str(out_dir)]
            )
            self.assertEqual(code, 0)
            index = json.loads((out_dir / "chunks.json").read_text(encoding="utf-8"))
            self.assertEqual(
                [e["id"] for e in index], ["vendor-page#1", "vendor-page#2"] + ["vendor-page#3"]
            )
            joined = []
            for n, entry in enumerate(index, start=1):
                payload = (out_dir / f"vendor-page-{n}.md").read_bytes()
                joined.append(payload.decode("utf-8"))
                self.assertEqual(entry["sha256"], hashlib.sha256(payload).hexdigest())
                self.assertEqual(entry["bytes"], len(payload))
                self.assertEqual(entry["page_id"], "vendor-page")
                self.assertEqual(
                    sorted(entry), ["bytes", "end_line", "id", "page_id", "sha256", "start_line"]
                )
            self.assertEqual("\n".join(joined), text)

    def test_cli_honours_max_bytes(self):
        text = "\n".join("l" * 99 for _ in range(100))
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.md"
            page.write_text(text, encoding="utf-8")
            out_dir = Path(tmp) / "chunks"
            code = chunk_tool.main(
                ["--page", str(page), "--page-id", "p", "--out-dir", str(out_dir)]
                + ["--max-bytes", "1000"]
            )
            self.assertEqual(code, 0)
            index = json.loads((out_dir / "chunks.json").read_text(encoding="utf-8"))
            self.assertGreater(len(index), 5)
            self.assertTrue(all(e["bytes"] <= 1000 for e in index))

    def test_cli_rejects_unsafe_page_id_and_invalid_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.md"
            page.write_bytes(b"fine\n")
            out_dir = Path(tmp) / "chunks"
            for bad in ("../x", "a/b", ".hidden"):
                code = chunk_tool.main(
                    ["--page", str(page), "--page-id", bad, "--out-dir", str(out_dir)]
                )
                self.assertEqual(code, 2, bad)
            page.write_bytes(b"bad \xff byte\n")
            code = chunk_tool.main(
                ["--page", str(page), "--page-id", "p", "--out-dir", str(out_dir)]
            )
            self.assertEqual(code, 2)
            self.assertFalse(out_dir.exists())

    def test_cli_selftest_prints_ok(self):
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "chunk.py"), "--selftest"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "OK")


if __name__ == "__main__":
    unittest.main()
