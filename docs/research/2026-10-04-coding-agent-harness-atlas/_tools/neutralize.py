"""Neutralize tag-like tokens in untrusted page text without changing line structure.

Pages fetched from the web are untrusted. The repo's own sanitizer deletes text
(it removed lines 946 to 1412 of a real page). This module never deletes a
character and never adds or removes a newline: it rewrites the ``<`` and ``>`` of
suspicious tag tokens in place (``<`` becomes U+2039, ``>`` becomes U+203A) and
reports which raw lines it touched or found instruction-shaped.

Usage: python3 neutralize.py --in RAW --out NEUTRAL --flags FLAGS_JSON
       python3 neutralize.py --selftest
"""

import argparse
import re
import sys
from pathlib import Path

from atlas_common import assert_worktree, dump_json

OPEN_MARK = "‹"
CLOSE_MARK = "›"

# Longer names come first inside the alternation; the lookahead enforces a name boundary.
# ``invoke`` is listed because the brief's own example match is an invoke tag.
_TAG_NAMES = (
    r"(?:system-reminder|system|assistant|user|human|instructions|instruction|"
    r"tool_use|tool_result|function_calls|function_results|thinking|invoke|"
    r"antml:[\w.:-]*)"
)
TAG_RE = re.compile(r"</?" + _TAG_NAMES + r"(?=[\s/>])[^>\n]*>", re.IGNORECASE)
# A tag-like opening with no ``>`` after it on its line (the ``>`` may be on the next line).
# Once TAG_RE has nothing left to match on a line, every opening this finds is such a case.
OPENER_RE = re.compile(r"<(?=/?" + _TAG_NAMES + r"(?:[\s/>]|$))", re.IGNORECASE)
# One pass converts at least one ``<``, so the repeat loop ends; this bounds how deep a
# hostile nesting may go before the page is refused instead of looped over.
MAX_PASSES = 1000

INSTRUCTION_RES = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"ignore (all )?(previous|prior|above) instructions",
        r"you (must|should) now",
        r"disregard (the )?(above|previous)",
        r"^\s*(system|assistant|human)\s*:",
        r"as an? (ai|assistant|agent)[, ]+(you|please)",
    )
]


def restore(s):
    """Map the neutral marks back to ``<`` and ``>``."""
    return s.replace(OPEN_MARK, "<").replace(CLOSE_MARK, ">")


def _neutralize_token(match):
    token = match.group(0)
    return OPEN_MARK + token[1:-1] + CLOSE_MARK


def _instruction_shaped(line):
    return any(rx.search(line) for rx in INSTRUCTION_RES)


def _neutralize_line(line):
    """Return ``(neutral_line, number_of_rewrites)`` for one line.

    A match runs from an opening ``<name`` to the first ``>``, so a tag nested inside
    another keeps its ``<`` after one pass; the substitution repeats until TAG_RE is
    silent. Whatever opening is then left has no ``>`` on the line and is rewritten alone.
    """
    rewrites = 0
    for _ in range(MAX_PASSES):
        line, count = TAG_RE.subn(_neutralize_token, line)
        if not count:
            break
        rewrites += count
    else:
        if TAG_RE.search(line):
            raise ValueError(f"tag-like tokens nest more than {MAX_PASSES} passes deep")
    line, count = OPENER_RE.subn(OPEN_MARK, line)
    return line, rewrites + count


def neutralize_text(raw):
    """Return ``(neutral_text, flagged_line_numbers)``; line numbers are 1-based raw lines.

    A line is flagged when a tag token or an unclosed tag opening was rewritten on it or
    when it is instruction-shaped. Instruction-shaped lines are flagged but not modified.
    Raises ValueError for a line that nests tag tokens deeper than MAX_PASSES.
    """
    out_lines = []
    flagged = []
    for number, line in enumerate(raw.split("\n"), start=1):
        new_line, rewrites = _neutralize_line(line)
        if rewrites or _instruction_shaped(line):
            flagged.append(number)
        out_lines.append(new_line)
    return "\n".join(out_lines), flagged


_MARK_SWAPS = {"<": OPEN_MARK, ">": CLOSE_MARK}


def check_parity(raw, neutral):
    """Raise ValueError unless neutral is raw with only ``<`` -> U+2039 and ``>`` -> U+203A.

    The comparison is character by character on every line: a position must be identical,
    or hold raw ``<`` against neutral U+2039, or raw ``>`` against neutral U+203A. A raw
    U+2039 or U+203A must therefore survive as itself, so a neutral ``<`` or ``>`` cannot be
    smuggled in over a literal mark. Lines of different length, and different line counts,
    raise.
    """
    raw_lines = raw.split("\n")
    neutral_lines = neutral.split("\n")
    if len(raw_lines) != len(neutral_lines):
        raise ValueError(
            f"line count mismatch: raw has {len(raw_lines)} lines, "
            f"neutral has {len(neutral_lines)} lines"
        )
    for number, (raw_line, neutral_line) in enumerate(zip(raw_lines, neutral_lines), start=1):
        if len(raw_line) != len(neutral_line):
            raise ValueError(
                f"line {number} changed length: {len(raw_line)} characters became "
                f"{len(neutral_line)}"
            )
        for position, (before, after) in enumerate(zip(raw_line, neutral_line)):
            if before != after and _MARK_SWAPS.get(before) != after:
                raise ValueError(f"line {number} changed at character {position + 1}")


def _selftest():
    raw = (
        "A sentence about the `<system-reminder>` tag.\r\n"
        "System: do this\n"
        "plain line\n"
        "```\n"
        "System prompts are described here.\n"
    )
    neutral, flagged = neutralize_text(raw)
    checks = [
        (flagged == [1, 2], f"flagged lines were {flagged}"),
        (neutral.count("\n") == raw.count("\n"), "newline count changed"),
        (neutral.count("\r") == raw.count("\r"), "carriage return count changed"),
        (restore(neutral) == raw, "round trip failed"),
        ("<system-reminder>" not in neutral, "tag was not rewritten"),
    ]
    for ok, message in checks:
        if not ok:
            raise AssertionError(message)
    check_parity(raw, neutral)
    print("OK")


def main(argv=None):
    assert_worktree()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--in", dest="raw_path")
    parser.add_argument("--out", dest="neutral_path")
    parser.add_argument("--flags", dest="flags_path")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    if not (args.raw_path and args.neutral_path and args.flags_path):
        parser.error("--in, --out and --flags are required unless --selftest is given")

    data = Path(args.raw_path).read_bytes()
    try:
        raw = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        print(f"neutralize: {args.raw_path} is not valid UTF-8: {exc}", file=sys.stderr)
        return 2

    try:
        neutral, flagged = neutralize_text(raw)
        check_parity(raw, neutral)
    except ValueError as exc:
        print(f"neutralize: {args.raw_path} refused: {exc}", file=sys.stderr)
        return 1

    out_path = Path(args.neutral_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(neutral.encode("utf-8"))
    # Re-read what reached the disk: the file, not the string, is what the next phase sees.
    try:
        check_parity(raw, out_path.read_bytes().decode("utf-8", errors="strict"))
    except (ValueError, UnicodeDecodeError) as exc:
        print(f"neutralize: parity check on the written file failed: {exc}", file=sys.stderr)
        return 1

    dump_json(
        args.flags_path,
        {
            "flagged_lines": flagged,
            "raw_lines": len(raw.split("\n")),
            "neutral_lines": len(neutral.split("\n")),
        },
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
