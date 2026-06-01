#!/usr/bin/env python3
"""check-layout.py — validate file paths against .repo-layout.json allowed_globs.

Single source of truth for the layout allow-list match logic, shared by:
  - .github/workflows/validate-layout.yml (CI), and
  - scripts/audit-gates.sh (the meta-test fixture that proves this gate bites).

Two modes:
  --diff <base>   check only files Added/Copied/Renamed vs <base> (the PR check)
  --all           check EVERY tracked file (git ls-files) against the allow-list
                  (catches pre-existing / modified off-allow-list files the
                  diff-only check can never see — two-panel audit 2026-05-31, P1)

A path must (a) not match any forbidden glob and (b) match at least one allowed
glob. fnmatch with the same `**`/`*` semantics the hook uses. Exit 0 if every
checked path is allowed; exit 1 with a per-path report otherwise.

Usage:
    check-layout.py --all
    check-layout.py --diff origin/main
    check-layout.py --root <dir> --all        # test-fixture override
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from fnmatch import fnmatchcase
from pathlib import Path


def _matches(path: str, glob: str) -> bool:
    """Match `path` against a layout glob. `**` spans directory separators;
    a trailing `/**` also matches the directory itself's children. fnmatchcase
    with `*`/`**` collapsed is what the CI bash matcher (`[[ $path == $glob ]]`
    with globstar) and the hook approximate; we normalize `**` to `*` for
    fnmatch (which treats `*` as spanning `/` — acceptable for an allow-list)."""
    # fnmatch's * already spans '/', so `plugins/*/agents/**` and `docs/**`
    # behave like the globstar bash match for allow-list purposes.
    return fnmatchcase(path, glob)


def check_paths(paths: list[str], allowed: list[str], forbidden: list[str],
                suggestions: dict) -> list[str]:
    failures: list[str] = []
    for path in paths:
        path = path.strip()
        if not path:
            continue
        # forbidden first
        hit = next((g for g in forbidden if _matches(path, g)), None)
        if hit:
            sug = suggestions.get(hit, "")
            failures.append(f"{path}: matches FORBIDDEN glob '{hit}'.{(' ' + sug) if sug else ''}")
            continue
        if not any(_matches(path, g) for g in allowed):
            failures.append(
                f"{path}: matches no allowed_globs entry — add a glob to "
                f".repo-layout.json if this is a legitimate location."
            )
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="repo root (default: cwd)")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--all", action="store_true", help="scan every tracked file")
    mode.add_argument("--diff", metavar="BASE", help="scan files added/copied/renamed vs BASE")
    args = ap.parse_args()
    root = Path(args.root)

    layout = json.loads((root / ".repo-layout.json").read_text(encoding="utf-8"))
    allowed = layout.get("allowed_globs", [])
    forbidden = layout.get("forbidden_globs", [])
    suggestions = layout.get("suggestions", {})

    if args.all:
        out = subprocess.run(["git", "-C", str(root), "ls-files"],
                             capture_output=True, text=True)
        paths = out.stdout.splitlines()
        scope = f"all {len(paths)} tracked files"
    else:
        out = subprocess.run(
            ["git", "-C", str(root), "diff", "--name-only", "--diff-filter=ACR",
             f"{args.diff}...HEAD"],
            capture_output=True, text=True)
        paths = out.stdout.splitlines()
        scope = f"{len(paths)} added/copied/renamed file(s) vs {args.diff}"

    failures = check_paths(paths, allowed, forbidden, suggestions)
    if failures:
        print(f"Layout check FAILED ({scope}):")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print(f"Layout OK — {scope}; every path matches the allow-list.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
