#!/usr/bin/env python3
"""check-diff-budget.py — the pre-commit BLAST-RADIUS guard: mass deletion.

═══════════════════════════════════════════════════════════════════════════════
EXIT CODES — A CONTRACT. Callers branch on these; do not renumber.
═══════════════════════════════════════════════════════════════════════════════

    0  within budget    MEASURED, and the change is inside the budget.
    2  OVER BUDGET      MEASURED, and the change breaches it. A real stop.
    1  could-not-run    NOT MEASURED (git absent, not a repo, HEAD unreadable).

The 1-vs-0 split is the load-bearing half. "I could not measure" is NEVER
reported as "I measured and it is clean" — a checker that cannot see must not
say clean. Incident 2 is exactly what a confident-clean report costs: a
generator printed `ok` while deleting 806 tracked files.

═══════════════════════════════════════════════════════════════════════════════
WHAT THIS GUARDS, AND WHAT IT DELIBERATELY DOES NOT
═══════════════════════════════════════════════════════════════════════════════

THE INCIDENT (docs/plans/2026-08-08-premise-gate/incidents.md, Incident 2).
Fixing four version-pin failures, an agent ran the whole `regenerate-artifacts`
battery instead of only what the change needed. `render-trees.py` printed `ok`
and DELETED 800+ tree SVGs plus 186 concept visuals — it needs a renderer that
was not present on that host. It was caught by ACCIDENT, because an unrelated
gate had passed on an earlier run and failed on a later one. Nothing in the
commit path flagged that a documentation change was about to delete 806 tracked
files.

DELETIONS ARE NOT EDITS. 806 deletions is the signal; 806 modifications is a
big refactor. This guard counts them in separate buckets and only DELETIONS
trip it. A checker that folds deletions into a generic "files touched" number
cannot see the incident it exists to catch — that is the mutant `--must-fail`
plants and proves fatal.

NOT DUPLICATED HERE — the `diff-budget` skill
(plugins/ravenclaude-core/skills/diff-budget/SKILL.md) owns the per-PR
file-count + LoC tiers (Green/Yellow/Red) and the architectural-review routing.
That skill is about a diff being too BIG to review well. This is about a diff
DESTROYING more than it says it will. Same vocabulary (budget / over budget /
blast radius), different job, and this one runs automatically.

`exempt_paths` IS DELIBERATELY NOT HONORED. The skill exempts generated and
vendored artifacts from its LoC arithmetic, which is correct for a review-load
budget. Applying it here would have exempted Incident 2 completely: the 806
files were generated SVGs. A budget whose exemption list contains the incident
is not a budget. Generated files are cheap to regenerate ONLY on a host that can
regenerate them — which is precisely the premise that was false.

═══════════════════════════════════════════════════════════════════════════════
THE TWO RULES
═══════════════════════════════════════════════════════════════════════════════

  max-deleted-files   > 50 deleted files anywhere            -> over budget
  dir-fraction        > 25% of one directory's tracked files -> over budget

The directory rule catches a total wipe that stays under the absolute count
(deleting all 30 files of a directory). Its two noise floors are why it does
not fire on ordinary work: the directory must have had at least
`--dir-min-tracked` (10) files AND at least `--dir-min-deleted` (5) of them must
be going. Without those, deleting 1 of 2 files in a folder is "50% of a
directory" and the guard becomes something people switch off.

The denominator is the tracked-file count at HEAD — the pre-change state — so
staging a deletion (which removes the path from the index) does not shrink the
denominator underneath the measurement.

Renames are NOT deletions. `git status` rename detection is honored so a
directory move is reported as `renamed`, not as a mass delete.

Usage:
    python3 scripts/check-diff-budget.py                    # human summary
    python3 scripts/check-diff-budget.py --json             # machine-readable
    python3 scripts/check-diff-budget.py --repo PATH --scope staged
    python3 scripts/check-diff-budget.py --self-test        # scratch-repo fixtures
    python3 scripts/check-diff-budget.py --must-fail        # the teeth

OVERRIDING is deliberately not a config file and not an env var: raise the bound
on the command line (`--max-deleted-files 900`). The number that allowed the
deletion then appears in the shell history / CI log beside the deletion itself.

Python 3.9 compatible. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile

EXIT_OK = 0
EXIT_COULD_NOT_RUN = 1
EXIT_OVER_BUDGET = 2

DEFAULT_MAX_DELETED_FILES = 50
DEFAULT_MAX_DIR_FRACTION = 0.25
DEFAULT_DIR_MIN_TRACKED = 10
DEFAULT_DIR_MIN_DELETED = 5

TOP_DIRS_SHOWN = 5

# Flipped ONLY by --must-fail, to plant the Incident-2 mutant (deletions counted
# as ordinary edits) and prove the real check is what catches the 806-file wipe.
_COUNT_DELETIONS = True


class CouldNotRun(Exception):
    """Raised when the diff could not be MEASURED. Never means 'clean'."""


# ---------------------------------------------------------------- git plumbing


def _git(repo, args, check=True):
    """Run git in `repo`. Returns (stdout_text, returncode).

    The missing-directory case is checked FIRST because `subprocess` raises the
    same FileNotFoundError for "the git binary is absent" and "cwd does not
    exist". Both are exit 1, but they select opposite fixes — install git vs.
    correct the path — so the cause is disambiguated rather than guessed.
    """
    if not os.path.isdir(repo):
        raise CouldNotRun(f"{repo} is not a directory — nothing to measure")
    try:
        proc = subprocess.run(["git"] + list(args), cwd=repo, capture_output=True, check=False)
    except FileNotFoundError:
        raise CouldNotRun("git was not found on PATH — the diff could not be measured")
    except OSError as exc:
        raise CouldNotRun(f"git could not be executed: {exc}")
    if check and proc.returncode != 0:
        err = proc.stderr.decode("utf-8", "replace").strip().splitlines()
        detail = err[0] if err else f"exit {proc.returncode}"
        raise CouldNotRun(f"`git {' '.join(args)}` failed: {detail}")
    return proc.stdout.decode("utf-8", "replace"), proc.returncode


def repo_root(repo):
    out, _ = _git(repo, ["rev-parse", "--show-toplevel"])
    root = out.strip()
    if not root:
        raise CouldNotRun(f"{repo} is not inside a git repository")
    return root


# ------------------------------------------------------------------- statuses


def parse_status_z(raw):
    """Parse `git status --porcelain -z` into [{x, y, path, orig}].

    Record shape is `XY<space><path>NUL`, and a rename/copy appends a second
    NUL-terminated field carrying the ORIGINAL path — which is why this is an
    index walk and not a naive split-and-map.
    """
    parts = raw.split("\0")
    entries = []
    i = 0
    n = len(parts)
    while i < n:
        rec = parts[i]
        i += 1
        if len(rec) < 4:  # also drops the trailing empty field
            continue
        x, y, path = rec[0], rec[1], rec[3:]
        orig = None
        if x in ("R", "C") or y in ("R", "C"):
            if i < n:
                orig = parts[i]
                i += 1
        entries.append({"x": x, "y": y, "path": path, "orig": orig})
    return entries


def _kind_from_code(code):
    if code == "D":
        # The one line the --must-fail mutant rewrites.
        return "deleted" if _COUNT_DELETIONS else "modified"
    if code == "A":
        return "added"
    if code in ("R", "C"):
        return "renamed"
    if code in ("M", "T"):
        return "modified"
    if code == "U":
        return "unmerged"
    if code == "?":
        return "untracked"
    return None


def resolve_scope(scope, entries):
    """`auto` measures the index when anything is staged, else the worktree."""
    if scope != "auto":
        return scope
    for e in entries:
        if e["x"] not in (" ", "?", "!"):
            return "staged"
    return "worktree"


def classify(entries, scope):
    """path -> kind. Deletion wins any tie, because deletion is the signal."""
    changes = {}
    for e in entries:
        kinds = []
        if scope in ("staged", "both") and e["x"] not in (" ", "?", "!"):
            kinds.append(_kind_from_code(e["x"]))
        if scope in ("worktree", "both") and e["y"] not in (" ", "!"):
            kinds.append(_kind_from_code(e["y"]))
        kinds = [k for k in kinds if k]
        if not kinds:
            continue
        changes[e["path"]] = "deleted" if "deleted" in kinds else kinds[0]
    return changes


# ----------------------------------------------------------------- the budget


def _dirname(path):
    return path.rsplit("/", 1)[0] if "/" in path else "."


def head_tracked_by_dir(repo):
    """Tracked-file counts per directory at HEAD, or None on an unborn branch.

    HEAD is the correct denominator: staging a deletion drops the path from the
    index, so `git ls-files` would shrink under us exactly when files vanish.
    """
    _, rc = _git(repo, ["rev-parse", "--verify", "-q", "HEAD"], check=False)
    if rc != 0:
        return None  # unborn branch — nothing is tracked, so nothing can be deleted
    listing, _ = _git(repo, ["ls-tree", "-r", "-z", "--name-only", "HEAD"])
    counts = {}
    for path in listing.split("\0"):
        if path:
            d = _dirname(path)
            counts[d] = counts.get(d, 0) + 1
    return counts


def staged_lines_removed(repo):
    """Total removed lines in the index — context for the report, never a trip.

    Returns None when it cannot be read; the summary then says so rather than
    printing a confident 0.
    """
    out, rc = _git(repo, ["diff", "--cached", "--numstat", "-z"], check=False)
    if rc != 0:
        return None
    total = 0
    for rec in out.split("\0"):
        fields = rec.split("\t")
        if len(fields) < 2:
            continue  # a bare path field from a rename record
        try:
            total += int(fields[1])
        except ValueError:
            continue  # "-" for a binary file
    return total


def evaluate(changes, tracked_by_dir, budget):
    """Returns (breaches, dir_rows). Only deletions are ever a breach."""
    deleted = [p for p, kind in changes.items() if kind == "deleted"]
    breaches = []

    if len(deleted) > budget["max_deleted_files"]:
        breaches.append(
            {
                "rule": "max-deleted-files",
                "deleted": len(deleted),
                "budget": budget["max_deleted_files"],
            }
        )

    per_dir = {}
    for path in deleted:
        d = _dirname(path)
        per_dir[d] = per_dir.get(d, 0) + 1

    dir_rows = []
    for d, n in sorted(per_dir.items(), key=lambda kv: (-kv[1], kv[0])):
        tracked = None if tracked_by_dir is None else tracked_by_dir.get(d)
        fraction = None
        if tracked:
            fraction = n / float(tracked)
            if (
                tracked >= budget["dir_min_tracked"]
                and n >= budget["dir_min_deleted"]
                and fraction > budget["max_dir_fraction"]
            ):
                breaches.append(
                    {
                        "rule": "dir-fraction",
                        "dir": d,
                        "deleted": n,
                        "tracked": tracked,
                        "fraction": round(fraction, 4),
                        "budget": budget["max_dir_fraction"],
                    }
                )
        dir_rows.append(
            {
                "dir": d,
                "deleted": n,
                "tracked": tracked,
                "fraction": None if fraction is None else round(fraction, 4),
            }
        )
    return breaches, dir_rows


def override_hint(breaches):
    """The exact flags that would clear THESE breaches — computed, not guessed.

    The two rules are independent, so naming only one of them sends the reader
    into a re-run loop: raise the file count, and the directory-fraction breach
    still stops the commit with no clue why. Both flags are derived from the
    measured values, so the hint is a single copy-pasteable command.
    """
    flags = []
    counts = [b["deleted"] for b in breaches if b["rule"] == "max-deleted-files"]
    if counts:
        flags.append(f"--max-deleted-files {max(counts)}")
    fractions = [b["fraction"] for b in breaches if b["rule"] == "dir-fraction"]
    if fractions:
        flags.append(f"--max-dir-fraction {max(fractions)}")
    return " ".join(flags)


def analyze(repo, scope, budget):
    root = repo_root(repo)
    entries = parse_status_z(_git(root, ["status", "--porcelain", "-z"])[0])
    measured = resolve_scope(scope, entries)
    changes = classify(entries, measured)
    tracked_by_dir = head_tracked_by_dir(root)
    breaches, dir_rows = evaluate(changes, tracked_by_dir, budget)

    counts = {"deleted": 0, "added": 0, "modified": 0, "renamed": 0, "unmerged": 0, "untracked": 0}
    for kind in changes.values():
        counts[kind] = counts.get(kind, 0) + 1

    return {
        "verdict": "over-budget" if breaches else "within-budget",
        "exit_code": EXIT_OVER_BUDGET if breaches else EXIT_OK,
        "repo": root,
        "scope_requested": scope,
        "scope_measured": measured,
        "baseline": "unborn" if tracked_by_dir is None else "HEAD",
        "counts": counts,
        "lines_removed": staged_lines_removed(root) if measured != "worktree" else None,
        "budget": budget,
        "breaches": breaches,
        "override_hint": override_hint(breaches),
        "top_directories": dir_rows[:TOP_DIRS_SHOWN],
    }


# ------------------------------------------------------------------ rendering


def render_human(result):
    counts = result["counts"]
    out = []
    if result["verdict"] == "over-budget":
        out.append("BLAST RADIUS — OVER BUDGET (mass deletion)")
    else:
        out.append("blast radius — within budget")
    out.append("")
    out.append(f"  deleted   {counts['deleted']:6d} files      <- the signal")
    out.append(f"  modified  {counts['modified']:6d} files")
    out.append(f"  added     {counts['added']:6d} files")
    out.append(f"  renamed   {counts['renamed']:6d} files")
    if counts.get("unmerged"):
        out.append(f"  unmerged  {counts['unmerged']:6d} files")
    lines = result["lines_removed"]
    out.append(f"  lines removed: {'unavailable' if lines is None else lines}")
    out.append(f"  measured: {result['scope_measured']} (baseline {result['baseline']})")

    if result["top_directories"] and counts["deleted"]:
        out.append("")
        out.append("  top directories by deletions:")
        for row in result["top_directories"]:
            if row["tracked"]:
                pct = f"{row['fraction'] * 100:.0f}%"
                tracked = f"of {row['tracked']} tracked ({pct})"
            else:
                tracked = "tracked count unavailable"
            out.append(f"    {row['dir']:<44} {row['deleted']:6d} deleted {tracked}")

    if result["breaches"]:
        out.append("")
        out.append("  breached:")
        for b in result["breaches"]:
            if b["rule"] == "max-deleted-files":
                out.append(
                    f"    max-deleted-files  {b['deleted']} deleted files "
                    f"(budget {b['budget']})"
                )
            else:
                out.append(
                    f"    dir-fraction       {b['dir']}: {b['deleted']}/{b['tracked']} "
                    f"= {b['fraction'] * 100:.0f}% (budget {b['budget'] * 100:.0f}%)"
                )
        out.append("")
        out.append("  Deleting tracked files is not an edit. Before you re-run:")
        out.append("    1. confirm every deletion is one you asked for — a generator that")
        out.append("       printed `ok` on a host missing its renderer is how this happens;")
        out.append("    2. if it is intended, commit the deletion on its own and raise every")
        out.append("       breached bound explicitly, so the number that allowed it sits in")
        out.append("       the log beside the deletion:")
        out.append(f"         {result['override_hint']}")
    return "\n".join(out)


# ----------------------------------------------------------------- self-tests


def _run(cmd, cwd):
    subprocess.run(
        cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
    )


def _scratch_repo(root, tree_files=100, src_files=12):
    """A committed repo: docs/trees/<n>.svg x100, src/<n>.txt x12.

    src/ is sized ABOVE `dir_min_tracked` on purpose — a 5-file src/ sits under
    the noise floor, so wiping it would (correctly) not fire the dir-fraction
    rule and the fixture would be testing nothing.
    """
    os.makedirs(os.path.join(root, "docs", "trees"))
    os.makedirs(os.path.join(root, "src"))
    for i in range(tree_files):
        with open(os.path.join(root, "docs", "trees", f"t{i:03d}.svg"), "w") as fh:
            fh.write(f"<svg id='{i}'/>\n")
    for i in range(src_files):
        with open(os.path.join(root, "src", f"s{i}.txt"), "w") as fh:
            fh.write("x\n")
    # A deliberately TINY directory, to assert the noise floor holds.
    os.makedirs(os.path.join(root, "tools"))
    for i in range(4):
        with open(os.path.join(root, "tools", f"u{i}.sh"), "w") as fh:
            fh.write("#\n")
    _run(["git", "-c", "init.defaultBranch=main", "init", "-q"], root)
    _run(["git", "add", "-A"], root)
    _run(
        [
            "git",
            "-c",
            "user.name=gate",
            "-c",
            "user.email=gate@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "--no-verify",
            "-m",
            "seed",
        ],
        root,
    )


def _delete_trees(root, n, stage=True):
    for i in range(n):
        os.remove(os.path.join(root, "docs", "trees", f"t{i:03d}.svg"))
    if stage:
        _run(["git", "add", "-A"], root)


def _restore(root):
    _run(["git", "reset", "-q", "--hard", "HEAD"], root)


def _budget(**over):
    b = {
        "max_deleted_files": DEFAULT_MAX_DELETED_FILES,
        "max_dir_fraction": DEFAULT_MAX_DIR_FRACTION,
        "dir_min_tracked": DEFAULT_DIR_MIN_TRACKED,
        "dir_min_deleted": DEFAULT_DIR_MIN_DELETED,
    }
    b.update(over)
    return b


class _Tally:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def check(self, label, cond):
        if cond:
            self.passed += 1
            print(f"  OK   {label}")
        else:
            self.failed += 1
            print(f"  FAIL {label}")


def self_test():
    """Scratch-repo fixtures. Exit 0 iff every assertion holds."""
    t = _Tally()
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "repo")
        os.makedirs(root)
        _scratch_repo(root)

        print("-- 1. THE REPLAY: a mass deletion staged behind a docs change --")
        _delete_trees(root, 60)
        with open(os.path.join(root, "src", "s0.txt"), "w") as fh:
            fh.write("touched\n")
        _run(["git", "add", "-A"], root)
        r = analyze(root, "auto", _budget())
        t.check("60 deletions -> over budget", r["verdict"] == "over-budget")
        t.check("exit code is the 2 contract", r["exit_code"] == EXIT_OVER_BUDGET)
        t.check("counts the deletions (60)", r["counts"]["deleted"] == 60)
        t.check("keeps the edit in its own bucket", r["counts"]["modified"] == 1)
        t.check(
            "names the max-deleted-files rule",
            any(b["rule"] == "max-deleted-files" for b in r["breaches"]),
        )
        t.check(
            "names the directory",
            any(row["dir"] == "docs/trees" for row in r["top_directories"]),
        )

        print("-- 2. The friction floor: one deletion is not a blast radius --")
        _restore(root)
        _delete_trees(root, 1)
        r = analyze(root, "auto", _budget())
        t.check("1 deletion -> within budget", r["verdict"] == "within-budget")
        t.check("exit code is the 0 contract", r["exit_code"] == EXIT_OK)

        print("-- 3. DELETIONS != EDITS: 60 modifications must not trip --")
        _restore(root)
        for i in range(60):
            with open(os.path.join(root, "docs", "trees", f"t{i:03d}.svg"), "w") as fh:
                fh.write("<svg id='edited'/>\n")
        _run(["git", "add", "-A"], root)
        r = analyze(root, "auto", _budget())
        t.check("60 modifications -> within budget", r["verdict"] == "within-budget")
        t.check("all 60 land in `modified`", r["counts"]["modified"] == 60)
        t.check("none land in `deleted`", r["counts"]["deleted"] == 0)

        print("-- 4. A whole directory wiped UNDER the absolute count --")
        _restore(root)
        for i in range(12):
            os.remove(os.path.join(root, "src", f"s{i}.txt"))
        _run(["git", "add", "-A"], root)
        r = analyze(root, "auto", _budget())
        t.check("12 deletions = 100% of src/ -> over budget", r["verdict"] == "over-budget")
        t.check(
            "and it is the dir-fraction rule that fires",
            any(b["rule"] == "dir-fraction" and b["dir"] == "src" for b in r["breaches"]),
        )

        print("-- 4b. The noise floor: a tiny directory wiped does NOT trip --")
        _restore(root)
        for i in range(4):
            os.remove(os.path.join(root, "tools", f"u{i}.sh"))
        _run(["git", "add", "-A"], root)
        r = analyze(root, "auto", _budget())
        t.check("100% of a 4-file dir -> within budget", r["verdict"] == "within-budget")

        print("-- 5. Renames are not deletions --")
        _restore(root)
        os.makedirs(os.path.join(root, "docs", "moved"))
        for i in range(60):
            os.rename(
                os.path.join(root, "docs", "trees", f"t{i:03d}.svg"),
                os.path.join(root, "docs", "moved", f"t{i:03d}.svg"),
            )
        _run(["git", "add", "-A"], root)
        r = analyze(root, "auto", _budget())
        t.check("a 60-file move -> within budget", r["verdict"] == "within-budget")
        t.check("reported as renamed, not deleted", r["counts"]["deleted"] == 0)

        print("-- 6. The worktree is measured when nothing is staged --")
        _restore(root)
        _delete_trees(root, 60, stage=False)
        r = analyze(root, "auto", _budget())
        t.check("unstaged mass deletion -> over budget", r["verdict"] == "over-budget")
        t.check("and it says which tree it measured", r["scope_measured"] == "worktree")

        print("-- 7. Could-not-run is never reported as clean --")
        _restore(root)
        outside = os.path.join(tmp, "not-a-repo")
        os.makedirs(outside)
        raised = False
        try:
            analyze(outside, "auto", _budget())
        except CouldNotRun:
            raised = True
        t.check("a non-repo raises CouldNotRun (-> exit 1)", raised)

        # Same exit code, opposite fix: a missing directory must not be reported
        # as an absent git binary, or the reader reinstalls git and gets nowhere.
        msg = ""
        try:
            analyze(os.path.join(tmp, "no-such-dir"), "auto", _budget())
        except CouldNotRun as exc:
            msg = str(exc)
        t.check("a missing directory names ITS OWN cause", "is not a directory" in msg)

    print()
    print(f"  {t.passed} passed, {t.failed} failed")
    return EXIT_OK if t.failed == 0 else 1


def must_fail():
    """THE TEETH. Neuter the check, then assert the known-bad case is MISSED.

    The mutant is Incident 2's own shape: deletions folded into the generic
    "files changed" bucket. If the 60-file wipe still trips with deletion
    counting removed, then something OTHER than the deletion rule is producing
    the verdict and the gate proves nothing.
    """
    global _COUNT_DELETIONS
    t = _Tally()
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "repo")
        os.makedirs(root)
        _scratch_repo(root)
        _delete_trees(root, 60)

        baseline = analyze(root, "auto", _budget())
        t.check("control: the real check CATCHES the 60-file wipe", baseline["verdict"] == "over-budget")

        _COUNT_DELETIONS = False
        try:
            mutant = analyze(root, "auto", _budget())
        finally:
            _COUNT_DELETIONS = True

        t.check(
            "mutant (deletions counted as edits) MISSES it",
            mutant["verdict"] == "within-budget",
        )
        t.check("mutant sees 0 deletions", mutant["counts"]["deleted"] == 0)
        t.check("mutant relabels all 60 as modified", mutant["counts"]["modified"] == 60)

        restored = analyze(root, "auto", _budget())
        t.check("the check is restored afterwards", restored["verdict"] == "over-budget")

    print()
    if t.failed == 0:
        print("  TEETH PROVEN — the deletion rule is what stops the known-bad case.")
        return EXIT_OK
    print(f"  TEETH ABSENT — {t.failed} assertion(s) failed.")
    return 1


# ----------------------------------------------------------------------- main


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Pre-commit blast-radius guard: trip on mass deletion.",
        epilog="Exit codes: 0 within budget, 2 over budget, 1 could-not-run.",
    )
    ap.add_argument("--repo", default=os.getcwd(), help="repository to measure (default: cwd)")
    ap.add_argument(
        "--scope",
        choices=("auto", "staged", "worktree", "both"),
        default="auto",
        help="auto (default) measures the index when anything is staged, else the worktree",
    )
    ap.add_argument("--max-deleted-files", type=int, default=DEFAULT_MAX_DELETED_FILES)
    ap.add_argument("--max-dir-fraction", type=float, default=DEFAULT_MAX_DIR_FRACTION)
    ap.add_argument("--dir-min-tracked", type=int, default=DEFAULT_DIR_MIN_TRACKED)
    ap.add_argument("--dir-min-deleted", type=int, default=DEFAULT_DIR_MIN_DELETED)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--self-test", action="store_true", help="scratch-repo fixtures")
    ap.add_argument("--must-fail", action="store_true", help="prove the check has teeth")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.must_fail:
        return must_fail()

    budget = {
        "max_deleted_files": args.max_deleted_files,
        "max_dir_fraction": args.max_dir_fraction,
        "dir_min_tracked": args.dir_min_tracked,
        "dir_min_deleted": args.dir_min_deleted,
    }

    try:
        result = analyze(args.repo, args.scope, budget)
    except CouldNotRun as exc:
        payload = {
            "verdict": "could-not-run",
            "exit_code": EXIT_COULD_NOT_RUN,
            "error": str(exc),
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"COULD NOT MEASURE the diff: {exc}", file=sys.stderr)
            print("This is NOT a clean result. Exiting 1.", file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_human(result))
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
