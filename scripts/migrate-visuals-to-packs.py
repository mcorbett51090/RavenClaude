#!/usr/bin/env python3
"""migrate-visuals-to-packs.py — one-time move of the committed per-file SVGs into packs.

Reads every `knowledge/tree-visuals/<id>.svg` and `knowledge/concepts/visuals/*.svg`, writes the packs
(scripts/visual_pack.py), PROVES each packed member is byte-identical to the file it came from (sha256 of the
UTF-8 bytes), and only then removes the old files with an explicit-path `git rm` (never `git add -A`).

    python3 scripts/migrate-visuals-to-packs.py --dry-run     # write nothing, delete nothing, just prove it
    python3 scripts/migrate-visuals-to-packs.py               # write packs + manifest field, verify, git rm
    python3 scripts/migrate-visuals-to-packs.py --self-test

Safe to re-run: with no per-file SVGs left it reports "nothing to migrate" and changes nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import visual_pack as vp  # noqa: E402


class MigrationError(RuntimeError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_rm(paths: list) -> None:
    for i in range(0, len(paths), 100):
        chunk = [str(p) for p in paths[i : i + 100]]
        subprocess.run(["git", "rm", "-q", "--"] + chunk, check=True)


def migrate(root: Path, dry_run: bool = False, remover=_git_rm) -> dict:
    tdir, cdir = root / vp.TREE_DIR_REL, root / vp.CONCEPT_DIR_REL
    tree_files = sorted(tdir.glob("*.svg"))
    concept_files = sorted(cdir.glob("*.svg"))
    if not tree_files and not concept_files:
        return {"trees": 0, "concepts": 0, "removed": 0, "note": "nothing to migrate"}

    # 1. read, byte-exact
    tree_bytes, tree_svgs = {}, {}
    for p in tree_files:
        data = p.read_bytes()
        text = data.decode("utf-8")
        if text.encode("utf-8") != data:
            raise MigrationError(f"{p.name}: does not round-trip through UTF-8")
        tree_bytes[p.stem], tree_svgs[p.stem] = data, text
    concept_bytes, concept_svgs = {}, {}
    for p in concept_files:
        data = p.read_bytes()
        text = data.decode("utf-8")
        if text.encode("utf-8") != data:
            raise MigrationError(f"{p.name}: does not round-trip through UTF-8")
        concept_bytes[p.name], concept_svgs[p.name] = data, text

    # 2. the manifest is the list of trees that SHOULD be rendered: the two sets must agree exactly
    manifest = vp.read_tree_manifest(tdir)
    recorded = set(manifest.get("trees") or {})
    if recorded != set(tree_svgs):
        missing = sorted(recorded - set(tree_svgs))[:3]
        extra = sorted(set(tree_svgs) - recorded)[:3]
        raise MigrationError(
            f"manifest and tree SVG files disagree (missing files {missing}, unlisted files {extra})"
        )
    bad = [t for t in tree_svgs if "--" not in t]
    if bad:
        raise MigrationError(
            f"tree ids without a `<plugin>--` prefix cannot be grouped by owner: {bad[:3]}"
        )

    result = {"trees": len(tree_svgs), "concepts": len(concept_svgs), "removed": 0}
    if dry_run:
        # prove the round trip on an in-memory pack without touching the repo
        with tempfile.TemporaryDirectory() as td:
            vis = Path(td) / "t"
            vp.write_tree_packs(vis, tree_svgs)
            got = vp.read_tree_svgs(vis)
            _assert_identical(got, tree_bytes, "tree")
            cv = Path(td) / "c"
            vp.write_concept_pack(cv, concept_svgs)
            _assert_identical(vp.read_concept_pack(cv), concept_bytes, "concept")
        result["note"] = "dry run: round trip proven, nothing written"
        return result

    # 3. write packs + record the shard map in the manifest
    owner_shards = vp.write_tree_packs(tdir, tree_svgs, manifest.get("owner_shards"))
    manifest["owner_shards"] = {k: owner_shards[k] for k in sorted(owner_shards)}
    (tdir / vp.MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    vp.write_concept_pack(cdir, concept_svgs)

    # 4. prove it BY READING BACK FROM DISK, then (and only then) remove the old files
    _assert_identical(vp.read_tree_svgs(tdir), tree_bytes, "tree")
    _assert_identical(
        vp.load_concept_pack((cdir / vp.CONCEPT_PACK_NAME).read_text(encoding="utf-8")),
        concept_bytes,
        "concept",
    )
    problems = vp.verify_trees(tdir, manifest)
    if problems:
        raise MigrationError("packs inconsistent with the manifest:\n" + "\n".join(problems[:10]))
    remover(tree_files + concept_files)
    result["removed"] = len(tree_files) + len(concept_files)
    return result


def _assert_identical(packed: dict, original_bytes: dict, kind: str) -> None:
    """Every original is present in the pack with identical bytes; nothing extra is packed."""
    if set(packed) != set(original_bytes):
        raise MigrationError(
            f"{kind}: pack and files disagree on members "
            f"(only in pack {sorted(set(packed) - set(original_bytes))[:3]}, only in files {sorted(set(original_bytes) - set(packed))[:3]})"
        )
    for key, data in original_bytes.items():
        if _sha(packed[key].encode("utf-8")) != _sha(data):
            raise MigrationError(
                f"{kind} {key}: packed bytes differ from the file (sha256 mismatch)"
            )


def self_test() -> int:
    failures = []

    def check(name: str, ok: bool) -> None:
        print(("  ✓ " if ok else "  ✗ ") + name)
        if not ok:
            failures.append(name)

    def build(root: Path) -> None:
        t, c = root / vp.TREE_DIR_REL, root / vp.CONCEPT_DIR_REL
        t.mkdir(parents=True)
        c.mkdir(parents=True)
        trees = {f"{o}--x{i}": f"<svg>{o}{i} ✓ &amp;</svg>" for o in ("aa", "bb") for i in range(2)}
        for k, v in trees.items():
            (t / f"{k}.svg").write_bytes(v.encode("utf-8"))
        (t / vp.MANIFEST_NAME).write_text(json.dumps({"trees": dict.fromkeys(trees, "h")}))
        for n in ("one.svg", "one.mini.svg"):
            (c / n).write_bytes(f"<svg>{n}</svg>".encode())

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        build(root)
        r = migrate(root, dry_run=True)
        check(
            "dry run proves the round trip and writes nothing",
            r["trees"] == 4 and not list((root / vp.TREE_DIR_REL).glob("pack-*.js")),
        )

        removed = []
        r = migrate(root, remover=lambda ps: removed.extend(ps) or [p.unlink() for p in ps])
        check(
            "migration removes exactly the per-file SVGs it packed",
            r["removed"] == 6 and len(removed) == 6,
        )
        check(
            "no per-file SVG is left",
            not list((root / vp.TREE_DIR_REL).glob("*.svg"))
            and not list((root / vp.CONCEPT_DIR_REL).glob("*.svg")),
        )
        m = vp.read_tree_manifest(root / vp.TREE_DIR_REL)
        check(
            "the manifest records owner_shards for every owner",
            set(m["owner_shards"]) == {"aa", "bb"},
        )
        check("verify_trees is clean afterwards", vp.verify_trees(root / vp.TREE_DIR_REL) == [])
        check("re-running is a no-op", migrate(root).get("note") == "nothing to migrate")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        build(root)
        (root / vp.TREE_DIR_REL / "stray--y.svg").write_text("<svg/>")
        try:
            migrate(root, dry_run=True)
            check("a tree file the manifest does not list aborts the migration", False)
        except MigrationError:
            check("a tree file the manifest does not list aborts the migration", True)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        build(root)
        orig = vp.write_concept_pack

        def corrupting(vis, members):
            orig(vis, dict(members, **{"one.svg": members["one.svg"] + " "}))

        vp.write_concept_pack = corrupting
        try:
            kept = []
            try:
                migrate(root, remover=lambda ps: kept.extend(ps))
                check("a corrupted pack aborts BEFORE any file is removed", False)
            except MigrationError:
                check("a corrupted pack aborts BEFORE any file is removed", not kept)
        finally:
            vp.write_concept_pack = orig

    print(
        "migrate-visuals-to-packs self-test "
        + ("FAILED: " + ", ".join(failures) if failures else "OK")
    )
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--keep-originals",
        action="store_true",
        help="write + verify the packs but do not remove the per-file SVGs (removal is a separate, reviewable step)",
    )
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    try:
        r = migrate(
            Path(args.root).resolve(),
            dry_run=args.dry_run,
            remover=(lambda paths: None) if args.keep_originals else _git_rm,
        )
        if args.keep_originals:
            r["removed"] = 0
            r["note"] = "packs written and verified from disk; per-file SVGs kept"
    except MigrationError as exc:
        print(f"MIGRATION ABORTED (nothing removed): {exc}")
        return 1
    print(json.dumps(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
