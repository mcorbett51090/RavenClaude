"""Split a fetched page into line-covering chunks, split the Gemini docs file, report coverage.

Every function except the CLI is pure. A chunk is a run of whole lines; the chunks of a
page cover every line exactly once, so a reader can prove which lines were never read.

Usage: python3 chunk.py --page FILE --page-id ID --out-dir DIR [--max-bytes N]
       python3 chunk.py --selftest
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from atlas_common import assert_worktree, dump_json, sha256_bytes

DEFAULT_MAX_BYTES = 12000
DEFAULT_BATCH_BYTES = 16000

GEMINI_TITLE_RE = re.compile(r"^# \[(?P<title>.+?)\]\((?P<url>https?://[^)\s]+)\)\s*$")


@dataclass(frozen=True)
class Chunk:
    id: str
    page_id: str
    start_line: int  # 1-based, inclusive
    end_line: int  # 1-based, inclusive
    text: str  # the exact lines joined by "\n", no added header
    bytes: int  # UTF-8 length of text


def _fence_char(line):
    if line.startswith("```"):
        return "`"
    if line.startswith("~~~"):
        return "~"
    return None


def _section_starts(lines):
    """0-based indexes where a level-2 heading outside a fenced code block starts a section."""
    starts = [0]
    fence = None  # (char, run length) while inside a fenced block
    for index, line in enumerate(lines):
        char = _fence_char(line)
        if char == "`" and fence is None and "`" in line.lstrip("`"):
            char = None  # inline code such as ```x```, not a fence opener
        if char is not None:
            run = len(line) - len(line.lstrip(char))
            if fence is None:
                fence = (char, run)
                continue
            closes = char == fence[0] and run >= fence[1] and not line.lstrip(char).strip()
            if closes:
                fence = None
            continue
        if fence is None and line.startswith("## ") and index > 0:
            starts.append(index)
    return starts


def _split_by_size(lens, lines, lo, hi, max_bytes):
    """Split lines[lo:hi] into half-open ranges of at most max_bytes (joined size).

    Cut after the last blank line in the piece when there is one, else at the line
    boundary before the line that would overflow. A single over-long line stands alone.
    """

    def joined(a, b):
        return sum(lens[a:b]) + (b - a - 1)

    ranges = []
    start = lo
    size = 0
    last_blank = None
    i = lo
    while i < hi:
        added = lens[i] if i == start else lens[i] + 1
        if i > start and size + added > max_bytes:
            cut = last_blank + 1 if last_blank is not None else i
            ranges.append((start, cut))
            start = cut
            size = joined(start, i) if i > start else 0
            last_blank = None
            continue
        size += added
        if not lines[i].strip():
            last_blank = i
        i += 1
    ranges.append((start, hi))
    return ranges


def chunk_page(page_id, text, max_bytes=DEFAULT_MAX_BYTES):
    """Split text into contiguous chunks covering every line exactly once."""
    lines = text.split("\n")
    lens = [len(line.encode("utf-8")) for line in lines]
    starts = _section_starts(lines)
    bounds = starts + [len(lines)]
    ranges = []
    for lo, hi in zip(bounds, bounds[1:]):
        if sum(lens[lo:hi]) + (hi - lo - 1) <= max_bytes:
            ranges.append((lo, hi))
        else:
            ranges.extend(_split_by_size(lens, lines, lo, hi, max_bytes))
    chunks = []
    for number, (lo, hi) in enumerate(ranges, start=1):
        body = "\n".join(lines[lo:hi])
        chunks.append(
            Chunk(
                id=f"{page_id}#{number}",
                page_id=page_id,
                start_line=lo + 1,
                end_line=hi,
                text=body,
                bytes=len(body.encode("utf-8")),
            )
        )
    return chunks


def split_gemini(text):
    """Split the Gemini docs file into pages; only a ``# [title](url)`` line starts a page."""
    lines = text.split("\n")
    title_at = [i for i, line in enumerate(lines) if GEMINI_TITLE_RE.match(line)]
    pages = []
    first = title_at[0] if title_at else len(lines)
    if any(line.strip() for line in lines[:first]):
        pages.append(
            {
                "title": "preamble",
                "url": None,
                "start_line": 1,
                "end_line": first,
                "text": "\n".join(lines[:first]),
            }
        )
    ends = title_at[1:] + [len(lines)]
    for lo, hi in zip(title_at, ends):
        match = GEMINI_TITLE_RE.match(lines[lo])
        pages.append(
            {
                "title": match.group("title"),
                "url": match.group("url"),
                "start_line": lo + 1,
                "end_line": hi,
                "text": "\n".join(lines[lo:hi]),
            }
        )
    return pages


def coverage_report(total_lines, chunks, read_ids):
    """Report how many lines the chunks cover and how many were read, with the gaps."""
    in_chunk = bytearray(total_lines + 1)
    read = bytearray(total_lines + 1)
    for chunk in chunks:
        for line in range(max(chunk.start_line, 1), min(chunk.end_line, total_lines) + 1):
            in_chunk[line] = 1
            if chunk.id in read_ids:
                read[line] = 1
    missing = []
    run_start = None
    for line in range(1, total_lines + 2):
        unread = line <= total_lines and not read[line]
        if unread and run_start is None:
            run_start = line
        elif not unread and run_start is not None:
            missing.append([run_start, line - 1])
            run_start = None
    return {
        "lines_total": total_lines,
        "lines_in_chunks": sum(in_chunk),
        "lines_read": sum(read),
        "missing_ranges": missing,
    }


def make_batches(chunks, batch_bytes=DEFAULT_BATCH_BYTES):
    """Group chunk ids, in input order, into batches of at most batch_bytes total.

    The default is provisional: a later pilot measures the safe size. A chunk larger
    than batch_bytes gets a batch to itself.
    """
    batches = []
    current = []
    current_bytes = 0
    for chunk in chunks:
        if chunk.bytes > batch_bytes:
            if current:
                batches.append(current)
                current, current_bytes = [], 0
            batches.append([chunk.id])
            continue
        if current and current_bytes + chunk.bytes > batch_bytes:
            batches.append(current)
            current, current_bytes = [], 0
        current.append(chunk.id)
        current_bytes += chunk.bytes
    if current:
        batches.append(current)
    return batches


def _verify_cover(total_lines, chunks):
    """Raise ValueError unless the chunks are contiguous and cover lines 1..total once."""
    expected = 1
    for chunk in chunks:
        if chunk.start_line != expected or chunk.end_line < chunk.start_line:
            raise ValueError(f"chunk {chunk.id} does not continue at line {expected}")
        expected = chunk.end_line + 1
    if expected != total_lines + 1:
        raise ValueError(f"chunks end at line {expected - 1}, page has {total_lines} lines")


def _selftest():
    text = "\n".join(["intro", "## A", "a1", "```", "## not a heading", "```", "## B", "b1"])
    chunks = chunk_page("p", text)
    if [(c.start_line, c.end_line) for c in chunks] != [(1, 1), (2, 6), (7, 8)]:
        raise AssertionError(f"unexpected chunk ranges: {chunks}")
    _verify_cover(8, chunks)
    report = coverage_report(8, chunks, {chunks[0].id, chunks[2].id})
    if report["missing_ranges"] != [[2, 6]]:
        raise AssertionError(f"unexpected coverage report: {report}")
    if make_batches(chunks, 10) != [["p#1"], ["p#2"], ["p#3"]]:
        raise AssertionError("unexpected batches")
    pages = split_gemini("pre\n# [T](https://x.example/a)\n# plain\nbody")
    if [p["title"] for p in pages] != ["preamble", "T"]:
        raise AssertionError(f"unexpected gemini pages: {pages}")
    print("OK")


def main(argv=None):
    assert_worktree()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--page")
    parser.add_argument("--page-id")
    parser.add_argument("--out-dir")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    if not (args.page and args.page_id and args.out_dir):
        parser.error("--page, --page-id and --out-dir are required unless --selftest is given")
    if args.max_bytes < 1:
        parser.error("--max-bytes must be at least 1")
    if re.search(r"[/\\]", args.page_id) or args.page_id.startswith("."):
        print(f"chunk: unsafe page id {args.page_id!r}", file=sys.stderr)
        return 2

    data = Path(args.page).read_bytes()
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        print(f"chunk: {args.page} is not valid UTF-8: {exc}", file=sys.stderr)
        return 2

    chunks = chunk_page(args.page_id, text, args.max_bytes)
    try:
        _verify_cover(len(text.split("\n")), chunks)
    except ValueError as exc:
        print(f"chunk: coverage check failed: {exc}", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for number, chunk in enumerate(chunks, start=1):
        payload = chunk.text.encode("utf-8")
        (out_dir / f"{args.page_id}-{number}.md").write_bytes(payload)
        index.append(
            {
                "id": chunk.id,
                "page_id": chunk.page_id,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "bytes": chunk.bytes,
                "sha256": sha256_bytes(payload),
            }
        )
    dump_json(out_dir / "chunks.json", index)
    return 0


if __name__ == "__main__":
    sys.exit(main())
