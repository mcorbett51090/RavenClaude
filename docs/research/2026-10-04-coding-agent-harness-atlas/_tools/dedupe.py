"""Mark near-duplicate pages as secondary so extraction reads each fact once.

Containment is the fraction of one page's non-blank normalized lines found in another
page. Aggregate pages (for example a combined llms-full file) are never extracted and
never a parent; their containment is reported for information only.

Usage: python3 dedupe.py --pages-dir DIR --aggregate ID [--aggregate ID] --out JSON
       python3 dedupe.py --selftest
"""

import argparse
import sys
from pathlib import Path

from atlas_common import assert_worktree, dump_json


def norm_line(s):
    """Strip, collapse internal whitespace, lowercase."""
    return " ".join(s.split()).lower()


def _nonblank(lines):
    return [n for n in (norm_line(line) for line in lines) if n]


def _containment(a_norm, b_set):
    if not a_norm:
        return 0.0
    return sum(1 for line in a_norm if line in b_set) / len(a_norm)


def line_containment(a_lines, b_lines):
    """Fraction of A's non-blank normalized lines that appear in B's normalized lines."""
    return _containment(_nonblank(a_lines), set(_nonblank(b_lines)))


def mark_secondary(pages, aggregates, threshold=0.9):
    """Classify every page as aggregate, canonical or secondary.

    A page is secondary of its best-containing non-aggregate page when that containment
    is at least threshold, unless the two contain each other at or above the threshold
    and this page is the canonical one (more non-blank lines wins; on a tie the
    lexicographically smaller id wins). Ties between equally good parents go to the
    larger page, then to the smaller id.
    """
    norm = {pid: _nonblank(lines) for pid, lines in pages.items()}
    sets = {pid: set(lines) for pid, lines in norm.items()}
    aggregate_ids = sorted(pid for pid in pages if pid in aggregates)
    others = sorted(pid for pid in pages if pid not in aggregates)

    result = {}
    for pid in aggregate_ids:
        result[pid] = {"role": "aggregate", "secondary_of": None, "containment": None}

    def is_canonical_over(pid, other):
        """True when pid beats other as the canonical copy of mutually containing pages."""
        if len(norm[pid]) != len(norm[other]):
            return len(norm[pid]) > len(norm[other])
        return pid < other

    for pid in others:
        scores = {q: _containment(norm[pid], sets[q]) for q in others if q != pid}
        entry = {
            "aggregate_containment": {
                agg: _containment(norm[pid], sets[agg]) for agg in aggregate_ids
            }
        }
        if not scores:
            entry.update({"role": "canonical", "secondary_of": None, "containment": 0.0})
            result[pid] = entry
            continue
        best_score = max(scores.values())
        parent = min(
            (q for q in scores if scores[q] == best_score),
            key=lambda q: (-len(norm[q]), q),
        )
        secondary = best_score >= threshold
        if secondary:
            mutual = _containment(norm[parent], sets[pid]) >= threshold
            if mutual and is_canonical_over(pid, parent):
                secondary = False
        if secondary:
            entry.update({"role": "secondary", "secondary_of": parent, "containment": best_score})
        else:
            entry.update({"role": "canonical", "secondary_of": None, "containment": best_score})
        result[pid] = entry
    return result


def _selftest():
    pages = {
        "a": ["one", "two", "three", ""],
        "b": ["One", " two ", "three"],
        "agg": ["one", "two", "three", "four"],
    }
    result = mark_secondary(pages, {"agg"})
    expected = {
        "a": ("canonical", None),
        "b": ("secondary", "a"),
        "agg": ("aggregate", None),
    }
    got = {pid: (r["role"], r["secondary_of"]) for pid, r in result.items()}
    if got != expected:
        raise AssertionError(f"unexpected roles: {got}")
    if line_containment(["x", "y"], ["x"]) != 0.5 or line_containment([""], ["x"]) != 0.0:
        raise AssertionError("unexpected containment")
    print("OK")


def main(argv=None):
    assert_worktree()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pages-dir")
    parser.add_argument("--aggregate", action="append", default=[])
    parser.add_argument("--out")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    if not (args.pages_dir and args.out):
        parser.error("--pages-dir and --out are required unless --selftest is given")

    pages_dir = Path(args.pages_dir)
    if not pages_dir.is_dir():
        print(f"dedupe: {pages_dir} is not a directory", file=sys.stderr)
        return 2
    pages = {}
    for path in sorted(pages_dir.glob("*.md")):
        try:
            text = path.read_bytes().decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            print(f"dedupe: {path} is not valid UTF-8: {exc}", file=sys.stderr)
            return 2
        pages[path.stem] = text.split("\n")
    unknown = sorted(set(args.aggregate) - set(pages))
    if unknown:
        print(f"dedupe: aggregate id(s) not found in {pages_dir}: {unknown}", file=sys.stderr)
        return 2

    dump_json(args.out, mark_secondary(pages, set(args.aggregate)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
