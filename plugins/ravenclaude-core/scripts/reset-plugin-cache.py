#!/usr/bin/env python3
"""reset-plugin-cache.py — Ragnarök: disaster-recovery reset of a plugin cache.

Primary command `/reset-plugin-cache` (alias `/ragnarok`). Build-plan §3.10.
Full design + the resolved blockers: docs/ragnarok-reset-plugin-cache-tee-up.md.

WHAT IT DOES (dry-run by DEFAULT — execute is opt-in):
  Dry-run:  enumerate what WOULD be touched; move nothing; exit 0.
  Execute:  snapshot → fetch-fresh → verify-with-audit-gates → ATOMIC SWAP
            (two renames, roll back on partial) → preserve MEMORY → audit-JSON.

SAFETY ENVELOPE (the reason this exists over a bare `rm -rf` + reinstall):
  * Dry-run is the default; execute requires --execute AND a --confirm token that
    must equal the plugin name. IMPORTANT — honest scope (corrected 2026-07 after
    a review flagged the prior overstatement): this `--confirm` check is a
    friction/typo guard, NOT a robust proof of human invocation. The plugin name is
    knowable, and an agent that runs the (allowed, read-only) dry-run would see any
    printed value in stdout, so no script-level `--confirm` scheme can by itself
    keep an agent out. The ACTUAL user-only enforcement is the command-review
    tribunal concern `xc.ragnarok-non-user-invocation` (pre_llm_deny + always_screen
    in knowledge/concerns-catalog.md), which hard-denies — category-independently,
    before any LLM seat — an agent that shells `--execute` directly. `--confirm`
    composes with that as belt-and-suspenders; it is not the boundary on its own.
    (The spec's $CLAUDE_INVOCATION_SOURCE does not exist in the codebase — see the
    tee-up Blocker 1; the tribunal concern is the shipped user-only enforcement.)
  * Reinstall pins to a user-named SHA (--pin); no floating-HEAD fallback.
  * The pre-reset snapshot is retained (--ttl-days, default 30) so the reset is
    reversible. Atomic two-rename swap with roll-back if the second rename fails.
  * MEMORY.md / the memory dir live OUTSIDE the plugin cache and are never
    touched — the script operates only under the resolved cache root.

TESTABILITY: --cache-root overrides ~/.claude/plugins/cache (hidden; for the
fixture tests, which build a synthetic cache in a tmp dir — never the real one).
--fresh-tree injects an already-fetched fresh tree (so tests need no network);
in production the command body fetches it (pinned to --pin) before calling.
"""

from __future__ import annotations

import argparse
import errno
import json
import os
import shutil
import sys
import time
from pathlib import Path

_ERRORS_FILE = Path(__file__).resolve().parent / "_ragnarok-named-errors.json"


def _load_errors() -> dict:
    try:
        return json.loads(_ERRORS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return {}


def fail(code: str, detail: str = "") -> int:
    """Print a named error and return a non-zero exit code."""
    msgs = _load_errors()
    msg = msgs.get(code, code)
    suffix = f" — {detail}" if detail else ""
    print(f"ERROR {code}: {msg}{suffix}", file=sys.stderr)
    return 1


def default_cache_root() -> Path:
    return Path.home() / ".claude" / "plugins" / "cache"


def _version_key(version_dir: Path) -> tuple:
    """Sort key that orders version dirs by semver, not lexically.
    Lexical max picks `0.9.0` over `0.120.0` (wrong); a numeric tuple fixes it.
    Non-numeric components sort below numeric ones; an unparseable name falls
    back to its string so the sort never raises.
    """
    parts = version_dir.name.lstrip("v").split(".")
    key = []
    for p in parts:
        key.append((1, int(p)) if p.isdigit() else (0, p))
    return (tuple(key), version_dir.name)


def resolve_plugin_version_dir(cache_root: Path, plugin: str) -> Path | None:
    """Find the single live cache dir for a plugin: <cache_root>/<marketplace>/
    <plugin>/<version>/. Returns the version dir, or None if not installed.

    Layout per the build plan: cache_root / marketplace / plugin / version.
    We search any marketplace dir for a matching plugin and take its newest
    version dir by semver order (the dry-run prints exactly which).
    """
    if not cache_root.is_dir():
        return None
    candidates: list[Path] = []
    for marketplace in sorted(p for p in cache_root.iterdir() if p.is_dir()):
        pdir = marketplace / plugin
        if pdir.is_dir():
            # Exclude our own retained backup dirs (<version>-snapshot-<ts> /
            # <version>-pre-ragnarok-<ts>): they are siblings of the live version
            # dir and would otherwise be picked as "newest". Sort the rest by
            # semver (_version_key), not lexically (0.120.0 must beat 0.9.0).
            versions = sorted(
                (
                    v
                    for v in pdir.iterdir()
                    if v.is_dir()
                    and "-snapshot-" not in v.name
                    and "-pre-ragnarok-" not in v.name
                ),
                key=_version_key,
            )
            if versions:
                candidates.append(versions[-1])
    if not candidates:
        return None
    # If a plugin somehow appears under multiple marketplaces, prefer the first.
    return candidates[0]


def _ts() -> str:
    return time.strftime("%Y%m%d-%H%M%S", time.gmtime())


def run_audit_gates(tree: Path) -> bool:
    """Run audit-gates.sh against a freshly-fetched tree. True iff it passes.

    The fresh tree is a marketplace checkout, so scripts/audit-gates.sh lives at
    its root. If the script is absent (not a marketplace tree) we treat that as a
    FAILED verification — we refuse to swap in a tree we can't validate.
    """
    import subprocess

    gate = tree / "scripts" / "audit-gates.sh"
    if not gate.is_file():
        return False
    try:
        proc = subprocess.run(
            ["bash", str(gate)], cwd=str(tree), capture_output=True, text=True, timeout=600
        )
        return proc.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def dry_run(plugin: str, version_dir: Path, pin: str | None, ttl_days: int) -> int:
    snap = version_dir.parent / f"{version_dir.name}-snapshot-{_ts()}"
    pre = version_dir.parent / f"{version_dir.name}-pre-ragnarok-{_ts()}"
    print("Ragnarök — DRY RUN (nothing will be moved). Re-run with --execute --pin <sha> to act.\n")
    print(f"  plugin:            {plugin}")
    print(f"  live cache dir:    {version_dir}")
    print(f"  would snapshot to: {snap}  (retained {ttl_days} days)")
    print(f"  would fetch fresh pinned to: {pin or '<required: --pin <sha>>'}")
    print("  would verify fresh tree with: scripts/audit-gates.sh (abort on failure)")
    print(f"  would atomic-swap: live → {pre}, fresh → {version_dir}")
    print("  MEMORY / ~/.claude/projects/.../memory: NOT touched (outside the cache)")
    print("\nNo changes made.")
    return 0


def execute(
    plugin: str,
    version_dir: Path,
    pin: str,
    ttl_days: int,
    fresh_tree: Path,
    runs_dir: Path,
) -> int:
    parent = version_dir.parent
    ts = _ts()
    snapshot = parent / f"{version_dir.name}-snapshot-{ts}"
    pre = parent / f"{version_dir.name}-pre-ragnarok-{ts}"

    # Step 3 (verify) BEFORE any mutation: a failed fresh tree must leave the
    # live cache completely untouched.
    if not run_audit_gates(fresh_tree):
        return fail("RAGNAROK_FRESH_TREE_GATES_FAILED", f"fresh tree at {fresh_tree}")

    # Step 1 — snapshot (copy, not move: the live cache stays put until the swap).
    try:
        shutil.copytree(version_dir, snapshot)
    except OSError as e:
        return fail("RAGNAROK_ATOMIC_SWAP_PARTIAL", f"snapshot copy failed: {e}")

    # Step 4 — atomic swap: two renames. Roll back the first if the second fails.
    first_done = False
    staged = None  # set only on the cross-filesystem (EXDEV) path; tracked here so
    # a mid-copy / failed-rename failure doesn't orphan a partial staging dir.
    try:
        os.rename(version_dir, pre)  # live → pre-ragnarok
        first_done = True
        try:
            os.rename(fresh_tree, version_dir)  # fresh → canonical (same-FS fast path)
        except OSError as e:
            if e.errno != errno.EXDEV:
                raise
            # fresh_tree is on a different filesystem (e.g. a /tmp clone vs the
            # ~/.claude cache): os.rename can't cross mounts. Stage a copy onto
            # version_dir's own filesystem, then rename that into place so the
            # final swap is still an atomic same-FS rename.
            staged = parent / f"{version_dir.name}-fresh-{ts}"
            shutil.rmtree(staged, ignore_errors=True)
            shutil.copytree(fresh_tree, staged)
            os.rename(staged, version_dir)
            staged = None  # consumed by the rename; nothing left to clean up
    except OSError as e:
        # A partial cross-FS staging dir (copytree/rename failed mid-flight) would
        # otherwise accumulate under the version parent across failed retries.
        if staged is not None:
            shutil.rmtree(staged, ignore_errors=True)
        rolled_back = False
        if first_done:
            # Roll back: restore the original live cache.
            try:
                os.rename(pre, version_dir)
                rolled_back = True
            except OSError:
                pass  # best-effort; the snapshot copy is the ultimate recovery
        # If the original is fully restored (rollback succeeded, or the first
        # rename never happened), the snapshot copy is redundant — remove it so a
        # failed swap doesn't orphan it. If rollback FAILED, keep the snapshot:
        # it is then the only recovery anchor.
        if rolled_back or not first_done:
            shutil.rmtree(snapshot, ignore_errors=True)
        return fail("RAGNAROK_ATOMIC_SWAP_PARTIAL", str(e))

    # Step 7 — audit JSON record (stays in the user's project; never exfiltrated).
    record = {
        "schema_version": 1,
        "ts": ts,
        "plugin": plugin,
        "pinned_sha": pin,
        "version_dir": str(version_dir),
        "pre_reset_snapshot": str(snapshot),
        "swapped_out_to": str(pre),
        "ttl_days": ttl_days,
        "preserved": ["MEMORY.md", "~/.claude/projects/*/memory/ (outside cache; untouched)"],
    }
    try:
        runs_dir.mkdir(parents=True, exist_ok=True)
        (runs_dir / f"ragnarok-{ts}.json").write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )
    except OSError:
        pass  # the swap succeeded; a failed audit-log write must not fail the run

    print("Ragnarök complete — the world is reborn from what was preserved.\n")
    print(f"  fresh cache in place at: {version_dir}")
    print(f"  pre-reset snapshot kept: {snapshot}  (for {ttl_days} days)")
    print(f"  swapped-out original:    {pre}")
    print(f"  audit record:            {runs_dir / f'ragnarok-{ts}.json'}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Ragnarök — disaster-recovery reset of a plugin cache (dry-run by default).",
    )
    p.add_argument("plugin", help="plugin name to reset (e.g. ravenclaude-core)")
    p.add_argument("--execute", action="store_true", help="actually perform the reset (default: dry-run)")
    p.add_argument("--pin", help="required with --execute: the marketplace SHA to reinstall from")
    p.add_argument("--ttl-days", type=int, default=30, help="snapshot retention (default 30)")
    p.add_argument(
        "--confirm",
        default="",
        help="user-confirmation token (the slash-command body supplies this from an "
        "interactive prompt; its absence under --execute means a non-user invocation).",
    )
    # Hidden testability knobs (not surfaced in the command help).
    p.add_argument("--cache-root", default=None, help=argparse.SUPPRESS)
    p.add_argument("--fresh-tree", default=None, help=argparse.SUPPRESS)
    p.add_argument("--runs-dir", default=None, help=argparse.SUPPRESS)
    args = p.parse_args()

    cache_root = Path(args.cache_root).resolve() if args.cache_root else default_cache_root()
    version_dir = resolve_plugin_version_dir(cache_root, args.plugin)
    if version_dir is None:
        return fail("RAGNAROK_PLUGIN_NOT_INSTALLED", f"{args.plugin} under {cache_root}")

    if not args.execute:
        return dry_run(args.plugin, version_dir, args.pin, args.ttl_days)

    # ── Execute mode — the hard gates ────────────────────────────────────────
    # Friction/typo guard (NOT the real user-only boundary — see the module
    # docstring, corrected 2026-07): --confirm must equal the plugin name. This
    # trips an accidental / half-typed execute, but the plugin name is knowable and
    # visible in the read-only dry-run's stdout, so it does not by itself keep an
    # agent out. The actual user-only enforcement is the tribunal's
    # `xc.ragnarok-non-user-invocation` pre_llm_deny concern (hard-denies an agent
    # shelling --execute directly). Fail SAFE: absence blocks execute; dry-run works.
    if args.confirm != args.plugin:
        return fail("RAGNAROK_NOT_USER_INVOKED")

    if not args.pin or not _looks_like_sha(args.pin):
        return fail("RAGNAROK_SHA_NOT_FOUND", f"--pin={args.pin!r}")

    if not args.fresh_tree:
        # In production the slash-command body fetches the pinned tree and passes
        # --fresh-tree. Without it we have nothing verified to swap in → refuse.
        return fail("RAGNAROK_SHA_NOT_FOUND", "no fetched fresh tree supplied (--fresh-tree)")
    fresh = Path(args.fresh_tree).resolve()
    if not fresh.is_dir():
        return fail("RAGNAROK_SHA_NOT_FOUND", f"fresh tree {fresh} not found")

    runs_dir = (
        Path(args.runs_dir).resolve()
        if args.runs_dir
        else Path.cwd() / ".ravenclaude" / "runs" / os.environ.get("CLAUDE_SESSION_ID", "unknown")
    )
    return execute(args.plugin, version_dir, args.pin, args.ttl_days, fresh, runs_dir)


def _looks_like_sha(s: str) -> bool:
    s = (s or "").strip()
    return 7 <= len(s) <= 40 and all(c in "0123456789abcdefABCDEF" for c in s)


if __name__ == "__main__":
    sys.exit(main())
