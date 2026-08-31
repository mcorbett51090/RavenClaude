#!/usr/bin/env python3
"""Gate 221 - forms-engineering honesty markers (three sub-checks, one number).

Two claims in this plugin are weaker than they read, and a one-time release grep
protects only the PR that introduces it. Both ship behind permanent CI
sub-checks with must-fail halves instead.

  A  NOVEL-SYNTHESIS MARKER. Applying statistical process control to web-form
     telemetry is OUR synthesis. Two targeted open-web searches returned SPC
     generalities and form-analytics generalities with zero intersection. Any
     documentation surface that co-occurs an SPC/DMAIC term with a
     form-analytics term must carry the verbatim marker, so a reader cannot
     mistake the join for received practice.
  B  CHALLENGE-WIDGET WCAG LEVEL. The vendor's own documentation gives one
     conformance level on its overview page and a different one on its plans
     page. No surface may state either level unqualified; a level near a
     challenge-widget mention must sit in a block that names the conflict. The
     window is LINE-BASED, never same-physical-line - wrapped markdown prose
     almost never puts two strings on one line, and a same-line probe reports
     green while measuring nothing.
  C  NO VENDOR PRICING. Platform pricing goes stale within a quarter. Prose may
     not carry a currency figure or a per-period rate. Scoped to prose lines:
     a `$PATH` or a shell snippet inside a fenced block would otherwise
     false-positive.

## ⛔ LIMITATIONS, WRITTEN HERE RATHER THAN OVERSOLD

1. Sub-check A is FILE-LEVEL co-occurrence, not paragraph-level. A second,
   unlabelled synthesis claim later in an already-marked file evades it. A human
   read at authoring time is still required.
2. All three are STRING-SHAPED. This repo has recorded twice that source-scan
   gates match PROSE, and that a grep is satisfied by the thing being described.
   These check "a sentence is present", not "the content is honest". They raise
   the floor; they do not certify the property.
3. ⛔ Sub-check A covers DOCUMENTATION SURFACES ONLY. It does NOT and cannot
   verify that `form_metrics.py` PRINTS the marker - a marker in a docstring, a
   comment, or an unexercised branch satisfies a file-level string check
   identically to one emitted on every run. That half is GATE 220, which
   executes the script and reads captured stderr. Do not infer script-output
   coverage from a green sub-check A here.

Exit codes: 0 = clean; 2 = a finding or an empty scope (fail-closed). Exit 1 is
never used.

Usage:
    python3 scripts/check-forms-honesty-markers.py
    python3 scripts/check-forms-honesty-markers.py --self-test
    python3 scripts/check-forms-honesty-markers.py --must-fail
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
FORMS = ROOT / "plugins" / "forms-engineering"
FIXTURES = ROOT / "tests" / "fixtures" / "forms-engineering" / "gate221"

# ── Sub-check A ──────────────────────────────────────────────────────────────
MARKER = (
    "[NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not "
    "established practice. We found no published work joining web-form telemetry to "
    "SPC/DMAIC (open-web search, 2026-08-17); the negative finding is bounded by that "
    "method and is not proof of universal absence.]"
)

SPC_TERMS = (
    re.compile(r"control\s+chart", re.IGNORECASE),
    re.compile(r"\bX-mR\b", re.IGNORECASE),
    re.compile(r"\bDMAIC\b", re.IGNORECASE),
    re.compile(r"sigma", re.IGNORECASE),
    re.compile(r"common[-\s]cause", re.IGNORECASE),
    re.compile(r"special[-\s]cause", re.IGNORECASE),
)
ANALYTICS_TERMS = (
    re.compile(r"form_start"),
    re.compile(r"abandonment", re.IGNORECASE),
    re.compile(r"drop[-\s]off", re.IGNORECASE),
    re.compile(r"completion\s+rate", re.IGNORECASE),
)

# The four DOCUMENTATION surfaces that must be inside sub-check A's firing set.
# The fifth surface named by the plan - scripts/form_metrics.py - is Gate 220's
# job, because only an execution assertion proves a label reaches a user.
# ⛔ Rule #5 and the telemetry-plan template are on this list deliberately: both
# co-occur the two term families BY CONSTRUCTION ("three-sigma" is in rule #5's
# own filename). Listing them here means a future editor who narrows the term
# list to make the gate quiet gets a RED here instead of a quiet gate.
REQUIRED_MARKED_SURFACES = (
    "knowledge/form-telemetry-and-spc.md",
    "skills/form-telemetry-and-control/SKILL.md",
    "best-practices/do-not-put-three-sigma-limits-on-a-low-volume-form-series.md",
    "templates/form-telemetry-plan.md",
)

# ── Sub-check B ──────────────────────────────────────────────────────────────
WCAG_LEVEL_RE = re.compile(r"WCAG\s*2\.2\s*(AAA|AA)\b")
CHALLENGE_RE = re.compile(r"turnstile|captcha|challenge\s+widget|challenge\s+token", re.IGNORECASE)
CONFLICT_PHRASE = "unestablished pending a VPAT"
WCAG_WINDOW = 8

# ── Sub-check C ──────────────────────────────────────────────────────────────
PRICING_RES = (
    re.compile(r"[$£€]\s?\d"),
    re.compile(r"\b\d+(?:\.\d+)?\s*(?:USD|EUR|GBP)\b", re.IGNORECASE),
    re.compile(r"/mo\b", re.IGNORECASE),
    re.compile(r"/month\b", re.IGNORECASE),
    re.compile(r"per\s+month", re.IGNORECASE),
    re.compile(r"per\s+year", re.IGNORECASE),
)
FENCE_RE = re.compile(r"^\s*(```|~~~)")


class Finding(NamedTuple):
    check: str
    path: str
    line: int
    detail: str

    def render(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        return f"  [{self.check}] {where}: {self.detail}"


def normalise(text: str) -> str:
    """Collapse blockquote markers and whitespace so a wrapped marker still matches."""
    out = []
    for line in text.splitlines():
        out.append(re.sub(r"^\s*>\s?", "", line))
    return re.sub(r"\s+", " ", " ".join(out)).strip()


NORM_MARKER = re.sub(r"\s+", " ", MARKER).strip()


def prose_lines(lines: list[str]) -> list[tuple[int, str]]:
    """Lines outside fenced code blocks, with their 0-based index."""
    out: list[tuple[int, str]] = []
    in_fence = False
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out.append((i, line))
    return out


def analyse_file(path: Path, rel: str) -> tuple[list[Finding], bool]:
    """Return (findings, sub_check_A_fired) for one markdown file."""
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    norm = normalise(text)

    # ── A ────────────────────────────────────────────────────────────────────
    spc = next((p.pattern for p in SPC_TERMS if p.search(text)), None)
    analytics = next((p.pattern for p in ANALYTICS_TERMS if p.search(text)), None)
    a_fired = bool(spc and analytics)
    if a_fired and NORM_MARKER not in norm:
        findings.append(
            Finding(
                "A",
                rel,
                0,
                "co-occurs an SPC/DMAIC term (%s) with a form-analytics term (%s) but "
                "carries no verbatim NOVEL SYNTHESIS marker" % (spc, analytics),
            )
        )

    # ── B ────────────────────────────────────────────────────────────────────
    for i, line in enumerate(lines):
        m = WCAG_LEVEL_RE.search(line)
        if not m:
            continue
        lo = max(0, i - WCAG_WINDOW)
        hi = min(len(lines), i + WCAG_WINDOW + 1)
        window = "\n".join(lines[lo:hi])
        if not CHALLENGE_RE.search(window):
            continue
        if CONFLICT_PHRASE not in window:
            findings.append(
                Finding(
                    "B",
                    rel,
                    i + 1,
                    "states 'WCAG 2.2 %s' within %d lines of a challenge-widget mention "
                    "without naming the documentation conflict (%r must appear in the "
                    "same block)" % (m.group(1), WCAG_WINDOW, CONFLICT_PHRASE),
                )
            )

    # ── C ────────────────────────────────────────────────────────────────────
    for i, line in prose_lines(lines):
        for pat in PRICING_RES:
            hit = pat.search(line)
            if hit:
                findings.append(
                    Finding(
                        "C",
                        rel,
                        i + 1,
                        "prose carries a price-shaped figure (%r) - vendor pricing goes "
                        "stale within a quarter and is never published here" % hit.group(0),
                    )
                )
                break
    return findings, a_fired


def scan_tree(scan_root: Path) -> tuple[list[Finding], set[str], int]:
    findings: list[Finding] = []
    fired: set[str] = set()
    files = sorted(p for p in scan_root.rglob("*.md") if p.is_file())
    for path in files:
        rel = path.relative_to(scan_root).as_posix()
        f, a = analyse_file(path, rel)
        findings.extend(f)
        if a:
            fired.add(rel)
    return findings, fired, len(files)


def audit() -> tuple[list[Finding], int]:
    if not FORMS.is_dir():
        return [Finding("A", "plugins/forms-engineering", 0, "plugin tree is missing")], 0
    findings, fired, n = scan_tree(FORMS)
    if n == 0:
        findings.append(
            Finding("A", "plugins/forms-engineering", 0, "no markdown files found - empty scope")
        )
    # The required surfaces must be IN the firing set. If one drops out, either
    # the file lost its subject or the term list was narrowed to quiet the gate.
    for rel in REQUIRED_MARKED_SURFACES:
        if not (FORMS / rel).is_file():
            findings.append(Finding("A", rel, 0, "required marked surface is missing"))
        elif rel not in fired:
            findings.append(
                Finding(
                    "A",
                    rel,
                    0,
                    "no longer co-occurs both term families - sub-check A's term list "
                    "has been narrowed, or this surface lost its subject",
                )
            )
    return findings, n


# ── Self-test ────────────────────────────────────────────────────────────────

FIXTURE_EXPECTATIONS = (
    ("must-fail-a-unmarked-synthesis.md", ("A",), ()),
    ("must-fail-b-unqualified-wcag-level.md", ("B",), ()),
    ("must-fail-c-vendor-pricing.md", ("C",), ()),
    ("must-pass-marked-synthesis.md", (), ("A",)),
    ("must-pass-named-wcag-conflict.md", (), ("B",)),
    # ⛔ A negative INSTRUCTION about pricing must not itself trip sub-check C.
    # A gate that fires on the rule forbidding a thing is a gate whose term list
    # gets trimmed the first time it is inconvenient.
    ("must-pass-negative-instruction.md", (), ("C",)),
    # ⛔ Rule #5's real shape: an SPC prohibition about form series. It MUST pass
    # once marked - this is the contradiction that would otherwise make Gate 221
    # red on the plugin's own required content.
    ("must-pass-rule-five-shape.md", (), ("A", "B", "C")),
)


def self_test() -> int:
    problems: list[str] = []
    if not FIXTURES.is_dir():
        print(f"✗ fixture directory missing: {FIXTURES}", file=sys.stderr)
        return 2
    for name, must_fire, must_not_fire in FIXTURE_EXPECTATIONS:
        path = FIXTURES / name
        if not path.is_file():
            problems.append(f"fixture missing: {name}")
            continue
        found = {f.check for f in analyse_file(path, name)[0]}
        for check in must_fire:
            if check not in found:
                problems.append(
                    f"{name}: sub-check {check} did NOT fire (fired: {sorted(found) or 'none'})"
                )
        for check in must_not_fire:
            if check in found:
                problems.append(
                    f"{name}: sub-check {check} fired but must not (fired: {sorted(found)})"
                )
    if problems:
        print("✗ check-forms-honesty-markers self-test FAILED:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print("✓ self-test: A/B/C each distinguish pass from fail; negative-instruction stays silent")
    return 0


def must_fail() -> int:
    """Plant all three violations; exit 2 when they ARE caught."""
    with tempfile.TemporaryDirectory() as td:
        planted = Path(td) / "knowledge"
        planted.mkdir(parents=True)
        (planted / "planted.md").write_text(
            "# planted\n\n"
            "The abandonment rate is monitored on a control chart.\n\n"
            "Turnstile is fully WCAG 2.2 AA compliant.\n\n"
            "The hosted tier costs $29/month.\n",
            encoding="utf-8",
        )
        findings, _, _ = scan_tree(Path(td))
    kinds = {f.check for f in findings}
    if {"A", "B", "C"} <= kinds:
        print(f"✓ must-fail: all three planted violations ARE caught (sub-checks {sorted(kinds)})")
        return 2
    print(f"✗ must-fail: only {sorted(kinds)} caught - the gate has no teeth")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.must_fail:
        return must_fail()

    findings, n = audit()
    if findings:
        print(
            f"✗ forms-engineering honesty markers: {len(findings)} finding(s) across "
            f"{n} markdown file(s)",
            file=sys.stderr,
        )
        for f in findings:
            print(f.render(), file=sys.stderr)
        return 2
    print(f"✓ forms-engineering honesty markers clean ({n} markdown files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
