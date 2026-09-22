#!/usr/bin/env python3
"""Union-completeness meta-test for `scripts/audit-gates.sh`'s `--suite`
dispatcher (PR-C, Gate 267): every bannered Gate N in the full-suite region —
including letter-suffixed sub-gates (3b/5b/9b), each as its own INDEPENDENT
token — must appear in at least one named suite.

WHY A SEPARATE CHECKER, NOT A HAND-COUNTED ASSERTION: the suite membership
table (`_suite_gate_tokens()` in scripts/audit-gates.sh) and the real banner
set are two independently-maintained things; a completeness claim is only
worth anything if it is re-derived from BOTH every time, never hard-coded as
a number that can go stale the next time a gate is added. So this script:

  1. Asks `audit-gates.sh` itself — via `--list-suites` then `--list-suite-gates
     <name>` for each one — what the union of every suite's membership is.
     This is the SAME code path `--suite` uses to run gates, so there is no
     second copy of the table to drift from what actually executes.
  2. Independently parses `scripts/audit-gates.sh`'s own source for the real
     banner set, using the identical strict `echo "── Gate N: …"` header
     regex `scripts/audit-gates-suite-slice.py` uses (matching a comment that
     merely mentions the shape, never a live header — see that script's
     header for the one historical instance that motivates this).
  3. Reports every banner token in (1) missing from (2) — i.e. covered by no
     suite — as a finding.

Deliberately NOT checking the reverse direction (a suite token with no real
banner): the PR-C brief already forbids that at authoring time ("do not
invent gate numbers absent from `── Gate N:` banners"), and
scripts/audit-gates-suite-slice.py fails closed (Ambiguity, exit 2) the
moment such a token is actually used with `--suite`, so it cannot silently
ship. Checking it here too would be a second, redundant enforcement point for
the same invariant — this script's OWN job is the completeness direction Gate
195 does not cover (Gate 195 asks "is every declared gate reachable"; this
script asks "is every reachable gate claimed by >=1 suite").

Exit codes: 0 = every banner covered; 2 = at least one uncovered banner OR a
parse/subprocess ambiguity (fail-closed, matching every other gate-audit
checker in this repo).

Usage:
    python3 scripts/check-gate-suite-coverage.py [path/to/audit-gates.sh]
    python3 scripts/check-gate-suite-coverage.py --self-test
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HEADER_SINGLE_RE = re.compile(r'^\s*echo\s+"─{2,}\s*Gate\s+(\d+[a-z]?)\s*:')
HEADER_RANGE_RE = re.compile(r'^\s*echo\s+"─{2,}\s*Gates\s+(\d+)\s*[–—-]\s*(\d+)\s*:')
SUPPORTED_RE = re.compile(r"Supported:\s*\d")


class Ambiguity(Exception):
    """Could not determine either side of the coverage comparison with
    confidence. Always fail-closed — never report "clean" over an unknown."""


def _run(args: list[str]) -> str:
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise Ambiguity(f"`{' '.join(args)}` exited {proc.returncode}: {proc.stderr.strip()}")
    return proc.stdout


def real_banner_tokens(script: Path) -> set[str]:
    """The ground-truth set: every token a real (executed, not merely
    mentioned-in-a-comment) `echo "── Gate N: …"` header in the full-suite
    region declares. Mirrors scripts/audit-gates-suite-slice.py's own region-
    finding — see that script for why the landmarks below are the right ones.
    """
    try:
        text = script.read_text(encoding="utf-8")
    except OSError as exc:
        raise Ambiguity(f"cannot read {script}: {exc}") from exc
    lines = text.splitlines()

    supported_idx = next((i for i, ln in enumerate(lines) if SUPPORTED_RE.search(ln)), None)
    if supported_idx is None:
        raise Ambiguity("no `Supported:` line — cannot locate the --check dispatcher")
    esac = next((i for i in range(supported_idx, len(lines)) if lines[i].strip() == "esac"), None)
    if esac is None:
        raise Ambiguity("no `esac` after `Supported:` — dispatcher never closes")
    close = next((i for i in range(esac, len(lines)) if lines[i].strip() == "fi"), None)
    if close is None:
        raise Ambiguity("no `fi` after the dispatcher `esac` — cannot split the regions")

    region_start = close + 1
    box_idx = next((i for i in range(region_start, len(lines)) if "═" in lines[i]), None)
    if box_idx is None:
        raise Ambiguity("no closing summary banner (a line containing '═') found")
    region_end = box_idx

    tokens: set[str] = set()
    for i in range(region_start, region_end):
        line = lines[i]
        mr = HEADER_RANGE_RE.match(line)
        if mr:
            lo, hi = int(mr.group(1)), int(mr.group(2))
            if lo > hi:
                raise Ambiguity(f"line {i + 1}: grouped header has lo > hi ({lo}-{hi})")
            tokens.update(str(n) for n in range(lo, hi + 1))
            continue
        ms = HEADER_SINGLE_RE.match(line)
        if ms:
            tokens.add(ms.group(1))
    if not tokens:
        raise Ambiguity("no gate headers found — the region-finding landmarks may have drifted")
    return tokens


def suite_union_tokens(audit_gates_sh: Path) -> set[str]:
    """The union of every suite's membership, read from `audit-gates.sh`
    ITSELF via its `--list-suites` / `--list-suite-gates` introspection
    flags — never a second, hand-maintained copy of the table."""
    names_out = _run(["bash", str(audit_gates_sh), "--list-suites"]).strip()
    names = names_out.split()
    if not names:
        raise Ambiguity("`--list-suites` returned no suite names")
    union: set[str] = set()
    for name in names:
        tokens_out = _run(["bash", str(audit_gates_sh), "--list-suite-gates", name]).strip()
        tokens = tokens_out.split()
        if not tokens:
            raise Ambiguity(f"suite '{name}' has an empty token list")
        union.update(tokens)
    return union


def audit(audit_gates_sh: Path) -> list[str]:
    """Returns a sorted list of finding strings (empty == clean)."""
    real = real_banner_tokens(audit_gates_sh)
    covered = suite_union_tokens(audit_gates_sh)
    uncovered = real - covered
    return [
        f"Gate {tok} is bannered but not a member of any suite"
        for tok in sorted(uncovered, key=_sort_key)
    ]


def _sort_key(tok: str):
    m = re.match(r"(\d+)([a-z]?)", tok)
    return (int(m.group(1)), m.group(2)) if m else (0, tok)


# ── Teeth ────────────────────────────────────────────────────────────────────
def _mutants(src: Path, work: Path) -> list[tuple[str, Path]]:
    """(name, path) — each must produce >=1 finding when audited."""
    base = src.read_text(encoding="utf-8")
    lines = base.splitlines()

    # M1: a new real gate header added to the full-suite region, but its
    # token deliberately never added to any suite's `_suite_gate_tokens()`
    # arm. The mutation must land BEFORE the closing summary box so it is
    # inside the region real_banner_tokens() scans.
    box_i = next(i for i, ln in enumerate(lines) if "═" in ln)
    m1 = (
        lines[:box_i]
        + ['echo "── Gate 909: planted uncovered gate ──"', 'gate "orphan" must_pass "0"', ""]
        + lines[box_i:]
    )
    p1 = work / "m1-uncovered.sh"
    p1.write_text("\n".join(m1) + "\n", encoding="utf-8")
    return [("a real header covered by no suite", p1)]


def _companions(src: Path) -> list[tuple[str, Path]]:
    """(name, path) — each must produce ZERO findings (anti-flood)."""
    return [("the live, unmodified suite", src)]


def self_test(src: Path) -> int:
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for name, path in _mutants(src, work):
            try:
                findings = audit(path)
            except Ambiguity as exc:
                ok = False
                print(f"  \u2717 ERROR auditing mutant '{name}': {exc}")
                continue
            if findings:
                print(f"  \u2713 caught: {name} ({len(findings)} finding(s))")
            else:
                ok = False
                print(f"  \u2717 MISSED: {name} (expected >=1 finding, got none)")

        for name, path in _companions(src):
            try:
                findings = audit(path)
            except Ambiguity as exc:
                ok = False
                print(f"  \u2717 ERROR auditing companion '{name}': {exc}")
                continue
            if not findings:
                print(f"  \u2713 clean:  {name}")
            else:
                ok = False
                print(f"  \u2717 FLOODED on: {name}")
                for f in findings:
                    print(f"      {f}")

        # An audit-gates.sh that cannot even answer --list-suites must fail
        # CLOSED, never report a vacuous "clean" (an unreachable introspection
        # command and a genuinely complete suite map produce different failure
        # shapes, but neither may print "clean").
        broken = work / "unparseable.sh"
        broken.write_text("#!/usr/bin/env bash\necho hello\n", encoding="utf-8")
        try:
            audit(broken)
            ok = False
            print(
                "  \u2717 MISSED: an unparseable/non-conforming script was accepted instead of failing closed"
            )
        except Ambiguity:
            print("  \u2713 caught: a script with no --list-suites support fails closed")

    print("\nteeth verified" if ok else "\nTEETH BROKEN")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", default="scripts/audit-gates.sh")
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="prove the checker's teeth: the planted-uncovered-gate mutant is caught, the live tree is clean",
    )
    args = ap.parse_args()

    src = Path(args.path)
    if args.self_test:
        return self_test(src)

    try:
        findings = audit(src)
    except Ambiguity as exc:
        print(f"check-gate-suite-coverage: FAIL-CLOSED - {exc}", file=sys.stderr)
        return 2

    if findings:
        print(f"check-gate-suite-coverage: {len(findings)} finding(s) in {src}", file=sys.stderr)
        for f in findings:
            print(f"  - {f}", file=sys.stderr)
        return 2

    print(f"check-gate-suite-coverage: {src} — every bannered gate is a member of >=1 suite")
    return 0


if __name__ == "__main__":
    sys.exit(main())
