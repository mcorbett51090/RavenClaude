#!/usr/bin/env python3
"""Content-hash review cache for the repo-review skill (Phase 1).

Cache key: sha256(file content) + dimension + model. Stored per-file under
<cache-dir>/<relpath>.json (a list of entries). A repeat sweep whose files are
unchanged and whose (dimension, model) pairs were already run replays findings
from cache instead of re-dispatching a review agent.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

try:  # POSIX advisory file locking; absent on non-POSIX hosts.
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX
    fcntl = None  # type: ignore[assignment]


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _validate_rel_path(rel_path: str) -> None:
    """Reject an unsafe rel_path before it is used to build ANY filesystem
    path (a cache-entry path under cache_dir, or a source-file path under
    repo_root).

    rel_path comes directly from the CLI --file argument, i.e. it is
    untrusted input. Without this check, pathlib's "/" operator discards the
    left operand entirely when the right is absolute (Path("/x") / "/etc/y"
    == Path("/etc/y")), so an absolute rel_path escapes cache_dir/repo_root
    outright, and a relative "../../../etc/y" achieves the same escape via
    ".." traversal. Fails LOUDLY (raises) rather than silently sanitizing --
    this is a CLI tool, and silently rewriting a hostile path could still
    land somewhere unintended.
    """
    if not rel_path:
        raise ValueError("rel_path must not be empty")
    if os.path.isabs(rel_path):
        raise ValueError(f"rel_path must be relative, got an absolute path: {rel_path!r}")
    # Belt-and-suspenders beyond os.path.isabs: explicitly refuse a leading
    # "/" (covers the pathlib absolute-override quirk described above even
    # if os.path.isabs's platform semantics ever differ) and refuse any ".."
    # path segment (not a substring match -- "foo..bar" is a legal filename).
    if rel_path.startswith("/"):
        raise ValueError(f"rel_path must not start with '/': {rel_path!r}")
    if ".." in Path(rel_path).parts:
        raise ValueError(f"rel_path must not contain '..' path segments: {rel_path!r}")


def _require_contained(path: Path, root: Path, what: str) -> Path:
    """Defense-in-depth: resolve `path` and verify it is still contained
    within `root` after resolution.

    _validate_rel_path checks the input STRING; this checks the FINAL
    resolved path. String-level validation alone can sometimes be bypassed
    by symlinks or other on-disk tricks between validation and use, so this
    is the belt to that suspenders. Path.resolve() works even when `path`
    does not yet exist (e.g. a cache entry not yet written), so this is safe
    to call before a file is created.
    """
    resolved = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        raise ValueError(f"{what} resolves outside of {resolved_root!s}: {resolved!s}") from None
    return resolved


def _cache_path(cache_dir: str, rel_path: str) -> Path:
    # rel_path may contain "/" — mirror the tree under cache_dir.
    _validate_rel_path(rel_path)
    candidate = Path(cache_dir) / (rel_path + ".json")
    return _require_contained(candidate, Path(cache_dir), "cache path")


def _load_entries(cache_dir: str, rel_path: str) -> list[dict]:
    p = _cache_path(cache_dir, rel_path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _write_atomic(path: Path, content: str) -> None:
    """Write content to path atomically (temp file + rename-into-place).

    Mirrors fix_summary.py's _write_atomic in this same skill directory. A
    concurrent writer racing mid-write against a reader's _load_entries (or
    a process crashing mid-write) must never leave a torn/invalid JSON file
    on disk -- _load_entries silently treats an unparseable file as an empty
    list, which would otherwise discard ALL previously cached entries for
    that file. The temp file is created in the SAME directory as the
    destination so os.replace() is an atomic same-filesystem rename.
    """
    dest_dir = os.path.dirname(os.path.abspath(str(path))) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dest_dir, prefix=".review_cache_tmp_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(path))
    except BaseException:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


@contextlib.contextmanager
def _cache_lock(cache_path: Path):
    """Advisory exclusive lock serializing a single cache-entry file's
    read-modify-write cycle.

    store() reads the existing entries list, filters/rebuilds it in memory,
    then rewrites the whole file. The /repo-review pipeline this skill
    implements fans review agents out across multiple (dimension, model)
    pairs that may all be reviewing the SAME file concurrently -- without
    this lock, two concurrent writers can both read the same entries list
    and the second writer's rewrite silently clobbers (loses) the first
    writer's finding. Flocks a "<cache_path>.lock" sibling across the whole
    read-modify-write cycle, so a losing writer blocks until it can safely
    read the winner's update rather than working from stale data.

    FAIL-SAFE: if the lock can't be created/taken (fcntl unavailable on a
    non-POSIX host, a permission error, etc.) store() proceeds WITHOUT the
    lock rather than raising -- _write_atomic still prevents a torn/corrupt
    file either way; only the lost-update race is unguarded in that case.
    """
    fh = None
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = cache_path.with_name(cache_path.name + ".lock")
        fh = open(lock_path, "w")
        if fcntl is not None:
            with contextlib.suppress(OSError):
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
    except OSError:
        fh = None
    try:
        yield
    finally:
        if fh is not None:
            if fcntl is not None:
                with contextlib.suppress(OSError):
                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            with contextlib.suppress(OSError):
                fh.close()


def lookup(cache_dir: str, repo_root: str, rel_path: str, dimension: str, model: str) -> dict | None:
    _validate_rel_path(rel_path)
    abspath = _require_contained(Path(repo_root) / rel_path, Path(repo_root), "file path")
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
    _validate_rel_path(rel_path)
    abspath = _require_contained(Path(repo_root) / rel_path, Path(repo_root), "file path")
    h = file_hash(abspath)
    p = _cache_path(cache_dir, rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with _cache_lock(p):
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
        _write_atomic(p, json.dumps(entries, indent=2, sort_keys=True))


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
        try:
            result = lookup(args.cache_dir, args.repo_root, args.rel_path, args.dimension, args.model)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        print(json.dumps(result) if result is not None else "null")
        return 0

    if args.cmd == "store":
        findings = json.loads(Path(args.findings_file).read_text(encoding="utf-8"))
        try:
            store(
                args.cache_dir,
                args.repo_root,
                args.rel_path,
                args.dimension,
                args.model,
                findings,
                args.timestamp,
            )
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
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

        # --- Path-traversal / arbitrary-path rejection (security regression guard) ---
        for hostile in ("/etc/cron.d/evil", "../../../../etc/cron.d/evil", "../escape.py"):
            try:
                lookup(cache_dir, repo_root, hostile, "correctness", "sonnet")
                check(f"lookup rejects hostile rel_path {hostile!r}", False)
            except ValueError:
                check(f"lookup rejects hostile rel_path {hostile!r}", True)

            try:
                store(cache_dir, repo_root, hostile, "correctness", "sonnet", [], timestamp=4000)
                check(f"store rejects hostile rel_path {hostile!r}", False)
            except ValueError:
                check(f"store rejects hostile rel_path {hostile!r}", True)

        # Confirm the hostile absolute-path attempt did not actually escape onto disk.
        check(
            "hostile absolute rel_path did not create /etc/cron.d/evil.json",
            not Path("/etc/cron.d/evil.json").exists(),
        )

        # --- Cache file layout after all stores above (on-disk shape regression guard) ---
        check(
            "cache entries persisted as JSON at <cache_dir>/<relpath>.json",
            (Path(cache_dir) / "src" / "a.py.json").exists(),
        )

    print(f"\n{'ALL PASS' if not failures else f'{len(failures)} FAILED'}: {len(failures)} failing")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
