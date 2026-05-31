#!/usr/bin/env python3
"""check-ragnarok.py — fixture tests for reset-plugin-cache.py (Ragnarök, §3.10).

Drives the real script against a SYNTHETIC cache built in a tmp dir — never the
real ~/.claude (which doesn't exist in CI anyway; see the tee-up Blocker 3). Each
fixture is a small self-contained synthetic <cache-root>/<marketplace>/<plugin>/
<version>/ tree. Exercises the build-plan §3.10 acceptance criteria:

  1. dry-run on a non-existent plugin       → RAGNAROK_PLUGIN_NOT_INSTALLED
  2. dry-run on a real plugin               → enumerates; moves NOTHING
  3. execute with a valid SHA + fresh tree  → atomic swap; snapshot exists; audit JSON
  4. execute when fresh-tree gates FAIL     → abort; live cache untouched
  5. execute without the confirm token      → RAGNAROK_NOT_USER_INVOKED (user-only gate)
  6. MEMORY survival                        → a memory sentinel outside the cache is untouched

Run:  python3 scripts/check-ragnarok.py
Wired bidirectionally as audit-gates.sh Gate 44.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path("plugins/ravenclaude-core/scripts/reset-plugin-cache.py").resolve()

_fail = 0


def ok(cond: bool, msg: str) -> None:
    global _fail
    if cond:
        print(f"  ✓ {msg}")
    else:
        print(f"  ✗ {msg}")
        _fail += 1


def run(args: list[str]):
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args, capture_output=True, text=True, timeout=120
    )


def make_cache(root: Path, marketplace: str, plugin: str, version: str) -> Path:
    """Build a synthetic <root>/<marketplace>/<plugin>/<version>/ with a marker file."""
    vdir = root / marketplace / plugin / version
    vdir.mkdir(parents=True)
    (vdir / "plugin.json").write_text(f'{{"name":"{plugin}","version":"{version}"}}\n')
    (vdir / "MARKER").write_text("live-cache\n")
    return vdir


def make_fresh_tree(path: Path, *, gates_pass: bool) -> Path:
    """A synthetic 'freshly fetched marketplace tree' with a scripts/audit-gates.sh
    that exits 0 (pass) or 1 (fail), so we can test the verify-before-swap gate
    without running the real 332-gate suite."""
    path.mkdir(parents=True)
    (path / "scripts").mkdir()
    gate = path / "scripts" / "audit-gates.sh"
    gate.write_text("#!/usr/bin/env bash\nexit %d\n" % (0 if gates_pass else 1))
    gate.chmod(0o755)
    (path / "MARKER").write_text("fresh-tree\n")
    return path


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="ragnarok-test-"))
    try:
        # ── 1. dry-run on a non-existent plugin → NOT_INSTALLED ──────────────
        root1 = tmp / "c1"
        make_cache(root1, "ravenclaude", "ravenclaude-core", "0.1.0")
        r = run(["nonexistent-plugin", "--cache-root", str(root1)])
        ok(r.returncode != 0 and "RAGNAROK_PLUGIN_NOT_INSTALLED" in r.stderr,
           "dry-run on missing plugin → RAGNAROK_PLUGIN_NOT_INSTALLED")

        # ── 2. dry-run on a real plugin → enumerates, moves nothing ──────────
        root2 = tmp / "c2"
        v2 = make_cache(root2, "ravenclaude", "ravenclaude-core", "0.1.0")
        before = sorted(p.name for p in v2.parent.iterdir())
        r = run(["ravenclaude-core", "--cache-root", str(root2)])
        after = sorted(p.name for p in v2.parent.iterdir())
        ok(r.returncode == 0 and "DRY RUN" in r.stdout, "dry-run on real plugin → exit 0 + DRY RUN banner")
        ok(before == after and v2.is_dir() and (v2 / "MARKER").read_text() == "live-cache\n",
           "dry-run moved NOTHING (live cache intact)")

        # ── 5. execute WITHOUT confirm token → NOT_USER_INVOKED ──────────────
        #     (the user-only gate; checked before any mutation)
        root5 = tmp / "c5"
        v5 = make_cache(root5, "ravenclaude", "ravenclaude-core", "0.1.0")
        fresh5 = make_fresh_tree(tmp / "fresh5", gates_pass=True)
        r = run(["ravenclaude-core", "--execute", "--pin", "abc1234",
                 "--cache-root", str(root5), "--fresh-tree", str(fresh5),
                 "--runs-dir", str(tmp / "runs5")])
        ok(r.returncode != 0 and "RAGNAROK_NOT_USER_INVOKED" in r.stderr,
           "execute without confirm token → RAGNAROK_NOT_USER_INVOKED")
        ok(v5.is_dir() and (v5 / "MARKER").read_text() == "live-cache\n",
           "refused execute left the live cache untouched")

        # ── 4. execute when fresh-tree gates FAIL → abort, live untouched ────
        root4 = tmp / "c4"
        v4 = make_cache(root4, "ravenclaude", "ravenclaude-core", "0.1.0")
        fresh4 = make_fresh_tree(tmp / "fresh4", gates_pass=False)
        r = run(["ravenclaude-core", "--execute", "--pin", "abc1234",
                 "--confirm", "ravenclaude-core",
                 "--cache-root", str(root4), "--fresh-tree", str(fresh4),
                 "--runs-dir", str(tmp / "runs4")])
        ok(r.returncode != 0 and "RAGNAROK_FRESH_TREE_GATES_FAILED" in r.stderr,
           "execute with failing fresh-tree gates → RAGNAROK_FRESH_TREE_GATES_FAILED")
        ok(v4.is_dir() and (v4 / "MARKER").read_text() == "live-cache\n"
           and not list(v4.parent.glob("*-pre-ragnarok-*")),
           "failed-gate abort left the live cache untouched (no swap)")

        # ── 3. execute happy path → atomic swap + snapshot + audit JSON ──────
        root3 = tmp / "c3"
        v3 = make_cache(root3, "ravenclaude", "ravenclaude-core", "0.1.0")
        fresh3 = make_fresh_tree(tmp / "fresh3", gates_pass=True)
        runs3 = tmp / "runs3"
        r = run(["ravenclaude-core", "--execute", "--pin", "deadbeef",
                 "--confirm", "ravenclaude-core",
                 "--cache-root", str(root3), "--fresh-tree", str(fresh3),
                 "--runs-dir", str(runs3)])
        ok(r.returncode == 0, "execute happy path → exit 0")
        ok(v3.is_dir() and (v3 / "MARKER").read_text() == "fresh-tree\n",
           "after swap, canonical dir holds the FRESH tree")
        snaps = list(v3.parent.glob("*-snapshot-*"))
        ok(len(snaps) == 1 and (snaps[0] / "MARKER").read_text() == "live-cache\n",
           "pre-reset snapshot exists and holds the ORIGINAL cache")
        pres = list(v3.parent.glob("*-pre-ragnarok-*"))
        ok(len(pres) == 1 and (pres[0] / "MARKER").read_text() == "live-cache\n",
           "swapped-out original preserved at pre-ragnarok path")
        recs = list(runs3.glob("ragnarok-*.json")) if runs3.is_dir() else []
        rec_ok = False
        if len(recs) == 1:
            d = json.loads(recs[0].read_text())
            rec_ok = d.get("plugin") == "ravenclaude-core" and d.get("pinned_sha") == "deadbeef"
        ok(rec_ok, "audit JSON record written with plugin + pinned SHA")

        # ── 6. MEMORY survival: a sentinel OUTSIDE the cache is untouched ─────
        root6 = tmp / "c6"
        v6 = make_cache(root6, "ravenclaude", "ravenclaude-core", "0.1.0")
        memory = tmp / "home6" / ".claude" / "projects" / "proj" / "memory"
        memory.mkdir(parents=True)
        mem_file = memory / "MEMORY.md"
        mem_file.write_text("important user memory\n")
        fresh6 = make_fresh_tree(tmp / "fresh6", gates_pass=True)
        r = run(["ravenclaude-core", "--execute", "--pin", "abc1234",
                 "--confirm", "ravenclaude-core",
                 "--cache-root", str(root6), "--fresh-tree", str(fresh6),
                 "--runs-dir", str(tmp / "runs6")])
        ok(r.returncode == 0 and mem_file.read_text() == "important user memory\n",
           "MEMORY.md (outside the cache) is byte-identical after a real swap")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if _fail == 0:
        print("Ragnarök: ALL FIXTURES PASS")
        return 0
    print(f"Ragnarök: {_fail} fixture(s) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
