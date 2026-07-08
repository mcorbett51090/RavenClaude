#!/usr/bin/env python3
"""flesch_kincaid.py - a zero-dependency reading-level checker.

Makes the Flesch-Kincaid Grade Level a computation instead of a guess, so the
`gold-standard-website-pipeline` **G4** acceptance bar ("reading level hits a
stated target - FK grade <= the ceiling named for the G1 audience") has a real
runnable checker (Tier 1), matching the tiered "tool unavailable -> closeable
Conditional, never a silent wedge" pattern the rest of the pipeline uses. Two
modes:

  grade     Given a text file (or stdin), report the Flesch-Kincaid Grade Level
            plus the word / sentence / syllable counts it is computed from.

  check     Given a text file (or stdin) and --max <grade>, exit non-zero if the
            text reads above the ceiling - so it can gate a PR or a copy review.
            Example: FK <= 8 for a broad consumer site, <= 12 for technical/B2B.

This is a HEURISTIC checker: the syllable count is a rule-based estimate (vowel
groups with common adjustments), which is how every FK implementation works -
English spelling has no closed-form syllable count. Treat the grade as a
reproducible proxy a second reviewer gets the same number from, not as ground
truth about comprehension. Strip HTML/markup to plain prose before measuring;
measure the copy a reader actually reads. Stdlib only (argparse, re, sys); runs
anywhere Python 3.8+ is present.

The math (Kincaid et al. 1975, the standard FKGL formula):

    FKGL = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
"""

from __future__ import annotations

import argparse
import re
import sys

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
_SENTENCE_RE = re.compile(r"[.!?]+(?:\s|$)")
_VOWEL_GROUP_RE = re.compile(r"[aeiouy]+")


def count_syllables(word: str) -> int:
    """Heuristic syllable count for a single English word (>= 1)."""
    w = word.lower().strip("'-")
    if not w:
        return 0
    groups = _VOWEL_GROUP_RE.findall(w)
    n = len(groups)
    # Silent trailing "e" (but not "-le" as in "table", which is syllabic).
    if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1:
        n -= 1
    return max(1, n)


def analyze(text: str) -> dict:
    """Return counts + Flesch-Kincaid Grade Level for a block of prose."""
    words = _WORD_RE.findall(text)
    n_words = len(words)
    n_sentences = max(1, len(_SENTENCE_RE.findall(text)))
    n_syllables = sum(count_syllables(w) for w in words)
    if n_words == 0:
        return {"words": 0, "sentences": n_sentences, "syllables": 0, "fkgl": 0.0}
    fkgl = 0.39 * (n_words / n_sentences) + 11.8 * (n_syllables / n_words) - 15.59
    return {
        "words": n_words,
        "sentences": n_sentences,
        "syllables": n_syllables,
        "fkgl": round(fkgl, 2),
    }


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def cmd_grade(args: argparse.Namespace) -> int:
    r = analyze(_read(args.file))
    print(
        f"FK grade: {r['fkgl']}  "
        f"(words={r['words']}, sentences={r['sentences']}, syllables={r['syllables']})"
    )
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    r = analyze(_read(args.file))
    ok = r["fkgl"] <= args.max
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] FK grade {r['fkgl']} vs ceiling {args.max}  (words={r['words']})")
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flesch_kincaid.py",
        description="Zero-dependency Flesch-Kincaid Grade Level checker (G4 reading-level bar).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_grade = sub.add_parser("grade", help="report the FK grade of a text file (or - for stdin)")
    p_grade.add_argument("file", help="path to a plain-text file, or - for stdin")
    p_grade.set_defaults(func=cmd_grade)

    p_check = sub.add_parser("check", help="exit non-zero if FK grade exceeds --max")
    p_check.add_argument("file", help="path to a plain-text file, or - for stdin")
    p_check.add_argument(
        "--max", type=float, required=True, help="the FK grade ceiling for the G1 audience"
    )
    p_check.set_defaults(func=cmd_check)

    return parser


def main(argv: list | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
