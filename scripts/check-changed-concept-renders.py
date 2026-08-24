#!/usr/bin/env python3
"""check-changed-concept-renders.py — P6 §8.2 (⛔ R2 corollary).

⛔ THE MOST DANGEROUS LINE IN EITHER PANEL PLAN, AND WHAT REPLACES IT.

Plan A skeleton prefilled a mermaid diagram per draft entry. Three measured facts
make that an all-or-nothing revert dressed as a feature:

  1. `regenerate-artifacts.yml` reverts a FAILED render with a `::warning::` and
     continues GREEN.
  2. `render-concepts.py --check` is deliberately OFF the PR path — rendering
     needs mermaid-cli plus Chromium fetched on demand, which no PR should pay.
  3. 162 diagrams is 162 `npx` processes.

Together: a render breaks, the output is reverted, CI stays green, and the SVGs
go permanently stale while every gate reports success. That is the silent-green
shape at the largest scale in this plan.

THREE RULES REPLACE IT, and this file is the third:

  · diagrams are OPT-IN per inventory entry (enforced in concepts.py — an entry
    with `entry_class: inventory` may omit the mermaid block entirely)
  · rendering happens in batches of <= BATCH_MAX
  · `render-concepts.py --check` becomes a PR gate FOR CHANGED CONCEPTS ONLY

Scoping to changed concepts is what makes it affordable on a PR: the check reads
a source-hash manifest and needs no browser, and restricting it to the diff means
a repo-wide staleness inherited from main cannot red-fail an unrelated PR. ⛔ That
is a deliberate, stated limit, not an oversight — a whole-corpus render check
belongs on the scheduled sweep, where it blocks nothing and can take its time.

⛔ THE TEETH-BIT EXIT IS 3, AND THE NUMBER IS LOAD-BEARING.
0 is ordinary success, 1 is an uncaught Python exception, and 2 is an argparse
error — every one of them reachable WITHOUT the canary biting. Measured
2026-08-20: an adversarial mutation that introduced an IndentationError exited 1,
which was the declared teeth code at the time, so a CRASHED teeth run was
indistinguishable from a PASSING one. That is the silent-green shape, inside the
mechanism built to detect it. 3 is returned only where this file returns it.

Usage:
    check-changed-concept-renders.py [--base origin/main] [--check]
    check-changed-concept-renders.py --must-fail
    check-changed-concept-renders.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _base_ref import merge_base as _resolve_merge_base  # noqa: E402

CONCEPT_DIR = "plugins/ravenclaude-core/knowledge/concepts"
BATCH_MAX = 20


def _git(root: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout.strip()


def changed_concepts(root: Path, base: str) -> tuple[list[str], str | None]:
    """Concept files changed vs the merge base. Returns (paths, unknown_reason)."""
    # ⛔ UNKNOWN IS NOT EMPTY. No base means this check cannot scope itself, and
    # reporting "0 changed concepts, all clean" would manufacture a pass out of a
    # broken query. But a CI checkout legitimately has no origin/main, so the base
    # is resolved through _base_ref before UNKNOWN is concluded.
    mb, how = _resolve_merge_base(root, base)
    if not mb:
        return [], f"{how} — the changed set is UNKNOWN, not empty"
    rc, out = _git(root, "diff", "--name-only", mb, "--", f"{CONCEPT_DIR}/*.md")
    if rc != 0:
        return [], "git diff failed — the changed set is UNKNOWN, not empty"
    return [p for p in out.split("\n") if p.strip()], None


def batch_cap_verdict(paths: list, check: bool):
    """The FULL batch-cap decision: returns an exit code, or None to continue.

    ⛔ main() HAS NO BRANCH OF ITS OWN. That is deliberate. An earlier fix moved
    only the comparison into a shared helper, and the auditor mutation that
    started this — deleting the enforcement branch out of main() — STILL passed,
    because main() calling the helper was not itself certified.
    A teeth run can only certify code it executes, so the whole decision lives
    here and main() does nothing but return what this says.
    """
    if not over_batch_cap(paths):
        return None
    print(f"  ✗ {len(paths)} changed concepts exceeds the batch cap of {BATCH_MAX}.")
    print("     Split the batch. 162 diagrams is 162 npx+Chromium processes with an")
    print("     all-or-nothing revert that continues GREEN on failure.")
    return 1 if check else 0


def over_batch_cap(paths: list) -> bool:
    """⛔ THE SINGLE ENFORCEMENT POINT FOR THE BATCH CAP.

    This exists because its absence was a real, demonstrated defect. The
    `--must-fail` teeth used to assert `len(over) <= BATCH_MAX` against a list it
    had just built — arithmetic on a fixture, never the enforcement path. An
    adversarial audit deleted the real cap check from main() entirely and
    `--must-fail` STILL printed success and returned the declared teeth exit.

    That is the exact defect class this whole initiative exists to catch — a
    check that cannot fail — shipped inside one of its own gates.

    Both main() and --must-fail now route through here, so removing or inverting
    the comparison breaks the teeth run too. A teeth test that does not share a
    code path with the thing it certifies is testing its own fixture.
    """
    return len(paths) > BATCH_MAX


def run_check(root: Path, base: str, check: bool) -> int:
    """⛔ EVERYTHING main() DOES AFTER PARSING ARGS, so the teeth can execute it.

    An adversarial audit deleted the batch-cap call out of main() and the teeth
    still passed — they exercised the decision function but never the code that
    CALLS it. A teeth run can only certify code it executes, so main() now holds
    nothing but arg-parsing and a call to this, and the teeth call this too.
    """
    paths, unknown = changed_concepts(root, base)
    print("── changed-concept render gate (⛔ R2 corollary) ──")
    if unknown:
        print(f"  ⚠ {unknown}")
        print("  Refusing to report a pass from a query that did not resolve.")
        return 1 if check else 0

    print(f"  concepts changed vs {base}: {len(paths)}")
    for p in paths:
        print(f"    · {p}")

    cap_rc = batch_cap_verdict(paths, check=check)
    if cap_rc is not None:
        return cap_rc

    if not paths:
        print("  ✓ no concept changed in this diff — nothing to render-check.")
        print("  ⛔ Stated limit: a whole-corpus render check is NOT run here. It")
        print("     belongs on the scheduled sweep, where it blocks no PR.")
        return 0

    r = subprocess.run(
        [sys.executable, "scripts/render-concepts.py", "--check"],
        cwd=str(root), capture_output=True, text=True, timeout=300,
    )
    if r.returncode != 0:
        print("  ✗ render-concepts.py --check FAILED for this diff:")
        for ln in (r.stdout + r.stderr).strip().split("\n")[:15]:
            print(f"      {ln}")
        print("     ⛔ This FAILS the PR. It must never be downgraded to a ::warning::")
        print("        — a warned render leaves the SVGs stale while CI reads green.")
        return 1 if check else 0

    print("  ✓ every changed concept SVG matches its source hash.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 3")
        return 0

    root = Path(args.root).resolve()

    if args.must_fail:
        # TEETH, on the two things that can silently disarm this gate.
        # 1. A batch over the cap must be REPORTED, not quietly rendered.
        # ⛔ EXERCISE THE REAL ENFORCEMENT FUNCTION, IN BOTH DIRECTIONS. The
        # previous version compared len(over) against BATCH_MAX directly, which is
        # arithmetic on a locally-built list and false by construction — it passed
        # with the cap check deleted from main(). Both calls below go through
        # over_batch_cap(), the same function main() branches on.
        # ⛔ PIN THE CAP. The fixtures below are DERIVED from BATCH_MAX, so raising
        # BATCH_MAX to 100000 moves the fixtures with it and the teeth still pass —
        # "expected and actual from the same source", which an adversarial audit
        # demonstrated. The pin is the independent half: the cap is a reviewed
        # decision, and changing it must be a visible edit here, not a silent one.
        if BATCH_MAX != 20:
            print(f"✗ must-fail: BATCH_MAX is {BATCH_MAX}, not the reviewed 20.")
            print("  The cap is a decision, not a tunable. If 20 is genuinely wrong,")
            print("  change BOTH the constant and this pin, in one reviewable diff.")
            return 0
        over = [f"{CONCEPT_DIR}/x{i}.md" for i in range(BATCH_MAX + 1)]
        under = [f"{CONCEPT_DIR}/x{i}.md" for i in range(BATCH_MAX)]

        # ⛔ DRIVE THE REAL run_check() WITH A STUBBED CHANGED-SET. This is what
        # catches a deletion of the cap CALL, as opposed to the cap logic — the one
        # mutation the earlier fixes still let through.
        global changed_concepts
        _real = changed_concepts
        try:
            changed_concepts = lambda _r, _b: (over, None)  # noqa: E731
            if run_check(root, "origin/main", check=True) != 1:
                print(f"✗ must-fail: run_check() did not FAIL a {len(over)}-concept batch.")
                print("  The cap is not wired into the path main() actually takes.")
                return 0
        finally:
            changed_concepts = _real

        if batch_cap_verdict(over, check=True) != 1:
            print(f"✗ must-fail: a {len(over)}-concept batch was NOT reported over the")
            print(f"  cap of {BATCH_MAX}. The enforcement path is gone or inverted.")
            return 0
        if batch_cap_verdict(under, check=True) is not None:
            print(f"✗ must-fail: a {len(under)}-concept batch was reported OVER the cap.")
            print("  A cap that rejects a legal batch blocks every author — the")
            print("  false-positive half matters as much as the false-negative one.")
            return 0
        # 2. An unknown changed-set must NOT be reported as clean.
        # ⛔ UNKNOWN MUST BE TESTED IN A REPO THAT GENUINELY HAS NO BASE.
        # The old fixture passed a bogus ref name and expected UNKNOWN — which
        # stopped working the moment _base_ref learned to FALL BACK to origin/main,
        # because a bogus ref in a normal clone now correctly resolves to the real
        # base. A teeth fixture that silently starts asserting the opposite of its
        # intent is worse than none, so the isolation is now real: a fresh repo with
        # one commit, no remote, no merge commit, and GITHUB_BASE_REF cleared.
        with tempfile.TemporaryDirectory() as _td:
            _r = Path(_td)
            for _cmd in (["init", "-q"], ["config", "user.email", "t@t"],
                         ["config", "user.name", "t"]):
                subprocess.run(["git", "-C", str(_r), *_cmd], check=False, timeout=60)
            (_r / "seed.txt").write_text("x\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(_r), "add", "-A"], check=False, timeout=60)
            subprocess.run(["git", "-C", str(_r), "commit", "-qm", "seed"], check=False, timeout=60)
            _saved = os.environ.pop("GITHUB_BASE_REF", None)
            try:
                _paths, _unknown = changed_concepts(_r, "origin/main")
            finally:
                if _saved is not None:
                    os.environ["GITHUB_BASE_REF"] = _saved
        if _unknown is None:
            print("✗ must-fail: a repo with NO resolvable base returned a KNOWN result.")
            print("  'nothing changed' and 'the query broke' would be the same output.")
            return 0
        print("✓ must-fail: a repo with no resolvable base reports UNKNOWN (never clean), and")
        print(f"  a {len(over)}-concept batch trips batch_cap_verdict() while {len(under)} does not.")
        print("  Exiting 3, the DECLARED teeth code.")
        return 3

    return run_check(root, args.base, args.check)


if __name__ == "__main__":
    sys.exit(main())
