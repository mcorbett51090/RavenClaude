#!/usr/bin/env python3
"""fix_summary.py

Assembles the human-facing fix summary (+ diff capture) after confirmed
findings have been auto-applied to the working tree by per-file "fix
agents", each of which writes a JSON "fix receipt" describing what it did.

This script is the safety-invariant enforcer for that stage: it MUST
assert that every row it writes into the summary corresponds to exactly
one applied fix, and vice versa. A mismatch is a bug in the pipeline and
must make this script exit non-zero, never silently under- or
over-report.

Stdlib-only. See --self-test for a runnable proof of the invariant.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
import tempfile

# --------------------------------------------------------------------------
# Core data loading
# --------------------------------------------------------------------------


def load_merged(path: str) -> dict[str, dict]:
    """Load merged.json (findings_merge.py output) and index survivors by id."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    index: dict[str, dict] = {}
    for s in data.get("survivors", []):
        fid = s.get("id")
        if fid is not None:
            index[fid] = s
    return index


def load_receipts(receipts_dir: str) -> list[dict]:
    """Read every *.json file in receipts_dir, sorted for determinism."""
    paths = sorted(glob.glob(os.path.join(receipts_dir, "*.json")))
    receipts: list[dict] = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            receipts.append(json.load(f))
    return receipts


# --------------------------------------------------------------------------
# Row building
# --------------------------------------------------------------------------


def build_rows(
    merged_index: dict[str, dict], receipts: list[dict]
) -> tuple[list[dict], list[dict], int, set]:
    """Build summary table rows (one per applied finding) from receipts.

    Returns (rows, anomalies, total_skipped, files_touched).
    Deterministic ordering: receipts sorted by "file", rows sorted by
    (file, line, id).
    """
    rows: list[dict] = []
    anomalies: list[dict] = []
    total_skipped = 0
    files_touched: set = set()

    sorted_receipts = sorted(receipts, key=lambda r: str(r.get("file", "")))

    for receipt in sorted_receipts:
        file_ = receipt.get("file", "?")
        applied = receipt.get("applied", []) or []
        skipped = receipt.get("skipped", []) or []

        if applied:
            files_touched.add(file_)
        total_skipped += len(skipped)

        for entry in applied:
            fid = entry.get("id", "?")
            what_changed = entry.get("summary", "")
            match = merged_index.get(fid)
            if match is None:
                anomalies.append({"id": fid, "file": file_, "summary": what_changed})
                line: object = "?"
                dims = "?"
            else:
                line = match.get("line", "?")
                dim_list = match.get("dimensions") or []
                dims = ", ".join(dim_list) if dim_list else "?"

            rows.append(
                {
                    "id": fid,
                    "file": file_,
                    "line": line,
                    "dimensions": dims,
                    "summary": what_changed,
                    "status": "applied",
                }
            )

    rows.sort(key=lambda r: (str(r["file"]), str(r["line"]), str(r["id"])))
    return rows, anomalies, total_skipped, files_touched


# --------------------------------------------------------------------------
# Atomic write helpers
# --------------------------------------------------------------------------


def _write_atomic(path: str, content: str) -> None:
    """Write content to path atomically (temp file + rename-into-place)."""
    dest_dir = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dest_dir, prefix=".fix_summary_tmp_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


# --------------------------------------------------------------------------
# Summary writing (the load-bearing assertion lives here)
# --------------------------------------------------------------------------


def write_summary(
    path: str,
    rows: list[dict],
    anomalies: list[dict],
    total_applied: int,
    total_skipped: int,
    files_touched: set,
) -> bool:
    """Write the markdown summary. Returns False (no file touched) on a
    row-count / applied-count mismatch instead of writing a partial file.
    """
    row_count = len(rows)
    if row_count != total_applied:
        print(
            "error: mismatch between summary rows written (%d) and total "
            "applied findings across fix receipts (%d) -- refusing to "
            "write a possibly-corrupt summary" % (row_count, total_applied),
            file=sys.stderr,
        )
        return False

    lines: list[str] = []
    lines.append("| id | file:line | dimension | what changed | status |")
    lines.append("|---|---|---|---|---|")
    for r in rows:
        lines.append(
            "| {id} | {file}:{line} | {dim} | {what} | {status} |".format(
                id=r["id"],
                file=r["file"],
                line=r["line"],
                dim=r["dimensions"],
                what=r["summary"],
                status=r["status"],
            )
        )
    lines.append("")
    lines.append(
        "Applied: {a} · Skipped: {s} · Files touched: {f}".format(
            a=total_applied, s=total_skipped, f=len(files_touched)
        )
    )

    if anomalies:
        lines.append("")
        lines.append("## Anomalies")
        for a in anomalies:
            lines.append(
                "- id `{id}` (file: {file}) was applied but not found in "
                "merged.json survivors -- summary: {summary}".format(
                    id=a["id"], file=a["file"], summary=a["summary"]
                )
            )

    content = "\n".join(lines) + "\n"
    _write_atomic(path, content)
    return True


def write_patch_and_stat(patch_path: str, stat_path: str, repo_root: str | None) -> None:
    """Capture `git diff` / `git diff --stat` when repo_root is given;
    otherwise write a placeholder comment to each output file.
    """
    if repo_root:
        diff = subprocess.run(
            ["git", "-C", repo_root, "diff"],
            capture_output=True,
            text=True,
        ).stdout
        stat = subprocess.run(
            ["git", "-C", repo_root, "diff", "--stat"],
            capture_output=True,
            text=True,
        ).stdout
        _write_atomic(patch_path, diff)
        _write_atomic(stat_path, stat)
    else:
        placeholder = "# no --repo-root given; patch not captured\n"
        _write_atomic(patch_path, placeholder)
        _write_atomic(stat_path, placeholder)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble the repo-review fix summary.")
    parser.add_argument("--merged")
    parser.add_argument("--fix-receipts-dir")
    parser.add_argument("--out-summary")
    parser.add_argument("--out-patch")
    parser.add_argument("--out-stat")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    missing = [
        name
        for name, val in (
            ("--merged", args.merged),
            ("--fix-receipts-dir", args.fix_receipts_dir),
            ("--out-summary", args.out_summary),
            ("--out-patch", args.out_patch),
            ("--out-stat", args.out_stat),
        )
        if not val
    ]
    if missing:
        parser.error(
            "missing required arguments (unless --self-test): " + ", ".join(missing)
        )

    merged_index = load_merged(args.merged)
    receipts = load_receipts(args.fix_receipts_dir)
    total_applied = sum(len(r.get("applied", []) or []) for r in receipts)

    rows, anomalies, total_skipped, files_touched = build_rows(merged_index, receipts)

    ok = write_summary(
        args.out_summary, rows, anomalies, total_applied, total_skipped, files_touched
    )
    if not ok:
        return 1

    write_patch_and_stat(args.out_patch, args.out_stat, args.repo_root)
    return 0


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------


def run_self_test() -> int:
    results: list[bool] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        tag = "[ok]" if cond else "[FAIL]"
        msg = f"{tag} {name}"
        if not cond and detail:
            msg += f" -- {detail}"
        print(msg)
        results.append(bool(cond))

    # ---- Test 1: two receipts, one applied + one skipped each ----------
    try:
        with tempfile.TemporaryDirectory() as td:
            merged = {
                "survivors": [
                    {
                        "id": "f1",
                        "file": "a.py",
                        "line": 10,
                        "severity": "high",
                        "title": "t1",
                        "dimensions": ["security"],
                    },
                    {
                        "id": "f2",
                        "file": "a.py",
                        "line": 20,
                        "severity": "low",
                        "title": "t2",
                        "dimensions": ["style"],
                    },
                    {
                        "id": "f3",
                        "file": "b.py",
                        "line": 5,
                        "severity": "med",
                        "title": "t3",
                        "dimensions": ["perf"],
                    },
                    {
                        "id": "f4",
                        "file": "b.py",
                        "line": 6,
                        "severity": "med",
                        "title": "t4",
                        "dimensions": ["perf"],
                    },
                ]
            }
            merged_path = os.path.join(td, "merged.json")
            with open(merged_path, "w", encoding="utf-8") as f:
                json.dump(merged, f)

            receipts_dir = os.path.join(td, "receipts")
            os.mkdir(receipts_dir)
            r1 = {
                "file": "a.py",
                "applied": [{"id": "f1", "summary": "fixed f1"}],
                "skipped": [{"id": "f2", "reason": "not safe"}],
            }
            r2 = {
                "file": "b.py",
                "applied": [{"id": "f3", "summary": "fixed f3"}],
                "skipped": [{"id": "f4", "reason": "not safe"}],
            }
            with open(os.path.join(receipts_dir, "a.json"), "w", encoding="utf-8") as f:
                json.dump(r1, f)
            with open(os.path.join(receipts_dir, "b.json"), "w", encoding="utf-8") as f:
                json.dump(r2, f)

            merged_index = load_merged(merged_path)
            receipts = load_receipts(receipts_dir)
            total_applied = sum(len(r.get("applied", []) or []) for r in receipts)
            rows, anomalies, total_skipped, files_touched = build_rows(
                merged_index, receipts
            )
            out_summary = os.path.join(td, "summary.md")
            ok = write_summary(
                out_summary, rows, anomalies, total_applied, total_skipped, files_touched
            )
            content = open(out_summary, encoding="utf-8").read() if ok else ""
            data_rows = [
                ln
                for ln in content.splitlines()
                if ln.startswith("|") and ln not in (
                    "| id | file:line | dimension | what changed | status |",
                ) and not ln.startswith("|---")
            ]
            check(
                "test1: write_summary succeeded",
                ok is True,
                "write_summary returned False unexpectedly",
            )
            check(
                "test1: exactly 2 data rows",
                len(data_rows) == 2,
                f"got {len(data_rows)}: {data_rows}",
            )
            check(
                "test1: stats line correct",
                "Applied: 2 · Skipped: 2 · Files touched: 2" in content,
                content,
            )
    except Exception as e:  # pragma: no cover - defensive
        check("test1: no crash", False, repr(e))

    # ---- Test 2: the row-count == applied-count assertion has real teeth
    # Call the REAL write_summary() with rows/total_applied deliberately
    # mismatched (simulating a row-writing loop that dropped a row for
    # one applied finding). This proves the invariant is checked in the
    # actual production code path, not merely documented: if someone
    # deletes the check inside write_summary(), this assertion fails.
    try:
        with tempfile.TemporaryDirectory() as td:
            out_summary = os.path.join(td, "summary.md")
            rows = [
                {
                    "id": "x1",
                    "file": "f.py",
                    "line": 1,
                    "dimensions": "d",
                    "summary": "s",
                    "status": "applied",
                }
            ]
            # total_applied claims 2 applied findings, but only 1 row was
            # produced -- a real shortchanged row-writing loop.
            ok = write_summary(
                out_summary, rows, [], total_applied=2, total_skipped=0,
                files_touched={"f.py"},
            )
            check("test2: mismatch is caught (write_summary returns False)", ok is False)
            check(
                "test2: no summary file written on mismatch",
                not os.path.exists(out_summary),
                "a partial/corrupt summary file was left behind",
            )
    except Exception as e:  # pragma: no cover - defensive
        check("test2: no crash", False, repr(e))

    # ---- Test 3: applied id not present in merged.json -> anomaly -------
    try:
        with tempfile.TemporaryDirectory() as td:
            merged = {
                "survivors": [
                    {
                        "id": "f1",
                        "file": "a.py",
                        "line": 1,
                        "severity": "high",
                        "title": "t",
                        "dimensions": ["security"],
                    }
                ]
            }
            merged_path = os.path.join(td, "merged.json")
            with open(merged_path, "w", encoding="utf-8") as f:
                json.dump(merged, f)
            receipts_dir = os.path.join(td, "receipts")
            os.mkdir(receipts_dir)
            r = {
                "file": "a.py",
                "applied": [{"id": "unknown_id", "summary": "did something"}],
                "skipped": [],
            }
            with open(os.path.join(receipts_dir, "a.json"), "w", encoding="utf-8") as f:
                json.dump(r, f)

            merged_index = load_merged(merged_path)
            receipts = load_receipts(receipts_dir)
            total_applied = sum(len(x.get("applied", []) or []) for x in receipts)
            rows, anomalies, total_skipped, files_touched = build_rows(
                merged_index, receipts
            )
            out_summary = os.path.join(td, "summary.md")
            ok = write_summary(
                out_summary, rows, anomalies, total_applied, total_skipped, files_touched
            )
            content = open(out_summary, encoding="utf-8").read() if ok else ""
            check("test3: write_summary succeeded despite unknown id", ok is True)
            check(
                "test3: row written with '?' for unknown id",
                "| unknown_id | a.py:? | ? | did something | applied |" in content,
                content,
            )
            check("test3: Anomalies section present", "## Anomalies" in content, content)
            check(
                "test3: anomalies list contains unknown_id",
                any(a["id"] == "unknown_id" for a in anomalies),
            )
    except Exception as e:  # pragma: no cover - defensive
        check("test3: no crash", False, repr(e))

    # ---- Test 4: without --repo-root, placeholder patch/stat files -----
    try:
        with tempfile.TemporaryDirectory() as td:
            patch_path = os.path.join(td, "fixes.patch")
            stat_path = os.path.join(td, "fixes.stat")
            write_patch_and_stat(patch_path, stat_path, None)
            pc = open(patch_path, encoding="utf-8").read()
            sc = open(stat_path, encoding="utf-8").read()
            check(
                "test4: fixes.patch created with placeholder comment",
                "# no --repo-root given; patch not captured" in pc,
                pc,
            )
            check(
                "test4: fixes.stat created with placeholder comment",
                "# no --repo-root given; patch not captured" in sc,
                sc,
            )
    except Exception as e:  # pragma: no cover - defensive
        check("test4: no crash", False, repr(e))

    # ---- Test 5: with --repo-root pointing at a real git repo ----------
    try:
        with tempfile.TemporaryDirectory() as td:
            def run_git(*cmd: str) -> None:
                subprocess.run(
                    ["git", "-C", td] + list(cmd),
                    capture_output=True,
                    text=True,
                    check=True,
                )

            run_git("init", "-q")
            run_git("config", "user.email", "test@example.com")
            run_git("config", "user.name", "Test")
            run_git("config", "commit.gpgsign", "false")

            fpath = os.path.join(td, "file.txt")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write("hello\n")
            run_git("add", "file.txt")
            run_git("commit", "-q", "-m", "init")

            with open(fpath, "w", encoding="utf-8") as f:
                f.write("hello world\n")

            patch_path = os.path.join(td, "fixes.patch")
            stat_path = os.path.join(td, "fixes.stat")
            write_patch_and_stat(patch_path, stat_path, td)
            pc = open(patch_path, encoding="utf-8").read()
            check(
                "test5: fixes.patch non-empty and contains 'diff --git'",
                len(pc) > 0 and "diff --git" in pc,
                pc[:200],
            )
    except Exception as e:  # pragma: no cover - defensive
        check("test5: no crash", False, repr(e))

    # ---- Test 6: zero receipts -> empty-but-valid summary ---------------
    try:
        with tempfile.TemporaryDirectory() as td:
            merged = {"survivors": []}
            merged_path = os.path.join(td, "merged.json")
            with open(merged_path, "w", encoding="utf-8") as f:
                json.dump(merged, f)
            receipts_dir = os.path.join(td, "receipts")
            os.mkdir(receipts_dir)  # empty dir, zero receipt files

            merged_index = load_merged(merged_path)
            receipts = load_receipts(receipts_dir)
            total_applied = sum(len(x.get("applied", []) or []) for x in receipts)
            rows, anomalies, total_skipped, files_touched = build_rows(
                merged_index, receipts
            )
            out_summary = os.path.join(td, "summary.md")
            ok = write_summary(
                out_summary, rows, anomalies, total_applied, total_skipped, files_touched
            )
            content = open(out_summary, encoding="utf-8").read() if ok else ""
            data_rows = [
                ln
                for ln in content.splitlines()
                if ln.startswith("|") and ln not in (
                    "| id | file:line | dimension | what changed | status |",
                ) and not ln.startswith("|---")
            ]
            check("test6: write_summary succeeded on zero receipts", ok is True)
            check(
                "test6: stats line reads all zero",
                "Applied: 0 · Skipped: 0 · Files touched: 0" in content,
                content,
            )
            check("test6: no data rows in table", len(data_rows) == 0, data_rows)
    except Exception as e:  # pragma: no cover - defensive
        check("test6: no crash", False, repr(e))

    failing = sum(1 for r in results if not r)
    total = len(results)
    if failing:
        print(f"{failing} FAILED: {failing} failing")
        return 1
    print(f"ALL PASS: 0 failing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
