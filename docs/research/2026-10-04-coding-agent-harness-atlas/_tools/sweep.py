"""Absence sweep: the only licence to write "undocumented" about a vendor.

The sweep scans the whole raw mirror, excluded pages included, line by line for each term
(case-insensitive regular expressions) and also for a positive-control term known to be on
that vendor's pages. An empty search from a blind probe and from an empty subject look the
same, so a sweep whose control finds nothing raises instead of returning "zero hits".

A hit's text is the line, or for a line longer than 200 characters a 200-character window that
starts 60 characters before the first match, so a match deep inside a long line stays visible.

Terms match one line at a time; a pattern that needs to span a line break cannot hit. Lines
end at a line feed; a carriage return before it is not part of the line, so a pattern anchored
with $ matches a page with CRLF line breaks as it does one with LF.

Usage: python3 sweep.py --pages-dir DIR --term REGEX [--term REGEX ...] --control REGEX --out JSON
       python3 sweep.py --selftest
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

from atlas_common import assert_worktree, dump_json

MAX_HITS = 200
MAX_TEXT = 200
CONTEXT = 60


class SweepBlindError(RuntimeError):
    """The positive control matched nothing, so the probe could not have returned anything."""


def _compile(pattern):
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error as exc:
        raise ValueError(f"invalid regular expression {pattern!r}: {exc}") from exc


def corpus_digest(pages):
    """SHA-256 over the sorted lines page id + NUL + sha256(page text), each ending in LF."""
    lines = sorted(
        f"{pid}\0{hashlib.sha256(text.encode('utf-8')).hexdigest()}" for pid, text in pages.items()
    )
    return hashlib.sha256("".join(f"{line}\n" for line in lines).encode("utf-8")).hexdigest()


def sweep(pages, terms, positive_control):
    """Scan every page for the terms and the control; raise SweepBlindError on a blind probe."""
    term_res = [_compile(t) for t in terms]
    control_re = _compile(positive_control)
    if control_re.search(""):
        raise ValueError(
            f"positive control {positive_control!r} matches the empty string, so it would hit "
            f"on any page and could not show that the probe sees the vendor's text"
        )
    hits = []
    hit_count = 0
    control_hits = 0
    for pid in sorted(pages):
        for number, line in enumerate(pages[pid].split("\n"), 1):
            line = line.rstrip("\r")
            if control_re.search(line):
                control_hits += 1
            starts = [m.start() for m in (r.search(line) for r in term_res) if m]
            if starts:
                hit_count += 1
                if len(hits) < MAX_HITS:
                    begin = max(0, min(starts) - CONTEXT)
                    hits.append(
                        {"page": pid, "line": number, "text": line[begin : begin + MAX_TEXT]}
                    )
    if control_hits == 0:
        raise SweepBlindError(
            f"positive control {positive_control!r} matched no line in {len(pages)} pages: "
            f"the probe could not have returned anything, so a zero-hit result for "
            f"{list(terms)!r} would not be evidence of absence"
        )
    return {
        "terms": list(terms),
        "pages_scanned": len(pages),
        "corpus_sha256": corpus_digest(pages),
        "hits": hits,
        "hit_count": hit_count,
        "positive_control_term": positive_control,
        "positive_control_hits": control_hits,
    }


def _selftest():
    pages = {"b": "alpha\nneedle here\n", "a": "control line\nneedle again\nneedle\n"}
    result = sweep(pages, ["needle"], "control")
    expected = [("a", 2), ("a", 3), ("b", 2)]
    if [(h["page"], h["line"]) for h in result["hits"]] != expected or result["hit_count"] != 3:
        raise AssertionError(f"unexpected hits: {result}")
    if sweep(pages, ["nothing-like-this"], "CONTROL")["hit_count"] != 0:
        raise AssertionError("expected a clean zero-hit result")
    try:
        sweep(pages, ["needle"], "absent-control")
    except SweepBlindError:
        pass
    else:
        raise AssertionError("a blind probe did not raise")
    try:
        sweep(pages, ["("], "control")
    except ValueError:
        pass
    else:
        raise AssertionError("an invalid regex did not raise")
    print("OK")


def _read_pages(pages_dir):
    pages = {}
    for path in sorted(pages_dir.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.stem in pages:
            raise ValueError(f"two files share the page id {path.stem!r} in {pages_dir}")
        pages[path.stem] = path.read_bytes().decode("utf-8", errors="strict")
    return pages


def main(argv=None):
    assert_worktree()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pages-dir")
    parser.add_argument("--term", action="append", default=[])
    parser.add_argument("--control")
    parser.add_argument("--out")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    if not (args.pages_dir and args.term and args.control and args.out):
        parser.error("--pages-dir, --term, --control and --out are required unless --selftest")

    pages_dir = Path(args.pages_dir)
    if not pages_dir.is_dir():
        print(f"sweep: {pages_dir} is not a directory", file=sys.stderr)
        return 2
    try:
        pages = _read_pages(pages_dir)
        result = sweep(pages, args.term, args.control)
    except (UnicodeDecodeError, ValueError) as exc:
        print(f"sweep: {exc}", file=sys.stderr)
        return 2
    except SweepBlindError as exc:
        print(f"sweep: BLIND PROBE: {exc}", file=sys.stderr)
        return 3
    dump_json(args.out, result)
    print(f"hit_count {result['hit_count']} control_hits {result['positive_control_hits']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
