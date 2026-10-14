#!/usr/bin/env python3
"""check-repo-file-budget.py — keep the repo under the Claude Code Directory's size limits.

The Directory's pre-submission checklist (https://claude.com/docs/plugins/pre-submission-checklist,
re-read 2026-10-14) stops validating a repository that is not "under 50 MiB as GitHub archives it and under
256 MiB unpacked, with fewer than 10,000 files and folders", and a stopped validation cannot be fixed from
the portal. This repo held 10,883 tracked files when that was first measured; packing the 1,019 generated
diagram SVGs (scripts/visual_pack.py) brought the FILE count under. This gate keeps it there: without it
the count drifts back over the limit one PR at a time and nobody notices until a submission fails.

What a green run does and does not mean (read before trusting it):
  - The gate FAILS on tracked FILES only (>= FAIL_AT). That is the reading of the rule this repo meets.
  - The official wording is "files and folders". Counting folders too, the monorepo is well over 10,000
    (see --report), and whether the portal adds the two is UNVERIFIED - only the portal's Validate answers
    it. --report shows both readings; only the files-only one can fail the build. The submission path that
    does not depend on the answer is the directory edition in its own repo (docs/directory-edition/).
  - Archive and unpacked size are measured by --report, not gated.

    python3 scripts/check-repo-file-budget.py              # fail at >= FAIL_AT tracked files, warn at >= WARN_AT
    python3 scripts/check-repo-file-budget.py --report     # files, folders, sizes against every limit (informational)
    python3 scripts/check-repo-file-budget.py --count      # print the file count only
    python3 scripts/check-repo-file-budget.py --simulate-extra N   # pretend N more files exist (the gate's teeth)
    python3 scripts/check-repo-file-budget.py --self-test

Counts `git ls-files` (tracked files - what a clone, and so the portal, sees). FAIL_AT sits 10 under the real
limit and WARN_AT 40 under it, so a PR that adds a lot is told before the limit, not at it. To raise either,
edit the constant in this file and say why in the PR: a budget changed in the same diff that needs it is
the review.

Stdlib only; Python 3.9-safe.
"""

from __future__ import annotations

import argparse
import collections
import contextlib
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

OFFICIAL_SOURCE = "https://claude.com/docs/plugins/pre-submission-checklist"
VERIFIED_ON = "2026-10-14"
# "fewer than 10,000 files and folders" [docs-verified 2026-10-14]
DIRECTORY_LIMIT = 10_000
ARCHIVE_LIMIT_BYTES = 50 * 2**20  # "under 50 MiB as GitHub archives it"
UNPACKED_LIMIT_BYTES = 256 * 2**20  # "under 256 MiB unpacked"
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


def count_folders(files: list) -> int:
    """Distinct directories that hold at least one tracked file, counting every ancestor once."""
    dirs = set()
    for f in files:
        p = os.path.dirname(f)
        while p and p not in dirs:
            dirs.add(p)
            p = os.path.dirname(p)
    return len(dirs)


def unpacked_bytes(root: Path, files: list) -> int:
    total = 0
    for f in files:
        try:
            total += os.lstat(str(root / f)).st_size
        except OSError:
            continue
    return total


def _count_bytes(stream, chunk: int = 1 << 20) -> int:
    n = 0
    while True:
        b = stream.read(chunk)
        if not b:
            return n
        n += len(b)


def archive_bytes(root: Path, fmt: str) -> int | None:
    """Size of `git archive --format=<fmt> HEAD`, streamed (nothing is written). None if there is no HEAD."""
    try:
        proc = subprocess.Popen(
            ["git", "archive", "--format=" + fmt, "HEAD"],
            cwd=str(root),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return None
    n = _count_bytes(proc.stdout)
    return n if proc.wait() == 0 else None


def largest(root: Path, files: list, n: int = 5) -> list:
    sizes = []
    for f in files:
        try:
            sizes.append((os.lstat(str(root / f)).st_size, f))
        except OSError:
            continue
    return sorted(sizes, reverse=True)[:n]


def _mib(n: int) -> str:
    return f"{n / 2**20:,.1f} MiB"


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
            f"(the Directory's limit is fewer than {DIRECTORY_LIMIT:,} files and folders; this gate counts "
            f"files only, so {DIRECTORY_LIMIT - count:,} to spare on that reading - run --report for folders and size)."
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
            f"fail at {FAIL_AT:,}, Directory limit {DIRECTORY_LIMIT:,} (files and folders)."
        )
        return 0
    print(
        f"Repo file budget OK: {count:,} tracked files{note} ({FAIL_AT - count:,} below the {FAIL_AT:,} budget)."
    )
    return 0


def report(root: Path) -> int:
    """Informational: every measurable Directory size limit against the repo as it is now. Exit 0 unless
    the files cannot be counted at all (2 = NOT RUN)."""
    try:
        files = tracked_files(root)
    except (RuntimeError, OSError) as exc:
        print(f"check-repo-file-budget --report: cannot count tracked files ({exc}) - NOT RUN")
        return 2
    folders = count_folders(files)
    both = len(files) + folders
    unpacked = unpacked_bytes(root, files)
    zip_b = archive_bytes(root, "zip")
    tgz_b = archive_bytes(root, "tar.gz")

    def size_row(label: str, n: int | None, limit: int) -> str:
        if n is None:
            return f"  {label:<24}{'n/a':>12}   (no commit to archive yet)"
        state = "within" if n < limit else "OVER"
        return f"  {label:<24}{_mib(n):>12}   limit {_mib(limit)}   {state}"

    print(
        f"Claude Directory limits - measured now. Source: {OFFICIAL_SOURCE} (read {VERIFIED_ON})."
    )
    print(f"  {'tracked files':<24}{len(files):>12,}   Gate 302 fails at {FAIL_AT:,}")
    print(f"  {'folders':<24}{folders:>12,}")
    print(
        f'  {"files + folders":<24}{both:>12,}   official: "fewer than {DIRECTORY_LIMIT:,} files and folders"'
    )
    files_state = "within the limit" if len(files) < DIRECTORY_LIMIT else "OVER the limit"
    both_state = (
        "within the limit" if both < DIRECTORY_LIMIT else f"OVER by {both - DIRECTORY_LIMIT + 1:,}"
    )
    print(f"      files-only reading   {files_state}   (enforced by Gate 302)")
    print(
        f"      combined reading     {both_state}   (reported, NOT enforced - "
        f"UNVERIFIED which one the portal applies)"
    )
    print(size_row("unpacked", unpacked, UNPACKED_LIMIT_BYTES))
    print(size_row("GitHub archive (zip)", zip_b, ARCHIVE_LIMIT_BYTES))
    print(size_row("GitHub archive (tar.gz)", tgz_b, ARCHIVE_LIMIT_BYTES))
    print("  (archive sizes are of HEAD; commit first to include staged changes)")
    print("Largest tracked files:")
    for size, f in largest(root, files):
        print(f"  {_mib(size):>12}  {f}")
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
    check(
        "count_folders counts every ancestor once and ignores root files",
        count_folders(["a/b/1", "a/b/2", "a/c/3", "z", "x/y/w/f"]) == 6,
    )
    check("count_folders of root-only files is 0", count_folders(["a", "b"]) == 0)
    check(
        "_count_bytes streams a body larger than one chunk",
        _count_bytes(io.BytesIO(b"x" * 2500), chunk=1000) == 2500,
    )
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        subprocess.run(["git", "init", "-q"], cwd=td, check=True)
        for i in range(3):
            (root / f"f{i}.txt").write_text("x")
        (root / "d").mkdir()
        (root / "d" / "g.txt").write_text("yy")
        subprocess.run(["git", "add", "."], cwd=td, check=True)
        tracked = tracked_files(root)
        check("tracked_files counts what is in the index", len(tracked) == 4)
        check("unpacked_bytes sums the tracked files", unpacked_bytes(root, tracked) == 5)
        check("run() passes on a tiny repo", run(root) == 0)
        check(
            "run() fails when simulated files push it over (teeth)", run(root, extra=FAIL_AT) == 1
        )
        check("archive_bytes is None when there is no commit", archive_bytes(root, "zip") is None)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = report(root)
        text = out.getvalue()
        check(
            "report() exits 0 and prints both readings, with n/a for an uncommitted repo",
            rc == 0
            and "files-only reading" in text
            and "combined reading" in text
            and "n/a" in text,
        )
        check(
            "report() says the combined reading is not enforced",
            "NOT enforced" in text and "UNVERIFIED" in text,
        )
    with tempfile.TemporaryDirectory() as td:
        check("run() reports NOT RUN (exit 2), not a pass, outside a git repo", run(Path(td)) == 2)
        check("report() is NOT RUN (exit 2) outside a git repo", report(Path(td)) == 2)
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
        "--report",
        action="store_true",
        help="files, folders, unpacked and archive size against every Directory limit (informational)",
    )
    ap.add_argument(
        "--simulate-extra", type=int, default=0, help="pretend N more files exist (test hook)"
    )
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    root = Path(args.root).resolve()
    if args.report:
        return report(root)
    if args.count:
        print(len(tracked_files(root)))
        return 0
    return run(root, extra=args.simulate_extra)


if __name__ == "__main__":
    sys.exit(main())
