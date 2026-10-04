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
TAG_RE = re.compile(
    r"</?(?:system-reminder|system|assistant|user|human|instructions|instruction|"
    r"tool_use|tool_result|function_calls|function_results|thinking|invoke|"
    r"antml:[\w.:-]*)(?=[\s/>])[^>\n]*>",
    re.IGNORECASE,
)

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


def neutralize_text(raw):
    """Return ``(neutral_text, flagged_line_numbers)``; line numbers are 1-based raw lines.

    A line is flagged when a tag token was rewritten on it or when it is
    instruction-shaped. Instruction-shaped lines are flagged but not modified.
    """
    out_lines = []
    flagged = []
    for number, line in enumerate(raw.split("\n"), start=1):
        new_line, replaced = TAG_RE.subn(_neutralize_token, line)
        if replaced or _instruction_shaped(line):
            flagged.append(number)
        out_lines.append(new_line)
    return "\n".join(out_lines), flagged


def check_parity(raw, neutral):
    """Raise ValueError unless the line counts match and every line round-trips via restore.

    A raw line that itself contains a literal U+2039 or U+203A cannot round-trip
    byte-for-byte; for those lines the comparison is restore(neutral) == restore(raw).
    """
    raw_lines = raw.split("\n")
    neutral_lines = neutral.split("\n")
    if len(raw_lines) != len(neutral_lines):
        raise ValueError(
            f"line count mismatch: raw has {len(raw_lines)} lines, "
            f"neutral has {len(neutral_lines)} lines"
        )
    for number, (raw_line, neutral_line) in enumerate(zip(raw_lines, neutral_lines), start=1):
        if restore(neutral_line) == raw_line:
            continue
        has_literal_mark = OPEN_MARK in raw_line or CLOSE_MARK in raw_line
        if has_literal_mark and restore(neutral_line) == restore(raw_line):
            continue
        raise ValueError(f"line {number} does not round-trip through restore")


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

    neutral, flagged = neutralize_text(raw)
    try:
        check_parity(raw, neutral)
    except ValueError as exc:
        print(f"neutralize: parity check failed: {exc}", file=sys.stderr)
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
