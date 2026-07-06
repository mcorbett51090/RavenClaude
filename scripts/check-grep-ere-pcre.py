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
# `egrep` is the historical ERE alias (== `grep -E`), so an `egrep '(?:…)'` carries
# the same dead-PCRE-in-ERE bug and must be recognized (2026-07 review).
_GREP_ERE = re.compile(r"\begrep\b|grep\s+(?:-[A-Za-z]*E|--extended-regexp)")
_GREP_PCRE = re.compile(r"grep\s+(?:-[A-Za-z]*P|--perl-regexp)")
# PCRE-only constructs that are dead inside POSIX ERE.
_PCRE_CONSTRUCT = re.compile(r"\(\?[:!=<]|\[\\s\\S\]|\[\\S\\s\]")
# Split a shell line into command segments so a benign sibling `grep -P` on the
# SAME line can't exonerate a broken `grep -E` earlier on it (2026-07 review):
# the per-line `not _GREP_PCRE.search(raw)` was evaluated over the whole line.
_SEGMENT_SPLIT = re.compile(r"&&|\|\||[;|]")


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
        # the same physical line.
        for seg in _SEGMENT_SPLIT.split(raw):
            if (
                _GREP_ERE.search(seg)
                and _PCRE_CONSTRUCT.search(seg)
                and not _GREP_PCRE.search(seg)
            ):
                out.append((n, raw.rstrip()))
                break
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
