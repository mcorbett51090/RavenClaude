#!/usr/bin/env python3
"""check-repo-file-budget.py — keep the repo under the Claude Code Directory's file-count limit.

The Directory stops validating a repository that holds 10,000 files or more (pre-submission checklist,
docs-verified 2026-10-13), and a stopped validation cannot be fixed from the portal. This repo was at
10,883 tracked files when that was measured; packing the 1,019 generated diagram SVGs (scripts/visual_pack.py)
brought it under. This gate keeps it there: without it the count drifts back over the limit one PR at a time
and nobody notices until a submission fails.

    python3 scripts/check-repo-file-budget.py              # fail at >= FAIL_AT tracked files, warn at >= WARN_AT
    python3 scripts/check-repo-file-budget.py --count      # print the count only
    python3 scripts/check-repo-file-budget.py --simulate-extra N   # pretend N more files exist (the gate's teeth)
    python3 scripts/check-repo-file-budget.py --self-test

Counts `git ls-files` (tracked files — what a clone, and so the portal, sees). FAIL_AT sits 10 under the real
limit and WARN_AT 40 under it, so a PR that adds a lot is told before the limit, not at it. To raise either,
edit the constant in this file and say why in the PR: a budget changed in the same diff that needs it is
the review.

Stdlib only; Python 3.9-safe.
"""

from __future__ import annotations

import argparse
import collections
import subprocess
import sys
import tempfile
from pathlib import Path

DIRECTORY_LIMIT = (
    10_000  # the Directory stops at this many files in the repo [docs-verified 2026-10-13]
)
FAIL_AT = 9_990
WARN_AT = 9_950


def tracked_files(root: Path) -> list:
    proc = subprocess.run(["git", "ls-files", "-z"], cwd=str(root), capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "git ls-files failed: " + proc.stderr.decode("utf-8", "replace").strip()[:200]
        )
    return [p for p in proc.stdout.decode("utf-8", "surrogateescape").split("\0") if p]


def verdict(count: int) -> str:
    """'fail' | 'warn' | 'ok' for a tracked-file count."""
    if count >= FAIL_AT:
        return "fail"
    if count >= WARN_AT:
        return "warn"
    return "ok"


def biggest_areas(files: list, n: int = 6) -> list:
    """Where the files are, two path segments deep, so a failure points at what to pack or prune."""
    c = collections.Counter("/".join(f.split("/")[:2]) for f in files)
    return c.most_common(n)


def run(root: Path, extra: int = 0) -> int:
    try:
        files = tracked_files(root)
    except (RuntimeError, OSError) as exc:
        print(
            f"check-repo-file-budget: cannot count tracked files ({exc}) - NOT RUN, this is not a pass"
        )
        return 2
    count = len(files) + extra
    v = verdict(count)
    note = f" (including {extra} simulated)" if extra else ""
    if v == "fail":
        print(
            f"Repo file budget FAILED: {count:,} tracked files{note} >= {FAIL_AT:,} "
            f"(the Directory stops validating at {DIRECTORY_LIMIT:,}; {DIRECTORY_LIMIT - count:,} to spare)."
        )
        print("Largest areas:")
        for area, n in biggest_areas(files):
            print(f"  {n:>6,}  {area}")
        print(
            "Fix by packing generated per-file artifacts (see scripts/visual_pack.py for the pattern), pruning dead files, "
            "or - only with a reason in the PR - raising FAIL_AT in scripts/check-repo-file-budget.py."
        )
        return 1
    if v == "warn":
        print(
            f"Repo file budget OK but close: {count:,} tracked files{note}, warn at {WARN_AT:,}, "
            f"fail at {FAIL_AT:,}, Directory limit {DIRECTORY_LIMIT:,}."
        )
        return 0
    print(
        f"Repo file budget OK: {count:,} tracked files{note} ({FAIL_AT - count:,} below the {FAIL_AT:,} budget)."
    )
    return 0


def self_test() -> int:
    failures = []

    def check(name: str, ok: bool) -> None:
        print(("  ✓ " if ok else "  ✗ ") + name)
        if not ok:
            failures.append(name)

    check(
        "limits are ordered WARN_AT < FAIL_AT < DIRECTORY_LIMIT",
        WARN_AT < FAIL_AT < DIRECTORY_LIMIT,
    )
    check("a small repo is ok", verdict(100) == "ok" and verdict(WARN_AT - 1) == "ok")
    check("at WARN_AT it warns", verdict(WARN_AT) == "warn" and verdict(FAIL_AT - 1) == "warn")
    check(
        "at FAIL_AT it fails (the boundary is inclusive)",
        verdict(FAIL_AT) == "fail" and verdict(DIRECTORY_LIMIT + 5) == "fail",
    )
    check(
        "biggest_areas ranks by two-segment prefix",
        biggest_areas(["a/b/1", "a/b/2", "a/c/3", "z"])[0] == ("a/b", 2),
    )
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        subprocess.run(["git", "init", "-q"], cwd=td, check=True)
        for i in range(3):
            (root / f"f{i}.txt").write_text("x")
        subprocess.run(["git", "add", "."], cwd=td, check=True)
        check("tracked_files counts what is in the index", len(tracked_files(root)) == 3)
        check("run() passes on a tiny repo", run(root) == 0)
        check(
            "run() fails when simulated files push it over (teeth)", run(root, extra=FAIL_AT) == 1
        )
    with tempfile.TemporaryDirectory() as td:
        check("run() reports NOT RUN (exit 2), not a pass, outside a git repo", run(Path(td)) == 2)
    print(
        "check-repo-file-budget self-test "
        + ("FAILED: " + ", ".join(failures) if failures else "OK")
    )
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument("--count", action="store_true", help="print the tracked-file count only")
    ap.add_argument(
        "--simulate-extra", type=int, default=0, help="pretend N more files exist (test hook)"
    )
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    root = Path(args.root).resolve()
    if args.count:
        print(len(tracked_files(root)))
        return 0
    return run(root, extra=args.simulate_extra)


if __name__ == "__main__":
    sys.exit(main())
