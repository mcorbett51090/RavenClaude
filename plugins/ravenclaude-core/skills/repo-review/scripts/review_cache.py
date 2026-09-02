#!/usr/bin/env python3
"""Content-hash review cache for the repo-review skill (Phase 1).

Cache key: sha256(file content) + dimension + model. Stored per-file under
<cache-dir>/<relpath>.json (a list of entries). A repeat sweep whose files are
unchanged and whose (dimension, model) pairs were already run replays findings
from cache instead of re-dispatching a review agent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _cache_path(cache_dir: str, rel_path: str) -> Path:
    # rel_path may contain "/" — mirror the tree under cache_dir.
    return Path(cache_dir) / (rel_path + ".json")


def _load_entries(cache_dir: str, rel_path: str) -> list[dict]:
    p = _cache_path(cache_dir, rel_path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def lookup(cache_dir: str, repo_root: str, rel_path: str, dimension: str, model: str) -> dict | None:
    abspath = Path(repo_root) / rel_path
    if not abspath.exists():
        return None
    h = file_hash(abspath)
    for entry in _load_entries(cache_dir, rel_path):
        if (
            entry.get("contentHash") == h
            and entry.get("dimension") == dimension
            and entry.get("model") == model
        ):
            return entry
    return None


def store(
    cache_dir: str,
    repo_root: str,
    rel_path: str,
    dimension: str,
    model: str,
    findings: list,
    timestamp: int,
) -> None:
    abspath = Path(repo_root) / rel_path
    h = file_hash(abspath)
    entries = _load_entries(cache_dir, rel_path)
    entries = [
        e for e in entries if not (e.get("dimension") == dimension and e.get("model") == model)
    ]
    entries.append(
        {
            "dimension": dimension,
            "model": model,
            "contentHash": h,
            "findings": findings,
            "timestamp": timestamp,
        }
    )
    p = _cache_path(cache_dir, rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(entries, indent=2, sort_keys=True), encoding="utf-8")


def batch_status(cache_dir: str, repo_root: str, files: list[str], dimensions: list[str], models: list[str]) -> dict:
    """For a batch (list of relpaths) and a set of (dimension, model) pairs,
    report which pairs are fully cache-hit (every file unchanged and present)
    vs. which need a real review dispatch."""
    hit_pairs = []
    miss_pairs = []
    for dim in dimensions:
        for model in models:
            all_hit = True
            for rel in files:
                if lookup(cache_dir, repo_root, rel, dim, model) is None:
                    all_hit = False
                    break
            (hit_pairs if all_hit else miss_pairs).append({"dimension": dim, "model": model})
    return {"hit": hit_pairs, "miss": miss_pairs}


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_lookup = sub.add_parser("lookup")
    p_lookup.add_argument("--cache-dir", required=True)
    p_lookup.add_argument("--repo-root", required=True)
    p_lookup.add_argument("--file", required=True, dest="rel_path")
    p_lookup.add_argument("--dimension", required=True)
    p_lookup.add_argument("--model", required=True)

    p_store = sub.add_parser("store")
    p_store.add_argument("--cache-dir", required=True)
    p_store.add_argument("--repo-root", required=True)
    p_store.add_argument("--file", required=True, dest="rel_path")
    p_store.add_argument("--dimension", required=True)
    p_store.add_argument("--model", required=True)
    p_store.add_argument("--findings-file", required=True, help="JSON list of findings")
    p_store.add_argument("--timestamp", type=int, required=True)

    p_status = sub.add_parser("batch-status")
    p_status.add_argument("--cache-dir", required=True)
    p_status.add_argument("--repo-root", required=True)
    p_status.add_argument("--files", required=True, help="comma-separated relpaths")
    p_status.add_argument("--dimensions", required=True, help="comma-separated")
    p_status.add_argument("--models", required=True, help="comma-separated")

    sub.add_parser("self-test")

    args = parser.parse_args(argv)

    if args.cmd == "self-test":
        return _self_test()

    if args.cmd == "lookup":
        result = lookup(args.cache_dir, args.repo_root, args.rel_path, args.dimension, args.model)
        print(json.dumps(result) if result is not None else "null")
        return 0

    if args.cmd == "store":
        findings = json.loads(Path(args.findings_file).read_text(encoding="utf-8"))
        store(
            args.cache_dir,
            args.repo_root,
            args.rel_path,
            args.dimension,
            args.model,
            findings,
            args.timestamp,
        )
        return 0

    if args.cmd == "batch-status":
        files = [f for f in args.files.split(",") if f]
        dims = [d for d in args.dimensions.split(",") if d]
        models = [m for m in args.models.split(",") if m]
        print(json.dumps(batch_status(args.cache_dir, args.repo_root, files, dims, models)))
        return 0

    return 2


def _self_test() -> int:
    failures = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        status = "ok" if cond else "FAIL"
        print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory() as repo_root, tempfile.TemporaryDirectory() as cache_dir:
        target = Path(repo_root) / "src" / "a.py"
        target.parent.mkdir(parents=True)
        target.write_text("def f():\n    return 1\n", encoding="utf-8")

        check("miss before any store", lookup(cache_dir, repo_root, "src/a.py", "correctness", "sonnet") is None)

        store(cache_dir, repo_root, "src/a.py", "correctness", "sonnet", [{"id": "f1"}], timestamp=1000)
        hit = lookup(cache_dir, repo_root, "src/a.py", "correctness", "sonnet")
        check("hit after store", hit is not None and hit["findings"] == [{"id": "f1"}])

        check(
            "miss on a different dimension",
            lookup(cache_dir, repo_root, "src/a.py", "security", "sonnet") is None,
        )
        check(
            "miss on a different model",
            lookup(cache_dir, repo_root, "src/a.py", "correctness", "opus") is None,
        )

        # Content change -> cache miss (hash changed).
        target.write_text("def f():\n    return 2\n", encoding="utf-8")
        check(
            "content change invalidates cache",
            lookup(cache_dir, repo_root, "src/a.py", "correctness", "sonnet") is None,
        )

        # Revert content -> cache hit again (content-hash based, not a write-time marker).
        target.write_text("def f():\n    return 1\n", encoding="utf-8")
        check(
            "reverted content re-hits cache",
            lookup(cache_dir, repo_root, "src/a.py", "correctness", "sonnet") is not None,
        )

        # Re-store overwrites the entry for the same (dimension, model), not append-duplicates.
        store(cache_dir, repo_root, "src/a.py", "correctness", "sonnet", [{"id": "f2"}], timestamp=2000)
        entries = _load_entries(cache_dir, "src/a.py")
        matching = [e for e in entries if e["dimension"] == "correctness" and e["model"] == "sonnet"]
        check("re-store overwrites, not duplicates", len(matching) == 1 and matching[0]["findings"] == [{"id": "f2"}])

        # batch_status: two files, one dimension/model pair fully cached, another not.
        target2 = Path(repo_root) / "src" / "b.py"
        target2.write_text("def g():\n    return 2\n", encoding="utf-8")
        store(cache_dir, repo_root, "src/b.py", "correctness", "sonnet", [], timestamp=3000)
        status = batch_status(
            cache_dir, repo_root, ["src/a.py", "src/b.py"], ["correctness", "security"], ["sonnet"]
        )
        check(
            "batch-status: correctness/sonnet is a hit (both files cached)",
            {"dimension": "correctness", "model": "sonnet"} in status["hit"],
        )
        check(
            "batch-status: security/sonnet is a miss (never cached)",
            {"dimension": "security", "model": "sonnet"} in status["miss"],
        )

    print(f"\n{'ALL PASS' if not failures else f'{len(failures)} FAILED'}: {len(failures)} failing")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
