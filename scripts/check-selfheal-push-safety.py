#!/usr/bin/env python3
"""A self-healing workflow must never gain a direct-to-`main` push path.

## The defect this closes (P14)

The self-heal workflow regenerates `index.html` / `dashboard.html` / the copilot
package after every merge, so `main` stays fresh without those files ever sitting
on a PR's critical path. It reaches `main` the safe way: it opens a PR from a bot
branch, waits for the ruleset's REQUIRED checks, and squash-merges that.

Nothing gated that shape. A future edit that "simplified" it back to a direct push
would look tidier, pass review, and quietly convert a checked path into an
unchecked one -- on the one workflow that runs after every single merge.

## THE HONEST BOUND -- read this before trusting the gate

**This is a proxy-string scan, not a behavioural proof.**

The runtime guarantee is and remains the **branch-protection ruleset**: a direct
push to `main` is rejected because "changes must be made through a pull request".
This scan cannot see:

  * a push whose ref is computed at runtime (`git push origin "HEAD:$BRANCH"`)
  * a commit made through `gh api` / the REST API
  * an admin merge that bypasses required checks by other means

So it is **paired with the ruleset, never a replacement for it.** What it buys is
catching the enumerated literal shapes at PR-review time, where a human is looking,
instead of after the fact. Claiming more than that would be the false-assurance
failure this initiative exists to close.

## Four shapes, because one literal would leave three uncaught

A fixture testing only the plain `git push origin main` would pass a workflow that
used `HEAD:main` -- the exact "gate that asserts less than it appears to" trap this
check is meant to prevent, reproduced inside the check itself. All four are
enumerated and each has its own must-fail fixture.

## Two false-positive classes, both found in the live tree before wiring

  1. **A comment describing the rule.** `regenerate-artifacts.yml` explains its own
     design with the words "direct `git push origin HEAD:main` is rejected by the
     ruleset". A naive grep flags the sentence that documents the invariant --
     source-scan-matches-prose, which this repo has shipped repeatedly.

  2. **Fixture strings inside another gate.** `validate-marketplace.yml` carries
     quoted push commands as *test data* for the destructive-command guard. They
     are strings in an array, not commands anyone runs.

Both are excluded structurally: only un-commented lines inside a `run:` block are
scanned, and a line whose push appears inside a quoted string is treated as data.

Exit codes:  0 = clean;  2 = a finding, or a workflow could not be parsed.
Exit 1 is never used for a finding -- the harness treats exit 1 as a non-blocking
error, which is a silent fail-open. An unparseable workflow FAILS, never passes.

Usage:
    python3 scripts/check-selfheal-push-safety.py
    python3 scripts/check-selfheal-push-safety.py --self-test
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

WORKFLOW_DIR = Path(".github/workflows")

# A workflow is "self-healing" when it WRITES ARTIFACTS BACK after a push to a
# protected branch. Identified by behaviour, not by filename, so a rename cannot
# silently drop it out of scope.
#
# ⛔ THE ACTION MARKER MUST BE MATCHED IN CODE, NOT IN PROSE. The first draft
# included `regenerat` and matched `validate-marketplace.yml` -- a pure VALIDATION
# workflow that writes nothing -- purely because its comments explain that certain
# artifacts are "regenerated post-merge by regenerate-artifacts.yml". Scoping a
# checker by a word that appears in an explanation of the rule is the same
# source-scan-matches-prose failure this repo has shipped repeatedly, and here it
# pulled a whole unrelated workflow into scope and produced three false findings.
SELFHEAL_MARKERS = (
    re.compile(r"^\s*push:\s*$", re.M),
    re.compile(r"branches:\s*\[\s*main\s*\]|^\s*-\s*main\s*$", re.M),
)
# A genuine write-back: the PR action, or an actual commit executed in a run block.
SELFHEAL_ACTION = re.compile(r"create-pull-request|\bgit\s+commit\b")

# The protected refs a self-heal must never push to directly.
_PROTECTED = r"(?:main|master)"

# The four enumerated shapes. Each carries its own name so a finding says which.
PUSH_SHAPES: list[tuple[str, re.Pattern[str]]] = [
    (
        "plain-push-to-protected",
        re.compile(rf"\bgit\s+push\b[^\n]*\borigin\s+{_PROTECTED}\b"),
    ),
    (
        "head-colon-protected",
        re.compile(rf"\bgit\s+push\b[^\n]*\bHEAD:\+?{_PROTECTED}\b"),
    ),
    (
        "refs-heads-protected",
        re.compile(rf"\bgit\s+push\b[^\n]*:refs/heads/{_PROTECTED}\b"),
    ),
    (
        "admin-merge-bypass",
        re.compile(r"\bgh\s+pr\s+merge\b[^\n]*--admin\b"),
    ),
]

# The sanctioned landing path: open a PR, let the ruleset's required checks run,
# then squash-merge. Explicitly NOT a finding.
SANCTIONED = re.compile(r"create-pull-request|gh\s+pr\s+merge(?![^\n]*--admin)")

# An escape sentinel, matching the repo's `# noport` convention.
SENTINEL = re.compile(r"#\s*selfheal-push-ok\b")


class Finding(NamedTuple):
    file: str
    line: int
    shape: str
    text: str


def _run_block_lines(src: str) -> list[tuple[int, str]]:
    """Lines that are executable shell inside a `run:` block.

    ⛔ THIS IS THE FALSE-POSITIVE FLOOR, and both classes it removes were found in
    the live tree, not imagined:

      * a whole-line COMMENT (`# … git push origin HEAD:main …`) is prose that
        documents the invariant -- flagging it would flag the sentence explaining
        why the rule exists;
      * a line OUTSIDE any `run:` block is YAML config or, in one real case, a
        quoted fixture string in another gate's test-data array.

    Block membership is tracked by indentation, which is how YAML actually scopes a
    literal block -- matching `run:` and then scanning to end-of-file would pull in
    every later key.
    """
    out: list[tuple[int, str]] = []
    in_run = False
    run_indent = 0

    for i, raw in enumerate(src.splitlines(), 1):
        stripped = raw.strip()
        indent = len(raw) - len(raw.lstrip())

        if not stripped:
            continue

        if in_run and indent <= run_indent and not raw.startswith(" " * (run_indent + 1)):
            in_run = False

        m = re.match(r"^(\s*)-?\s*run:\s*(\|-?|>-?)?\s*(.*)$", raw)
        if m:
            in_run = True
            run_indent = len(m.group(1))
            inline = m.group(3).strip()
            if inline and not inline.startswith("#"):
                out.append((i, inline))
            continue

        if in_run and not stripped.startswith("#"):
            out.append((i, stripped))

    return out


# A line that is ENTIRELY a quoted string is data, not a command.
#
# ⛔ FOUND IN THE LIVE TREE, not imagined: `validate-marketplace.yml` builds a bash
# array of denied-command fixtures, one quoted push per line, to test the
# destructive-command guard. Those are the *inputs* to another gate. Executing
# nothing, they are still inside a `run:` block, so block membership alone does not
# exclude them -- the quoting does. A real command is never wrapped whole in quotes.
_WHOLE_LINE_STRING = re.compile(r"""^\s*["'][^"']*["']\s*(?:#.*)?$""")


def check_source(src: str, rel: str) -> list[Finding]:
    findings: list[Finding] = []
    for lineno, line in _run_block_lines(src):
        if SENTINEL.search(line) or _WHOLE_LINE_STRING.match(line):
            continue
        for shape, pat in PUSH_SHAPES:
            if pat.search(line):
                findings.append(Finding(rel, lineno, shape, line[:110]))
    return findings


def is_selfheal(src: str) -> bool:
    """A workflow that triggers on a push to a protected branch AND writes artifacts.

    The action marker is searched over COMMENT-STRIPPED source only -- see the note
    on SELFHEAL_ACTION for the workflow this wrongly pulled into scope when it
    scanned prose. The trigger markers are matched on raw source because `on:`/
    `branches:` are YAML keys, which comment-stripping leaves untouched anyway.
    """
    if not all(p.search(src) for p in SELFHEAL_MARKERS):
        return False
    code = "\n".join(
        "" if ln.strip().startswith("#") else ln for ln in src.splitlines()
    )
    return bool(SELFHEAL_ACTION.search(code))


def scan(repo: Path) -> tuple[list[Finding], list[str]]:
    wf_dir = repo / WORKFLOW_DIR
    if not wf_dir.is_dir():
        raise FileNotFoundError(f"{WORKFLOW_DIR} not found")

    findings: list[Finding] = []
    scanned: list[str] = []
    for wf in sorted(wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml")):
        try:
            src = wf.read_text(encoding="utf-8")
        except OSError as exc:  # unparseable => fail, never pass
            raise RuntimeError(f"cannot read {wf}: {exc}") from exc
        if not is_selfheal(src):
            continue
        rel = wf.relative_to(repo).as_posix()
        scanned.append(rel)
        findings.extend(check_source(src, rel))
    return findings, scanned


# --------------------------------------------------------------------------
# Self-test. Fixtures are assembled by concatenation so this file does not itself
# contain a literal direct-push command -- a source-scan gate matches its own
# fixtures, and this repo has paid for that more than once.
# --------------------------------------------------------------------------

_PUSH = "git " + "push"
_MERGE = "gh pr " + "merge"


def _wf(run_body: str) -> str:
    """A minimal self-heal-shaped workflow wrapping one run block."""
    return (
        "name: t\non:\n  push:\n    branches: [main]\njobs:\n  j:\n"
        "    runs-on: ubuntu-latest\n    steps:\n"
        "      - name: regenerate\n        run: |\n"
        + "".join(f"          {ln}\n" for ln in run_body.splitlines())
    )


def _self_test() -> int:
    cases: list[tuple[str, str, bool]] = [
        # --- the four enumerated shapes must EACH be caught ---
        ("shape-plain", _wf(f"{_PUSH} origin main"), True),
        ("shape-head-colon", _wf(f"{_PUSH} origin HEAD:main"), True),
        ("shape-refs-heads", _wf(f"{_PUSH} origin HEAD:refs/heads/main"), True),
        ("shape-admin-merge", _wf(f'{_MERGE} "$n" --squash --admin'), True),
        ("shape-master-too", _wf(f"{_PUSH} origin master"), True),
        # --- the sanctioned landing path is NOT a finding ---
        ("sanctioned-pr-merge", _wf(f'{_MERGE} "$n" --squash --delete-branch'), False),
        # --- FALSE POSITIVE CLASS 1: a comment documenting the rule (REAL) ---
        (
            "comment-documenting-the-rule-is-silent",
            _wf(f"# main is protected: direct `{_PUSH} origin HEAD:main` is rejected\ngit status"),
            False,
        ),
        # --- FALSE POSITIVE CLASS 2: fixture strings outside a run block (REAL) ---
        (
            "fixture-string-outside-run-is-silent",
            "name: t\non:\n  push:\n    branches: [main]\njobs:\n  j:\n"
            "    runs-on: ubuntu-latest\n    steps:\n"
            "      - name: regenerate\n        env:\n"
            f'          CASES: |\n            "{_PUSH} origin main"\n'
            "        run: |\n          git commit -m x\n",
            False,
        ),
        (
            # FALSE POSITIVE CLASS 2b (REAL): a quoted fixture array INSIDE a run
            # block -- another gate's test data, which block membership alone
            # cannot exclude.
            "quoted-fixture-array-inside-run-is-silent",
            _wf(f'CASES=(\n"{_PUSH} -f origin main"\n"{_PUSH} origin +HEAD:main"\n)\ngit commit -m x'),
            False,
        ),
        ("sentinel-honored", _wf(f"{_PUSH} origin main  # selfheal-push-ok"), False),
    ]

    failures = 0
    for name, src, should_fire in cases:
        got = check_source(src, "fixture.yml")
        ok = bool(got) == should_fire
        shapes = sorted({f.shape for f in got})
        print(
            f"  [{'ok' if ok else 'FAIL'}] {name}: "
            f"expected={'fire' if should_fire else 'silent'} got={shapes or 'none'}"
        )
        if not ok:
            failures += 1

    # The scope predicate must not silently drop the real workflow.
    if not is_selfheal(_wf("git commit -m x")):
        print("  [FAIL] is_selfheal: a self-heal-shaped workflow was not recognised")
        failures += 1
    else:
        print("  [ok] is_selfheal recognises a self-heal-shaped workflow")

    print(f"\nself-test: {len(cases) + 1 - failures} passed, {failures} failed")
    return 2 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    try:
        findings, scanned = scan(Path.cwd())
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not scanned:
        # An empty scope is a claim about the PROBE. Fail rather than report clean.
        print(
            "ERROR: no self-healing workflow found. The scope predicate matched "
            "nothing, which is a finding about this checker, not a clean result.",
            file=sys.stderr,
        )
        return 2

    if not findings:
        print(
            f"OK: {len(scanned)} self-healing workflow(s) have no direct-to-protected "
            f"push path ({', '.join(scanned)}). Proxy-string scan — the runtime "
            f"guarantee is the branch-protection ruleset, which this pairs with."
        )
        return 0

    print(f"{len(findings)} direct-to-protected push path(s):\n", file=sys.stderr)
    for f in findings:
        print(f"  {f.file}:{f.line}  [{f.shape}]\n    {f.text}\n", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
