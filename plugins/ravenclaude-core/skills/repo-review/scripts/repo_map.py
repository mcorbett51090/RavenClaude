#!/usr/bin/env python3
"""Deterministic repo chunker + risk ranker for the repo-review skill (Phase 1).

Pure function of (HEAD, config) -> review-plan.json. No model calls, no network.
Same commit + same config must yield a byte-identical plan.

Status: Phase 1 of the repo-review build (see the FORGE-synthesized plan this
script came from). This is deterministic infra only -- there is no reviewer,
verifier, or fixer wired to it yet.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_PER_AGENT_TOKENS = 60_000
DEFAULT_MAX_FILE_TOKENS = 120_000
CHARS_PER_TOKEN = 4
MAX_FILES_PER_BATCH = 25
CHURN_WINDOW = "90.days"

VENDORED_GLOBS = [
    "node_modules/*",
    "*/node_modules/*",
    "vendor/*",
    "*/vendor/*",
    "dist/*",
    "*/dist/*",
    "build/*",
    "*/build/*",
    "*.min.js",
    "*.min.css",
    "*.lock",
    "*-lock.json",
    "*.generated.*",
    "*_pb2.py",
]

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".rb",
    ".php",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cs",
    ".swift",
    ".sh",
    ".bash",
    ".sql",
    ".graphql",
    ".proto",
}
ALWAYS_SOURCE_NAMES = {"Dockerfile"}

SENSITIVITY_RE = re.compile(r"(auth|crypto|payment|session|admin|migration|deploy)", re.IGNORECASE)


class GitError(RuntimeError):
    pass


def run_git(args: list[str], cwd: str) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, timeout=30
    )
    if result.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {result.stderr.decode('utf-8', 'replace')}")
    return result.stdout


def list_tracked_files(repo_root: str) -> list[str]:
    out = run_git(["ls-files", "-z"], repo_root)
    return [p for p in out.decode("utf-8", "surrogateescape").split("\0") if p]


def is_binary(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
    except OSError:
        return True
    return b"\0" in chunk


def is_vendored(rel_path: str) -> bool:
    return any(fnmatch.fnmatch(rel_path, pat) for pat in VENDORED_GLOBS)


def is_ci_yaml(rel_path: str) -> bool:
    return rel_path.startswith(".github/workflows/") and rel_path.endswith((".yml", ".yaml"))


def is_source(rel_path: str) -> bool:
    if is_ci_yaml(rel_path):
        return True
    name = Path(rel_path).name
    if name in ALWAYS_SOURCE_NAMES:
        return True
    return Path(rel_path).suffix in SOURCE_EXTENSIONS


def load_ignore_patterns(repo_root: str) -> list[str]:
    ignore_path = Path(repo_root) / ".ravenclaude" / "review-ignore"
    if not ignore_path.exists():
        return []
    patterns = []
    for line in ignore_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            patterns.append(line)
    return patterns


def est_tokens(path: Path) -> int:
    try:
        size = path.stat().st_size
    except OSError:
        return 0
    return max(1, size // CHARS_PER_TOKEN)


def churn_rank(repo_root: str, rel_path: str) -> int:
    try:
        out = run_git(
            ["log", f"--since={CHURN_WINDOW}", "--oneline", "--", rel_path], repo_root
        )
    except GitError:
        return 0
    return len(out.decode("utf-8", "surrogateescape").splitlines())


def _make_batch(batch_id: int, files: list[dict], tokens: int, module: str) -> dict:
    return {
        "id": f"b{batch_id:02d}",
        "_risk": sum(f["risk"] for f in files),
        "files": [f["path"] for f in files],
        "est_tokens": tokens,
        "modules": [module],
    }


def build_plan(
    repo_root: str,
    per_agent_tokens: int = DEFAULT_PER_AGENT_TOKENS,
    max_file_tokens: int = DEFAULT_MAX_FILE_TOKENS,
    only: list[str] | None = None,
    since: str | None = None,
    budget_batches: int = 0,
) -> dict:
    repo_root = str(Path(repo_root).resolve())
    commit = run_git(["rev-parse", "HEAD"], repo_root).decode().strip()
    tracked = list_tracked_files(repo_root)

    if since:
        try:
            changed = set(
                run_git(["diff", "--name-only", f"{since}...HEAD"], repo_root)
                .decode("utf-8", "surrogateescape")
                .splitlines()
            )
            tracked = [p for p in tracked if p in changed]
        except GitError:
            pass

    if only:
        tracked = [p for p in tracked if any(fnmatch.fnmatch(p, pat) for pat in only)]

    ignore_patterns = load_ignore_patterns(repo_root)

    excluded = {"binary": 0, "vendored": 0, "oversize": 0, "non_source": 0, "explicit": 0}
    reviewable: list[dict] = []

    for rel in sorted(tracked):
        abspath = Path(repo_root) / rel
        if not abspath.is_file():
            continue
        if any(fnmatch.fnmatch(rel, pat) for pat in ignore_patterns):
            excluded["explicit"] += 1
            continue
        if is_vendored(rel):
            excluded["vendored"] += 1
            continue
        if is_binary(abspath):
            excluded["binary"] += 1
            continue
        tokens = est_tokens(abspath)
        if tokens > max_file_tokens:
            excluded["oversize"] += 1
            continue
        if not is_source(rel):
            excluded["non_source"] += 1
            continue
        reviewable.append({"path": rel, "tokens": tokens})

    for f in reviewable:
        f["risk"] = churn_rank(repo_root, f["path"]) + (5 if SENSITIVITY_RE.search(f["path"]) else 0)

    by_dir: dict[str, list[dict]] = {}
    for f in reviewable:
        d = str(Path(f["path"]).parent)
        by_dir.setdefault(d, []).append(f)

    dir_order = sorted(by_dir.keys(), key=lambda d: (-sum(x["risk"] for x in by_dir[d]), d))

    batches = []
    batch_id = 1
    for d in dir_order:
        files = sorted(by_dir[d], key=lambda x: (-x["risk"], x["path"]))
        cur: list[dict] = []
        cur_tokens = 0
        for f in files:
            if cur and (cur_tokens + f["tokens"] > per_agent_tokens or len(cur) >= MAX_FILES_PER_BATCH):
                batches.append(_make_batch(batch_id, cur, cur_tokens, d))
                batch_id += 1
                cur, cur_tokens = [], 0
            cur.append(f)
            cur_tokens += f["tokens"]
        if cur:
            batches.append(_make_batch(batch_id, cur, cur_tokens, d))
            batch_id += 1

    batches.sort(key=lambda b: (-b["_risk"], b["id"]))
    for i, b in enumerate(batches, start=1):
        b["risk_rank"] = i
        del b["_risk"]

    total_batches_needed = len(batches)
    files_deferred = 0
    deferred_reason = None
    top_deferred_dirs: list[str] = []

    if budget_batches and budget_batches > 0 and len(batches) > budget_batches:
        kept = batches[:budget_batches]
        dropped = batches[budget_batches:]
        files_deferred = sum(len(b["files"]) for b in dropped)
        deferred_reason = f"budget-batches={budget_batches} exceeded ({total_batches_needed} needed)"
        dropped_dirs = []
        for b in dropped:
            dropped_dirs.extend(b["modules"])
        seen = set()
        for d in dropped_dirs:
            if d not in seen:
                seen.add(d)
                top_deferred_dirs.append(d)
        batches = kept

    files_covered = sum(len(b["files"]) for b in batches)

    plan = {
        "schema_version": 1,
        "commit": commit,
        "generated_by": "repo_map.py@1",
        "totals": {
            "tracked": len(tracked),
            "reviewable": len(reviewable),
            "est_source_tokens": sum(f["tokens"] for f in reviewable),
        },
        "excluded": excluded,
        "batches": batches,
        "coverage": {
            "batches_planned": total_batches_needed,
            "batches_budgeted": len(batches),
            "files_covered": files_covered,
            "files_deferred": files_deferred,
            "deferred_reason": deferred_reason,
            "top_deferred_dirs": top_deferred_dirs[:10],
        },
    }
    return plan


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out", default=None, help="write plan JSON here; default: stdout")
    parser.add_argument("--per-agent-tokens", type=int, default=DEFAULT_PER_AGENT_TOKENS)
    parser.add_argument("--max-file-tokens", type=int, default=DEFAULT_MAX_FILE_TOKENS)
    parser.add_argument("--budget-batches", type=int, default=0, help="0 = no cap")
    parser.add_argument("--only", action="append", default=None, help="pathspec glob, repeatable")
    parser.add_argument("--since", default=None, help="restrict to files changed since this ref")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    plan = build_plan(
        args.repo_root,
        per_agent_tokens=args.per_agent_tokens,
        max_file_tokens=args.max_file_tokens,
        only=args.only,
        since=args.since,
        budget_batches=args.budget_batches,
    )
    text = json.dumps(plan, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


# --------------------------------------------------------------------------- #
# Self-test — scratch-repo fixtures, no network, no formal audit-gate wiring
# yet (mirrors the forge-route.py / forge-worktree.sh precedent).
# --------------------------------------------------------------------------- #


def _sh(cwd: str, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _write(root: str, rel: str, content: str) -> None:
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _self_test() -> int:
    failures = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        status = "ok" if cond else "FAIL"
        print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        _sh(tmp, "init", "-q")
        _sh(tmp, "config", "user.email", "test@example.com")
        _sh(tmp, "config", "user.name", "Test")

        _write(tmp, "src/auth/session.py", "def login():\n    pass\n" * 5)
        _write(tmp, "src/auth/token.py", "def issue():\n    pass\n" * 5)
        _write(tmp, "src/util/helpers.py", "def add(a, b):\n    return a + b\n")
        _write(tmp, "node_modules/pkg/index.js", "module.exports = {};\n")
        _write(tmp, "dist/bundle.min.js", "!function(){}();\n")
        _write(tmp, "assets/logo.png", "\x89PNG\x00\x00binarydata")
        _write(tmp, "docs/README_ONLY.md", "# not source\n")
        _write(tmp, ".github/workflows/ci.yml", "name: ci\non: push\n")
        big = "x = 1\n" * 200_000
        _write(tmp, "src/huge.py", big)

        _sh(tmp, "add", "-A")
        _sh(tmp, "commit", "-q", "-m", "initial")

        # Give src/auth/ churn so it outranks src/util/ deterministically.
        _write(tmp, "src/auth/session.py", "def login():\n    pass\n" * 6)
        _sh(tmp, "add", "-A")
        _sh(tmp, "commit", "-q", "-m", "touch auth")

        plan1 = build_plan(tmp, per_agent_tokens=60_000, budget_batches=0)
        plan2 = build_plan(tmp, per_agent_tokens=60_000, budget_batches=0)

        check("determinism", json.dumps(plan1, sort_keys=True) == json.dumps(plan2, sort_keys=True))

        check(
            "excluded.vendored == 2 (node_modules + dist/*.min.js)",
            plan1["excluded"]["vendored"] == 2,
            str(plan1["excluded"]),
        )
        check("excluded.binary == 1", plan1["excluded"]["binary"] == 1, str(plan1["excluded"]))
        check("excluded.oversize == 1", plan1["excluded"]["oversize"] == 1, str(plan1["excluded"]))
        check(
            "excluded.non_source >= 1 (README_ONLY.md)",
            plan1["excluded"]["non_source"] >= 1,
            str(plan1["excluded"]),
        )

        all_files = [f for b in plan1["batches"] for f in b["files"]]
        check("node_modules file appears in no batch", "node_modules/pkg/index.js" not in all_files)
        check("ci yaml is reviewable (in a batch)", ".github/workflows/ci.yml" in all_files)

        auth_files = {"src/auth/session.py", "src/auth/token.py"}
        util_files = {"src/util/helpers.py"}
        auth_batch_rank = min(
            b["risk_rank"] for b in plan1["batches"] if auth_files & set(b["files"])
        )
        util_batch_rank = min(
            (b["risk_rank"] for b in plan1["batches"] if util_files & set(b["files"])),
            default=999,
        )
        check(
            "risk ordering — src/auth/ outranks src/util/",
            auth_batch_rank < util_batch_rank,
            f"auth={auth_batch_rank} util={util_batch_rank}",
        )

        plan_budget = build_plan(tmp, per_agent_tokens=60_000, budget_batches=1)
        check(
            "budget respected — exactly 1 batch emitted",
            len(plan_budget["batches"]) == 1,
            str(len(plan_budget["batches"])),
        )
        check(
            "coverage honesty — files_deferred > 0 when budget binds",
            plan_budget["coverage"]["files_deferred"] > 0,
            str(plan_budget["coverage"]),
        )
        check(
            "coverage honesty — deferred_reason + top_deferred_dirs populated",
            plan_budget["coverage"]["deferred_reason"] is not None
            and len(plan_budget["coverage"]["top_deferred_dirs"]) > 0,
        )

        plan_full = build_plan(tmp, per_agent_tokens=60_000, budget_batches=0)
        check(
            "no deferral when budget is unset",
            plan_full["coverage"]["files_deferred"] == 0
            and plan_full["coverage"]["deferred_reason"] is None,
        )

        only_plan = build_plan(tmp, only=["src/auth/*"])
        only_files = [f for b in only_plan["batches"] for f in b["files"]]
        check(
            "--only narrows the file set",
            set(only_files) == auth_files,
            str(only_files),
        )

    print(f"\n{'ALL PASS' if not failures else f'{len(failures)} FAILED'}: {len(failures)} failing")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
