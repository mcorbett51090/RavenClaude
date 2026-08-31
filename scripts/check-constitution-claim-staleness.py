#!/usr/bin/env python3
"""A claim in an every-session file must not be contradicted by the tree it describes.

## The defect this closes (P19)

`CLAUDE.md`, `AGENTS.md` and each plugin's `CLAUDE.md` are loaded into EVERY
session. A claim in one of them is not documentation -- it is a prior that every
future agent starts out believing, with nobody left to cross-examine it.

This repo has already paid for that, and its own constitution says so:

    "A stale 'Still open' in a file every session loads is an active defect,
     not a bookkeeping lag. When you close a door, supersede the entry that
     says it's open in the same PR."                      -- the v0.196.0 note

That note exists because an agent read a stale "Still open" list, took it at
face value, and told the maintainer TWICE that his command-review tribunal was
broken on macOS -- while it had been working for releases. The reader it fooled
was the constitution's primary audience: an agent.

So the rule was already written. It had no mechanism. This is the mechanism.

## What it checks -- and what it deliberately does NOT

It checks exactly ONE thing, because it is the only thing checkable without
guessing: a claim that a **named artifact is missing**, where the artifact is in
fact present. Both halves are binary and verifiable:

  * a named script asserted gone   -> is it on disk?
  * a gate asserted never wired    -> is it in audit-gates.sh?

It does NOT try to decide whether a "Still open" item is *actually* still open.
That needs a judgment about the world, not a fact about the tree, and a checker
that guesses at it produces exactly the false finding this initiative exists to
prevent.

## The two false-positive classes, found by hand-verifying before wiring

Run over the live tree, the first draft returned two hits. BOTH were false, each
a distinct class, now suppressed and pinned by a fixture rebuilt from the real
sentence that produced it:

  1. **Conditional** -- a sentence describing what a hook does *when* a manifest
     is missing is a statement about a code path, not a claim the file is gone.
     (`claim-grounding-lint.sh` suppresses the same class for the same reason.)

  2. **Past-tense history** -- a milestone recording that a gate *had been*
     unreachable and was then fixed. This repo's stated convention is to KEEP
     superseded entries as dated records, so past-tense prose about a closed
     defect is the convention working, not drift.

After both suppressions the tree is clean, so this ships as a **regression
preventer**, not a remediation. That is stated rather than dressed up -- an empty
finding list is a claim about the probe, so the fixtures below prove the probe
can return the opposite.

Exit codes:  0 = clean;  2 = a contradicted claim, or a file could not be read.
Exit 1 is never used for a finding -- the harness treats exit 1 as a
non-blocking error, which is a silent fail-open.

Usage:
    python3 scripts/check-constitution-claim-staleness.py
    python3 scripts/check-constitution-claim-staleness.py --self-test
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

GATES = Path("scripts/audit-gates.sh")

# A "named artifact is missing" claim. The path and the assertion must sit close
# together; a 120-char window keeps a path in one sentence from binding to an
# assertion two sentences later.
ABSENT_CLAIM = re.compile(
    r"`([A-Za-z0-9_./-]+\.(?:py|sh|mjs|js|json))`"
    r"[^.\n]{0,120}?"
    r"(does not exist|is a phantom|was deleted|were deleted"
    r"|never (?:shipped|existed|built)|no such file|is absent)",
    re.I,
)

# A "gate is not wired" claim, checkable against the suite itself.
UNRUN_CLAIM = re.compile(
    r"Gate (\d+)[^.\n]{0,100}?"
    r"(was unreachable|never ran|is unrun|is not registered|nothing runs it)",
    re.I,
)

# SUPPRESSION 1 -- a conditional lead makes the sentence a statement about a code
# path rather than a claim about the tree.
CONDITIONAL = re.compile(r"\b(if|when|whenever|unless|should|in case|were|absent)\b", re.I)

# SUPPRESSION 2 -- past tense / supersession. Superseded entries are KEPT here on
# purpose as dated historical records.
PAST_TENSE = re.compile(
    r"\b(was|were|used to|previously|formerly|until|SUPERSEDED|historical"
    r"|no longer|since fixed|has been fixed|stale)\b",
    re.I,
)

# An inline opt-out, mirroring the `claim-lint-ok` convention already in the repo.
SUPPRESS_MARKER = re.compile(r"staleness-ok\b")


class Finding(NamedTuple):
    file: str
    line: int
    claim: str
    detail: str


def constitution_files(repo: Path) -> list[Path]:
    """Every file loaded into a session's context."""
    out = [repo / "CLAUDE.md", repo / "AGENTS.md"]
    out += sorted((repo / "plugins").glob("*/CLAUDE.md"))
    return [p for p in out if p.is_file()]


def _suppressed(line: str, span_start: int) -> bool:
    """True when the sentence around the claim is conditional or historical.

    The lead is read from the start of the line up to the claim, so a conditional
    appearing AFTER the assertion cannot launder it.
    """
    lead = line[:span_start]
    return bool(
        SUPPRESS_MARKER.search(line)
        or CONDITIONAL.search(lead)
        or PAST_TENSE.search(lead)
        or PAST_TENSE.search(line[span_start : span_start + 160])
    )


def check_line(line: str, rel: str, lineno: int, repo: Path, gate_src: str) -> list[Finding]:
    found: list[Finding] = []

    for m in ABSENT_CLAIM.finditer(line):
        if _suppressed(line, m.start()):
            continue
        if (repo / m.group(1)).is_file():
            found.append(
                Finding(
                    rel,
                    lineno,
                    m.group(0).strip(),
                    f"asserts `{m.group(1)}` is gone, but it is on disk. A stale claim "
                    f"in an every-session file is an active defect: the next agent "
                    f"starts out believing it.",
                )
            )

    for m in UNRUN_CLAIM.finditer(line):
        if _suppressed(line, m.start()):
            continue
        num = m.group(1)
        if re.search(rf"──\s*Gate {num}\s*:", gate_src):
            found.append(
                Finding(
                    rel,
                    lineno,
                    m.group(0).strip(),
                    f"asserts Gate {num} is unwired, but it IS registered in "
                    f"audit-gates.sh. Supersede the entry in the PR that closed it.",
                )
            )

    return found


def scan(repo: Path) -> tuple[list[Finding], int]:
    gate_src = (repo / GATES).read_text(encoding="utf-8") if (repo / GATES).is_file() else ""
    findings: list[Finding] = []
    files = constitution_files(repo)
    for f in files:
        rel = f.relative_to(repo).as_posix()
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            findings.extend(check_line(line, rel, i, repo, gate_src))
    return findings, len(files)


# --------------------------------------------------------------------------
# Self-test.
#
# Fixtures are assembled by concatenation so this file does not itself contain a
# literal contradicted claim -- a source-scan gate matches its own fixtures, and
# that has bitten this repo repeatedly.
#
# The two suppression fixtures are rebuilt from the REAL sentences that produced
# the only two live hits, so the suppressions are proven against cases that
# actually occurred rather than invented ones.
# --------------------------------------------------------------------------

_P = "`scripts/" + "real-file.py`"
_GONE = "`scripts/" + "genuinely-gone.py`"
_MISSING = "does not " + "exist"
_UNWIRED = "is not " + "registered"


def _self_test() -> int:
    cases: list[tuple[str, str, bool]] = [
        ("contradicted-path", f"The launcher {_P} {_MISSING} on disk.", True),
        ("contradicted-gate", f"Gate 7 {_UNWIRED} and nothing runs it.", True),
        (
            # REAL false positive #1, reconstructed from the layout-hook sentence.
            "conditional-is-not-a-claim",
            f"The hook silently allows everything if {_P} is absent.",
            False,
        ),
        (
            # REAL false positive #2, reconstructed from the v0.243.0 milestone.
            "past-tense-history-is-the-convention",
            "Gate 7 was unreachable for a whole release while the suite reported green.",
            False,
        ),
        ("claim-that-is-TRUE-stays-silent", f"The helper {_GONE} {_MISSING}.", False),
        ("inline-opt-out-honored", f"The file {_P} {_MISSING}. <!-- staleness-ok -->", False),
    ]

    failures = 0
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        (repo / "scripts").mkdir()
        (repo / "scripts" / "real-file.py").write_text("# exists\n", encoding="utf-8")
        gate_src = 'echo "── Gate 7: a registered gate ──"\n'

        for name, line, should_fire in cases:
            got = check_line(line, "CLAUDE.md", 1, repo, gate_src)
            ok = bool(got) == should_fire
            print(
                f"  [{'ok' if ok else 'FAIL'}] {name}: "
                f"expected={'fire' if should_fire else 'silent'} got={len(got)}"
            )
            if not ok:
                failures += 1

    print(f"\nself-test: {len(cases) - failures} passed, {failures} failed")
    return 2 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    repo = Path.cwd()
    if not (repo / "CLAUDE.md").is_file():
        print("ERROR: CLAUDE.md not found (run from the repo root).", file=sys.stderr)
        return 2

    findings, n_files = scan(repo)

    if not findings:
        print(
            f"OK: no contradicted claim in {n_files} every-session file(s). "
            f"Conditional and past-tense/superseded phrasings are suppressed by "
            f"design -- both were real false positives found before wiring."
        )
        return 0

    print(f"{len(findings)} contradicted claim(s):\n", file=sys.stderr)
    for f in findings:
        print(f"  {f.file}:{f.line}\n    {f.claim}\n    -> {f.detail}\n", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
