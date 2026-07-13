#!/usr/bin/env python3
"""Fail on PCRE-only regex constructs used inside a POSIX-ERE `grep -E`.

Root-cause gate for the 2026-06 class of *dead* advisory-hook checks: a pattern
authored for PCRE — non-capturing `(?:...)`, look-around `(?!...)` / `(?=...)` /
`(?<...)`, or `[\\s\\S]` — placed inside `grep -E` (POSIX ERE) is silently
misparsed by GNU grep (it warns to stderr and matches nothing), so the check is
dead and a clean run *looks* like a pass. `bash -n` does not catch this. The fix
is either pure POSIX ERE or `grep -P`/`grep -Pz` (PCRE); this gate keeps the
whole hook corpus on one of those two rails.

Scans `<root>/plugins/*/hooks/*.sh`. Comment lines (`#`...) are ignored. A line
that uses a `grep -P` flag is fine (PCRE is intended there). Exit 0 = clean,
1 = at least one offending line (printed as file:line).
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys

# grep invoked with an ERE flag (E in the short-flag cluster, or the long option
# --extended-regexp) but NOT a PCRE flag. The long-option spellings were added
# after the 2026-07 review — the short-cluster-only forms missed
# `grep --extended-regexp` / `grep --perl-regexp` entirely.
#
# `_FLAGS` allows any run of intervening short-flag tokens between `grep` and the
# regex-dialect flag, so the common separated-flag idiom `grep -v -E '(?:...)'`
# (or `grep -i -E`, `grep -rn -E`, …) is matched — not just the bundled
# `grep -vE` form. Without it, any flag before -E anchored the dialect flag away
# from `grep` and the whole check silently missed the line (2026-07 review).
# `egrep` is the historical ERE alias (== `grep -E`), so an `egrep '(?:…)'`
# carries the same dead-PCRE-in-ERE bug and is recognized too (2026-07 review).
_FLAGS = r"(?:\s+-[A-Za-z]+)*"
_GREP_ERE = re.compile(rf"\begrep\b|grep{_FLAGS}\s+(?:-[A-Za-z]*E|--extended-regexp)")
_GREP_PCRE = re.compile(rf"grep{_FLAGS}\s+(?:-[A-Za-z]*P|--perl-regexp)")
# PCRE-only constructs that are dead inside POSIX ERE. The `(?...)` family is matched
# by its whole extension charset — non-capturing `(?:`, look-around `(?!`/`(?=`/`(?<`,
# named capture `(?P<`, atomic `(?>`, comment `(?#`, and inline flags `(?i)`/`(?m)` —
# not just the `[:!=<]` members (2026-07-13 review: `(?P<`, `(?>`, `(?#`, `(?i)` were
# missed, so a `grep -E '(?P<v>…)'` misparsed by GNU grep slipped the gate). Any `(?X`
# is invalid POSIX ERE, so widening the class introduces no false positives.
_PCRE_CONSTRUCT = re.compile(r"\(\?[A-Za-z:!=<>#]|\[\\s\\S\]|\[\\S\\s\]")
# Split a shell line into command segments so a benign sibling `grep -P` on the
# SAME line can't exonerate a broken `grep -E` earlier on it (2026-07 review):
# the per-line `not _GREP_PCRE.search(raw)` was evaluated over the whole line.
# The split must be QUOTE-AWARE (2026-07 review, Finding 5): a bare `re.split` on
# `;`/`|`/`&&` also severs a literal `|` living INSIDE a quoted ERE pattern, so a
# PCRE construct after a `|` alternation (`grep -E 'x|(?:y)'`) landed in a second
# segment and neither half satisfied the test — the offending line was missed.


def _split_segments(line: str) -> list[str]:
    """Split a shell line into command segments on ``;`` / ``|`` / ``&&`` / ``||`` —
    but ONLY when the delimiter is OUTSIDE single- or double-quotes, so a ``|`` inside
    a quoted ERE pattern (e.g. ``grep -E 'x|(?:y)'``) stays in one segment instead of
    severing the ``grep ... -E`` tokens from the trailing PCRE construct."""
    segs: list[str] = []
    buf: list[str] = []
    quote = ""  # "'" or '"' while inside a quoted string, else ""
    i, n = 0, len(line)
    while i < n:
        ch = line[i]
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = ""
            i += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            buf.append(ch)
            i += 1
            continue
        # Outside quotes: honor the segment delimiters.
        if ch == "&" and i + 1 < n and line[i + 1] == "&":
            segs.append("".join(buf))
            buf = []
            i += 2
            continue
        if ch == "|" and i + 1 < n and line[i + 1] == "|":
            segs.append("".join(buf))
            buf = []
            i += 2
            continue
        if ch in (";", "|"):
            segs.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    segs.append("".join(buf))
    return segs


def offending_lines(path: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError:
        return out
    for n, raw in enumerate(lines, 1):
        if raw.lstrip().startswith("#"):
            continue
        # Evaluate each command segment independently: an ERE grep carrying a dead
        # PCRE construct is offending even if a separate `grep -P` appears later on
        # the same physical line. The split is quote-aware, so an in-pattern `|`
        # (an ERE alternation) does not split the offending grep away from its
        # construct.
        flagged = False
        for seg in _split_segments(raw):
            if _GREP_ERE.search(seg) and _PCRE_CONSTRUCT.search(seg) and not _GREP_PCRE.search(seg):
                out.append((n, raw.rstrip()))
                flagged = True
                break
        if flagged:
            continue
        # Whole-line backstop (Finding 5): even if segmentation mis-split the line,
        # a line carrying an ERE grep AND a PCRE construct with NO `grep -P` anywhere
        # to own it is offending. A same-line `grep -P` (its presence detected here)
        # is what exonerates — so this fires only when nothing on the line legitimately
        # uses PCRE.
        if _GREP_ERE.search(raw) and _PCRE_CONSTRUCT.search(raw) and not _GREP_PCRE.search(raw):
            out.append((n, raw.rstrip()))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repo root to scan (default: cwd).")
    args = parser.parse_args(argv)

    pattern = os.path.join(args.root, "plugins", "*", "hooks", "*.sh")
    violations: list[str] = []
    for path in sorted(glob.glob(pattern)):
        for lineno, text in offending_lines(path):
            rel = os.path.relpath(path, args.root)
            violations.append(f"  {rel}:{lineno}: {text.strip()}")

    if violations:
        print(
            "PCRE constructs found inside `grep -E` (dead in POSIX ERE — "
            "use pure ERE or `grep -P`/`grep -Pz`):",
            file=sys.stderr,
        )
        for v in violations:
            print(v, file=sys.stderr)
        return 1

    print("grep-ERE/PCRE check passed: no PCRE-only constructs inside any `grep -E`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
