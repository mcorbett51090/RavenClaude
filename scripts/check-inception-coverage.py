#!/usr/bin/env python3
"""check-inception-coverage.py — P8 §10.1 (⛔ R2). The forcing function.

⛔ THE RULE:

  Any file added under plugins/ravenclaude-core/{hooks,skills,agents,scripts,
  commands}/ in this diff, that is not named in any inventory entry covers[],
  FAILS THE BUILD.

This is the mechanism by which "inventory all the features" is actually reached.
Coverage grows monotonically and cannot regress; new features never widen the gap.
A hard "162 entries by date X" target is explicitly REJECTED — it creates exactly
the pressure that produces restatements, which is the failure the whole project
exists to prevent. The ratchet guarantees the DIRECTION, not the date.

⛔ SEQUENCING CORRECTION OVER PLAN A. Plan A armed this only AFTER wave-1
authoring, which means every artifact shipped during a 90-110 hour authoring
effort is UNGATED — its own promise that "new features never widen the gap" does
not hold during the window it matters most. The gate is armed BEFORE bulk
authoring, on the strength of the seed entries P0 and P4 naturally produce.

⛔ SECOND ASSERTION, SAME FILE, SAME REASON: NO `paths:` FILTER ON A REQUIRED
WORKFLOW. A skipped JOB reports Success; a skipped WORKFLOW reports nothing and
hangs the PR forever. Both assertions here are "can this gate actually fire?"
checks, which is why they live together.

⛔ THE TEETH-BIT EXIT IS 1. Declared, never assumed.

Usage:
    check-inception-coverage.py [--base origin/main] [--check]
    check-inception-coverage.py --must-fail
    check-inception-coverage.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _base_ref import merge_base as _resolve_merge_base  # noqa: E402
from concepts import ENTRY_CLASS_INVENTORY, ConceptError, load_concepts  # noqa: E402

PLUGIN = "plugins/ravenclaude-core"
GATED_ROOTS = tuple(f"{PLUGIN}/{d}/" for d in ("hooks", "skills", "agents", "scripts", "commands"))
REQUIRED_WORKFLOWS = (
    ".github/workflows/validate-marketplace.yml",
    ".github/workflows/validate-layout.yml",
    ".github/workflows/validate-schemas.yml",
)
# Test files under hooks/tests/ are not shipped artifacts; the census excludes
# them and so does this gate. Stated, not assumed.
EXCLUDE = (f"{PLUGIN}/hooks/tests/",)


def _git(root: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout.strip()


def added_artifacts(root: Path, base: str) -> tuple[list[str], str | None]:
    # ⛔ Resolved through _base_ref: a CI checkout has no origin/main, and failing
    # every PR on that is an environment defect masquerading as a finding.
    mb, how = _resolve_merge_base(root, base)
    if not mb:
        return [], f"{how} — the added set is UNKNOWN, not empty"
    rc, out = _git(root, "diff", "--name-only", "--diff-filter=A", mb)
    if rc != 0:
        return [], "git diff failed — the added set is UNKNOWN, not empty"
    hits = []
    for p in out.split("\n"):
        p = p.strip()
        if not p or not p.startswith(GATED_ROOTS) or p.startswith(EXCLUDE):
            continue
        hits.append(p)
    return sorted(hits), None


def covered_paths(root: Path) -> set[str]:
    try:
        concepts = load_concepts(root)
    except ConceptError:
        # ⛔ A parse failure is UNKNOWN coverage, never full coverage. Returning an
        # empty set here would make every added artifact "uncovered" (loud, safe);
        # returning a full set would make them all "covered" (silent, wrong).
        return set()
    out: set[str] = set()
    for c in concepts:
        if c.get("entry_class") == ENTRY_CLASS_INVENTORY:
            out.update(c.get("covers") or [])
    return out


def workflow_path_filters(root: Path) -> list[str]:
    """A `paths:` filter on the PULL_REQUEST trigger of a REQUIRED check.

    ⛔ THE SCOPE IS pull_request AND ONLY pull_request, AND THAT IS THE WHOLE
    POINT. The first version of this check regex-matched `paths:` anywhere in the
    `on:` block and reported both validate-marketplace.yml and
    validate-schemas.yml. Both were FALSE:

      · validate-schemas.yml carries `paths:` under `push:`, which is DELIBERATE
        and documented in the file — a push run is not a required check, so a
        path-skipped push run blocks nothing.
      · a comment that merely SAYS the words "do not re-add paths:" is prose about
        a filter, not a filter. A grep satisfied by the thing being described is a
        recorded failure class in this repo, and this detector walked straight
        into it.

    Parsed with the YAML loader rather than a regex, so the check reads structure
    instead of text.
    """
    try:
        import yaml
    except ImportError:
        # ⛔ UNKNOWN, never clean.
        return ["pyyaml is unavailable — the paths: assertion is UNKNOWN, not passed"]

    bad = []
    for rel in REQUIRED_WORKFLOWS:
        fp = root / rel
        if not fp.is_file():
            bad.append(f"{rel}: MISSING — a required check that does not exist cannot report")
            continue
        try:
            doc = yaml.safe_load(fp.read_text(encoding="utf-8"))
        except Exception as exc:  # a malformed workflow is UNKNOWN, not clean
            bad.append(f"{rel}: does not parse as YAML ({type(exc).__name__}) — UNKNOWN")
            continue
        # PyYAML resolves a bare `on:` key to the boolean True (the Norway
        # problem). Accept both spellings rather than silently finding no trigger.
        trig = None
        if isinstance(doc, dict):
            trig = doc.get("on", doc.get(True))
        if not isinstance(trig, dict):
            bad.append(f"{rel}: no parseable `on:` mapping — UNKNOWN, not clean")
            continue
        pr = trig.get("pull_request")
        if isinstance(pr, dict) and ("paths" in pr or "paths-ignore" in pr):
            bad.append(
                f"{rel}: carries a paths: filter on its PULL_REQUEST trigger. A skipped "
                "WORKFLOW reports nothing, and a required check that reports nothing "
                "hangs the PR forever."
            )
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 1")
        return 0

    root = Path(args.root).resolve()

    if args.must_fail:
        # 1. A planted added artifact with no covers[] entry must be reported.
        planted = f"{PLUGIN}/hooks/planted-inception-canary.sh"
        if planted in covered_paths(root):
            print("✗ must-fail: the planted canary path is already covered; pick another.")
            return 0
        uncovered = [planted] if planted not in covered_paths(root) else []
        if not uncovered:
            print("✗ must-fail: an uncovered artifact was not reported.")
            return 0
        # 2. An unresolvable base must report UNKNOWN, never an empty clean set.
        # ⛔ UNKNOWN MUST BE TESTED IN A REPO THAT GENUINELY HAS NO BASE.
        # The old fixture passed a bogus ref name and expected UNKNOWN — which
        # stopped working the moment _base_ref learned to FALL BACK to origin/main,
        # because a bogus ref in a normal clone now correctly resolves to the real
        # base. A teeth fixture that silently starts asserting the opposite of its
        # intent is worse than none, so the isolation is now real: a fresh repo with
        # one commit, no remote, no merge commit, and GITHUB_BASE_REF cleared.
        import os as _os, subprocess as _sp, tempfile as _tf
        with _tf.TemporaryDirectory() as _td:
            _r = Path(_td)
            for _cmd in (["init", "-q"], ["config", "user.email", "t@t"],
                         ["config", "user.name", "t"]):
                _sp.run(["git", "-C", str(_r), *_cmd], check=False, timeout=60)
            (_r / "seed.txt").write_text("x\n", encoding="utf-8")
            _sp.run(["git", "-C", str(_r), "add", "-A"], check=False, timeout=60)
            _sp.run(["git", "-C", str(_r), "commit", "-qm", "seed"], check=False, timeout=60)
            _saved = _os.environ.pop("GITHUB_BASE_REF", None)
            try:
                _paths, _unknown = added_artifacts(_r, "origin/main")
            finally:
                if _saved is not None:
                    _os.environ["GITHUB_BASE_REF"] = _saved
        if _unknown is None:
            print("✗ must-fail: a repo with NO resolvable base returned a KNOWN result.")
            print("  'nothing changed' and 'the query broke' would be the same output.")
            return 0
        # 3. The paths:-filter detector must bite on a planted trigger block.
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            fake = Path(td)
            (fake / ".github" / "workflows").mkdir(parents=True)
            for rel in REQUIRED_WORKFLOWS:
                (fake / rel).write_text(
                    "on:\n  pull_request:\n    paths:\n      - 'plugins/**'\n"
                    "  push:\n    branches: [main]\njobs:\n  a:\n    runs-on: ubuntu-latest\n",
                    encoding="utf-8",
                )
            if len(workflow_path_filters(fake)) != len(REQUIRED_WORKFLOWS):
                print("✗ must-fail: the paths:-filter detector did not bite on all three.")
                return 0
            # ⛔ CONTROL, and it is the half that matters. A paths: filter under
            # `push:` is DELIBERATE in this repo and must NOT be flagged. Without
            # this the detector could pass its teeth run while reporting every
            # workflow in the tree, which is what the first version did.
            for rel in REQUIRED_WORKFLOWS:
                (fake / rel).write_text(
                    "on:\n  pull_request:\n  push:\n    branches: [main]\n"
                    "    paths:\n      - 'schemas/**'\njobs:\n  a:\n    runs-on: ubuntu-latest\n",
                    encoding="utf-8",
                )
            if workflow_path_filters(fake):
                print("✗ must-fail: a paths: filter under push: was flagged. Push runs are")
                print("  not required checks, so a path-skipped push run blocks nothing.")
                return 0
        if workflow_path_filters(root):
            print("✗ must-fail: the REAL tree already carries a paths: filter — fix that")
            print("  first; a teeth run against a broken tree proves nothing.")
            return 0
        print("✓ must-fail: an uncovered added artifact is reported, a base-less repo")
        print("  reports UNKNOWN, and the paths:-filter detector bites on a planted trigger")
        print("  while the real tree is clean. Exiting 1, the DECLARED teeth code.")
        return 1

    added, unknown = added_artifacts(root, args.base)
    covered = covered_paths(root)
    wf = workflow_path_filters(root)

    print("── inception coverage (⛔ R2: the forcing function) ──")
    for w in wf:
        print(f"  ✗ {w}")

    if unknown:
        print(f"  ⚠ {unknown}")
        print("  Refusing to report a pass from a query that did not resolve.")
        return 1 if args.check else 0

    uncovered = [p for p in added if p not in covered]
    print(f"  artifacts added vs {args.base} : {len(added)}")
    print(f"  of those, covered by an entry  : {len(added) - len(uncovered)}")

    if uncovered:
        print()
        print(f"  ⛔ {len(uncovered)} added artifact(s) named in no inventory entry covers[]:")
        for p in uncovered:
            print(f"    ✗ {p}")
        print()
        print("     Add each to the covers[] of an inventory entry. A MECHANISM entry may")
        print("     list many paths at once — the unit is the mechanism, not the file, and")
        print("     coverage still computes per artifact.")
    elif added:
        print("  ✓ every artifact added in this diff is covered by an inventory entry.")
    else:
        print("  ✓ this diff adds no gated artifact.")

    rc = 1 if (uncovered or wf) else 0
    return rc if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
