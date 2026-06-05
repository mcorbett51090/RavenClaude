#!/usr/bin/env python3
"""docs_check.py — stdlib-only readability + prose-hygiene checker for docs.

Decision-support, NOT a style authority: it computes the public-domain
Flesch Reading Ease / Flesch-Kincaid Grade Level scores and flags a small set
of mechanically-detectable docs anti-patterns (non-descriptive link text,
placeholder text, weasel words, banned/inconsistent terminology). It is a
*calculator + linter*, not a data source — every threshold is a documented,
overridable default, and the readability formulas are heuristics (syllable
counting is estimated), so treat the output as a prompt to look, not a verdict.

This complements — does not replace — a real prose linter (Vale) wired via the
plugin's `.lsp.json`. Vale owns the editor/CI style gate; this is a zero-install,
stdlib-only triage you can run on any Markdown file or pasted text immediately.

Modes:
  readability  Flesch Reading Ease + Flesch-Kincaid Grade for a file or --text
  prose        flag non-descriptive links, placeholders, weasel words, banned terms
  all          run both (default)

Usage:
  python3 docs_check.py readability path/to/doc.md
  python3 docs_check.py prose path/to/doc.md
  python3 docs_check.py all --text "Your prose here."
  python3 docs_check.py all path/to/doc.md --target-grade 10 --json

Formulas (public domain; Flesch 1948 / Kincaid et al. 1975):
  Reading Ease = 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
  Grade Level  = 0.39*(words/sentences) + 11.8*(syllables/words) - 15.59

Reading-ease bands (Flesch): 90-100 very easy ... 30-50 difficult, 0-30 very
confusing. Technical docs commonly target grade 9-12 [verify-at-use against the
audience]. These bands are guidance, not a pass/fail gate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# Markdown elements stripped before prose analysis so code/markup don't skew
# syllable and sentence counts.
_FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE = re.compile(r"`[^`]*`")
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_HTML_TAG = re.compile(r"<[^>]+>")
_HEADING_HASHES = re.compile(r"(?m)^#{1,6}\s+")
_TABLE_ROW = re.compile(r"(?m)^\s*\|.*\|\s*$")
_SENTENCE_SPLIT = re.compile(r"[.!?]+(?:\s|$)")
_WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")
_VOWEL_GROUP = re.compile(r"[aeiouy]+")

# Prose anti-patterns. Each entry: (compiled regex, label). Case-insensitive.
_NON_DESCRIPTIVE_LINK = re.compile(r"\[\s*(click here|read more|here|this link|link)\s*\]", re.I)
_PLACEHOLDER = re.compile(r"\b(TODO|TBD|FIXME|XXX|coming soon|lorem ipsum|WIP)\b", re.I)
_WEASEL = re.compile(
    r"\b(simply|just|easy|easily|obviously|of course|clearly|"
    r"basically|actually|note that|please note)\b",
    re.I,
)
# Banned / inconsistent terminology -> the canonical preferred form. A docs set
# that mixes these reads as inconsistent; pick one and enforce it. Defaults are
# common docs conventions and are meant to be edited per house style.
_BANNED_TERMS: dict[str, str] = {
    "login": 'use "log in" (verb) / "login" only as a noun',
    "e-mail": 'use "email"',
    "web site": 'use "website"',
    "filename": 'house-style check: "file name" vs "filename"',
    "drop down": 'use "drop-down" or "dropdown" consistently',
    "kindly": 'drop "kindly" — it is filler',
    "whitelist": 'prefer "allowlist"',
    "blacklist": 'prefer "denylist"',
}


def _strip_markdown(text: str) -> str:
    """Remove code, markup, and link/image URLs; keep link/heading *text*."""
    text = _FENCED_CODE.sub(" ", text)
    text = _MD_IMAGE.sub(" ", text)
    text = _MD_LINK.sub(r"\1", text)  # keep the visible link text
    text = _INLINE_CODE.sub(" ", text)
    text = _HTML_TAG.sub(" ", text)
    text = _TABLE_ROW.sub(" ", text)
    text = _HEADING_HASHES.sub("", text)
    return text


def count_syllables(word: str) -> int:
    """Estimate syllables in an English word (heuristic, vowel-group based).

    Not exact — silent-e and dipthong handling is approximate. Good enough for
    a corpus-level readability estimate, never authoritative per-word.
    """
    w = word.lower().strip("'-")
    if not w:
        return 0
    groups = _VOWEL_GROUP.findall(w)
    count = len(groups)
    # Silent trailing 'e' (but not 'le' after a consonant, e.g. "table").
    if w.endswith("e") and not w.endswith("le") and count > 1:
        count -= 1
    return max(1, count)


def analyze_readability(text: str) -> dict:
    """Compute Flesch Reading Ease + Flesch-Kincaid Grade for prose text."""
    prose = _strip_markdown(text)
    words = _WORD.findall(prose)
    sentences = [s for s in _SENTENCE_SPLIT.split(prose) if s.strip()]
    n_words = len(words)
    n_sentences = max(1, len(sentences))
    n_syllables = sum(count_syllables(w) for w in words)

    if n_words == 0:
        return {
            "words": 0,
            "sentences": 0,
            "syllables": 0,
            "reading_ease": None,
            "grade_level": None,
            "band": "no prose found",
        }

    wps = n_words / n_sentences
    spw = n_syllables / n_words
    reading_ease = 206.835 - 1.015 * wps - 84.6 * spw
    grade_level = 0.39 * wps + 11.8 * spw - 15.59

    return {
        "words": n_words,
        "sentences": n_sentences,
        "syllables": n_syllables,
        "words_per_sentence": round(wps, 2),
        "syllables_per_word": round(spw, 2),
        "reading_ease": round(reading_ease, 1),
        "grade_level": round(grade_level, 1),
        "band": _ease_band(reading_ease),
    }


def _ease_band(score: float) -> str:
    bands = [
        (90, "very easy"),
        (80, "easy"),
        (70, "fairly easy"),
        (60, "standard / plain English"),
        (50, "fairly difficult"),
        (30, "difficult"),
        (0, "very confusing"),
    ]
    for floor, label in bands:
        if score >= floor:
            return label
    return "very confusing"


def analyze_prose(text: str) -> list[dict]:
    """Flag mechanically-detectable docs anti-patterns with line numbers."""
    findings: list[dict] = []
    lines = text.splitlines()
    in_code = False
    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for m in _NON_DESCRIPTIVE_LINK.finditer(line):
            findings.append(_finding(i, "non-descriptive-link", m.group(0),
                                     "Use descriptive link text (the destination), not 'click here'/'here'."))
        for m in _PLACEHOLDER.finditer(line):
            findings.append(_finding(i, "placeholder", m.group(0),
                                     "Ship complete content or omit the section — placeholders erode trust."))
        for m in _WEASEL.finditer(line):
            findings.append(_finding(i, "weasel-word", m.group(0),
                                     "Weasel/filler word — 'simply/just/easy' assumes the reader's experience; cut it."))
        low = line.lower()
        for term, fix in _BANNED_TERMS.items():
            for m in re.finditer(r"\b" + re.escape(term) + r"\b", low):
                findings.append(_finding(i, "terminology", line[m.start():m.end()], fix))
    return findings


def _finding(line: int, kind: str, match: str, hint: str) -> dict:
    return {"line": line, "kind": kind, "match": match, "hint": hint}


def _read_input(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.path is None:
        sys.exit("error: provide a file PATH or --text")
    try:
        with open(args.path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        sys.exit(f"error: cannot read {args.path}: {exc}")


def _print_readability(r: dict, target_grade: float) -> None:
    print("── readability (Flesch) ─────────────────────────────")
    if r["reading_ease"] is None:
        print("  no prose found (file may be all code/markup).")
        return
    print(f"  words {r['words']}  sentences {r['sentences']}  "
          f"syllables {r['syllables']}")
    print(f"  words/sentence {r['words_per_sentence']}  "
          f"syllables/word {r['syllables_per_word']}")
    print(f"  Reading Ease  {r['reading_ease']}  ({r['band']})")
    print(f"  Grade Level   {r['grade_level']}  (target <= {target_grade} "
          "[verify-at-use against your audience])")
    if r["grade_level"] > target_grade:
        print("  ! above target grade — consider shorter sentences / simpler words.")


def _print_prose(findings: list[dict]) -> None:
    print("── prose hygiene ────────────────────────────────────")
    if not findings:
        print("  no anti-patterns flagged.")
        return
    for f in findings:
        print(f"  L{f['line']}: [{f['kind']}] '{f['match']}' — {f['hint']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Stdlib-only docs readability + prose-hygiene checker "
                    "(decision-support, not a style authority).")
    parser.add_argument("mode", choices=["readability", "prose", "all"],
                        nargs="?", default="all")
    parser.add_argument("path", nargs="?", help="Markdown/text file to check")
    parser.add_argument("--text", help="Inline text instead of a file")
    parser.add_argument("--target-grade", type=float, default=12.0,
                        help="Flesch-Kincaid grade target (default 12).")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args(argv)

    text = _read_input(args)
    out: dict = {}
    findings: list[dict] = []
    if args.mode in ("readability", "all"):
        out["readability"] = analyze_readability(text)
    if args.mode in ("prose", "all"):
        findings = analyze_prose(text)
        out["prose_findings"] = findings

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        if "readability" in out:
            _print_readability(out["readability"], args.target_grade)
        if "prose_findings" in out:
            _print_prose(findings)

    # Exit non-zero only if prose findings exist (CI-friendly); readability is
    # advisory and never fails the build on its own.
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
