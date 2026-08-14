#!/usr/bin/env python3
"""No plugin `description` may carry an artifact-count literal (P13).

## The defect this closes

Every plugin's `plugin.json` description, and its mirror in
`.claude-plugin/marketplace.json`, used to open with a hand-maintained inventory:

    "... - 4 agents (a, b, c, d), 5 skills, 4 templates, 5 commands,
     1 advisory hook, 8 best-practice rules, and a 4-file knowledge bank."

Every digit there is a claim about the tree that nothing derived. Add a skill and
three surfaces go stale at once (plugin.json, marketplace.json, README), plus the
Copilot projection that inherits the core description verbatim. That is the
count/version-mirror drift class (P13) and the copilot-freshness cascade.

`check-marketplace-claims.py` verified **two** of the six counted quantities
(skills, agents). The other four drifted freely, and the ~180 README tables had
no coverage at all.

## Why a NEGATIVE assertion instead of a freshness check

Owner decision **D1** (3-seat cross-model panel, 2-1) settled it: the prose counts
are **dropped everywhere** rather than made self-healing. A freshness gate keeps a
derived number in sync; dropping the number makes the whole class *impossible by
construction*. This checker is the enforcement of that ruling and doubles as the
migration-completeness proof -- if it is green, the DROP is complete.

The counts that remain are the ones a machine derives and self-heals: the
`| Skills | 53 |` rows of `ravenclaude-core/README.md`'s "What's inside" table and
the repo-level `ships **N plugins**` claim, both owned by
`check-marketplace-claims.py --fix`. Those are *data columns*, not prose, and they
are deliberately out of scope here.

## THE TRAP THIS CHECKER WAS BUILT AROUND -- read before editing the pattern

The obvious pattern is::

    \\b\\d+\\s+(agents?|skills?|templates?|commands?|hooks?|rules?)\\b

Measured against the live tree it found **595** literals. The adjective-tolerant
pattern below found **794**. The narrow one misses **199 (25%)** -- every count
separated from its noun by an adjective, and every count welded to its unit by a
hyphen::

    1 advisory hook            1 advisory anti-pattern hook      2 grief-aware agents
    10 best-practice rules     23 best-practice rules            2 runbook templates
    a 3-file knowledge bank    a 4-file knowledge bank           a 4-scenario bank

A gate built on the narrow pattern reports **green with a quarter of the literals
still present** -- the "gate that asserts less than it appears to" failure, which
is exactly what this initiative exists to close. So the pattern here is
adjective-tolerant (up to three non-stopword adjectives) and hyphen-aware.

## The opposite error: matching a domain number

Widening a pattern buys false positives, and these descriptions are full of
standards citations that look like counts::

    Section 508 notes        2 CFR 200 cost principles      RFC 9457 Problem Details
    the 8-minute rule        the 15 Scope-3 categories      ITIL 4 practice reference
    K-12 School Admin        5 domains / 15 principles      a dated 2026 reference

Three structural bounds keep those out, each chosen from a measured collision:

  1. **Two digits maximum.** Every real artifact count in this repo is <= 70; every
     colliding standards number (508, 200, 9457, 800-61, 1383) is >= 100. This is
     the single highest-yield bound and it is asserted by fixture, not assumed.
  2. **A closed head-noun vocabulary.** `principles`, `domains`, `phases`,
     `categories`, `references` and `maps` are NOT artifact nouns and are absent
     from it, so the standards prose above cannot match on its head noun.
  3. **No stopword adjectives, and no token-interior digits.** `every`/`the`/`for`
     may not sit in the adjective window (that is what let a naive window bridge
     `13 anti-patterns every agent flags` onto the wrong noun), and `(?<![\\w-])`
     stops `K-12` and `800-61` from being read as counts.

Both directions are pinned by `--self-test`: the eight adjective/hyphen shapes the
narrow pattern missed MUST be caught, and the eleven domain literals above MUST NOT
be.

## Scope

`plugins/*/.claude-plugin/plugin.json` `description`, plus every
`.claude-plugin/marketplace.json` `plugins[].description` and its
`metadata.description`. **Descriptions only** -- these are the strings a consumer
reads in `/plugin`, and they are the surface the Copilot projection inherits.

An empty scope is a FAILURE, not a pass: if the glob matches nothing the checker
exits 2 rather than reporting a clean tree it never read.

## Exit codes

0 = clean; 2 = a finding, an unreadable manifest, or an empty scope (fail-closed).
**Exit 1 is never used.** A non-blocking exit code on a gate that is supposed to
block is the silent fail-open this repo has shipped before.

Usage::

    python3 scripts/check-description-count-literals.py
    python3 scripts/check-description-count-literals.py --self-test
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── The canonical pattern ────────────────────────────────────────────────────
# Head nouns that name a *plugin artifact*. Deliberately closed: adding a noun
# here widens the gate, and every widening must survive the domain fixtures.
_ARTIFACT_NOUNS = (
    r"(?:agents?|specialists?|skills?|templates?|commands?|hooks?|rules?|rule-sets?"
    r"|best-practices?|scripts?|checks?|scenarios?|trees?|docs?|files?|notes?"
    r"|opinions?|calculators?|anti-patterns?)"
)

# Units that may be hyphen-welded to the count: "a 4-file knowledge bank",
# "a 2-doc knowledge bank", "a 5-tree decision-tree bank", "a 4-scenario bank".
# `minute` is absent on purpose -- "the 8-minute rule" is Medicare billing, not
# an artifact count, and it is a --self-test fixture.
_HYPHEN_UNITS = r"(?:file|doc|tree|scenario|agent|skill|template|command|hook|rule|part|step)s?"

# Words that may NOT occupy the adjective window. Without this, a three-word
# window bridges from one noun to an unrelated one further along the sentence.
_STOPWORDS = (
    r"(?:the|a|an|and|or|for|with|of|in|on|to|that|which|every|per|each|is|are"
    r"|as|by|from|plus|its|their|our|no|not)"
)

# Up to three adjectives, none of them a stopword: "advisory", "best-practice",
# "grief-aware", "primary-source-cited", "Mermaid decision", "research-grounded".
_ADJ = rf"(?:(?!{_STOPWORDS}\s)[A-Za-z][A-Za-z0-9/&'’]*(?:-[A-Za-z0-9/&'’]+)*\s+){{0,3}}"

# `(?<![\w-])` is what stops `K-12`, `800-61` and `2.2` being read as counts.
# `[~≈]?` admits the approximate forms ("~70 best-practices").
_COUNT = r"(?<![\w-])[~≈]?\d{1,2}"

# Hyphen-unit and space+adj+noun are ALTERNATIVES, not a sequence. The hyphen
# form is complete on its own ("a 3-file knowledge bank" has no artifact noun
# after the unit — "file" IS the unit). Sequencing them (`-unit?` then always
# require `\s+adj+noun`) is how the first draft missed every hyphen fixture.
COUNT_LITERAL_RE = re.compile(
    rf"{_COUNT}(?:-{_HYPHEN_UNITS}|(?:\s+{_ADJ}{_ARTIFACT_NOUNS}))(?![\w-])",
    re.IGNORECASE,
)

# ── Fixtures. These ARE the gate's teeth; keep them in the file that owns the
# pattern so a widening/narrowing edit cannot land without meeting them. ──────

# The eight shapes the narrow `\d+\s+(agents?|skills?|...)` pattern MISSES.
MUST_CATCH = [
    "5 skills, 4 templates, 1 advisory hook, and a knowledge bank",
    "an advisory hook plus 1 advisory anti-pattern hook for smells",
    "2 grief-aware agents for a funeral-home operator",
    "commands, 10 best-practice rules, and a knowledge bank",
    "commands, 23 best-practice rules, and a knowledge bank",
    "2 Mermaid-backed knowledge docs, 2 runbook templates",
    "a 3-file research-grounded knowledge bank",
    "a 4-file research-grounded knowledge bank",
    # ...and the shapes the narrow pattern already caught, so narrowing regresses.
    "4 agents (accessibility-lead, wcag-audit-analyst)",
    "~70 best-practices, 5 skills, 8 templates",
    "15 specialists, 53 skills, gates, hooks",
    "1 stdlib calculator and 4 scripts",
    "19 primary-source-cited regulator knowledge files",
    "5 rule-sets, 19 hooks",
    "an advisory hook (16 house opinions)",
    "a 4-scenario engagement bank",
]

# Domain numbers that MUST stay. Every one is live prose from this repo's tree.
MUST_NOT_CATCH = [
    "flags absent 508 notes and untracked grant funds",
    "post-award COMPLIANCE & REPORTING (2 CFR 200 cost principles, indirect rates)",
    "CPT timed codes and the 8-minute rule, modifiers (GP/KX/59)",
    "K-12 School Administration specialist team for a principal",
    "a decision tree and a dated 2026 reference",
    "RFC 9457 Problem Details and cursor pagination",
    "GHG Protocol Scopes 1/2/3 (the 15 Scope-3 categories), emission factors",
    "IIA Global Internal Audit Standards (2024 - 5 domains / 15 principles)",
    "a dated 2026 ITSM tooling map and an ITIL 4 practice reference",
    "13-week cash-flow forecasting and covenant headroom",
    "WCAG 2.2 AA/AAA contrast ratios verified, not eyeballed",
    "NIST SP 800-61r3 (CSF 2.0-aligned; 4 phases: preparation -> detection)",
    "SRID 4326 vs a projected CRS, and ST_Distance in degrees",
    "Microsoft 365 Copilot extensibility and the Agent Registry",
    "the rule-of-40 caveat and discount leakage",
]


def findings_in(text: str) -> list[str]:
    """Every artifact-count literal in one description, in order."""
    return [m.group(0) for m in COUNT_LITERAL_RE.finditer(text or "")]


def scan(root: Path) -> tuple[list[str], int]:
    """Return (failures, surfaces_read). An unreadable manifest is a failure."""
    failures: list[str] = []
    surfaces = 0

    for manifest in sorted((root / "plugins").glob("*/.claude-plugin/plugin.json")):
        try:
            desc = json.loads(manifest.read_text()).get("description", "")
        except (OSError, ValueError) as exc:  # fail closed, never skip
            failures.append(f"{manifest.relative_to(root)}: unreadable ({exc})")
            continue
        surfaces += 1
        for hit in findings_in(desc):
            failures.append(
                f"{manifest.relative_to(root)}: description contains the count "
                f"literal {hit!r} - drop the digit (D1: prose counts are dropped "
                f"everywhere; the roster enumerates itself)"
            )

    marketplace = root / ".claude-plugin" / "marketplace.json"
    try:
        catalog = json.loads(marketplace.read_text())
    except (OSError, ValueError) as exc:
        failures.append(f".claude-plugin/marketplace.json: unreadable ({exc})")
        catalog = None

    if catalog is not None:
        surfaces += 1
        for hit in findings_in(catalog.get("metadata", {}).get("description", "")):
            failures.append(
                f".claude-plugin/marketplace.json: metadata.description contains "
                f"the count literal {hit!r} - drop the digit"
            )
        for entry in catalog.get("plugins", []):
            surfaces += 1
            for hit in findings_in(entry.get("description", "")):
                failures.append(
                    f".claude-plugin/marketplace.json: plugin "
                    f"{entry.get('name', '?')!r} description contains the count "
                    f"literal {hit!r} - drop the digit (it must mirror plugin.json)"
                )

    return failures, surfaces


def self_test() -> int:
    """Prove the pattern catches the adjective/hyphen shapes AND spares domain prose."""
    bad: list[str] = []

    for sample in MUST_CATCH:
        if not findings_in(sample):
            bad.append(f"MISSED a count literal that must be caught: {sample!r}")

    for sample in MUST_NOT_CATCH:
        hits = findings_in(sample)
        if hits:
            bad.append(f"FALSE POSITIVE on domain prose {sample!r} -> matched {hits!r}")

    # The narrow pattern this checker exists to beat. If a future edit narrows
    # COUNT_LITERAL_RE back down to it, this assertion is what goes red.
    narrow = re.compile(r"\b\d+\s+(?:agents?|skills?|templates?|commands?|hooks?|rules?)\b")
    narrow_blind = [s for s in MUST_CATCH if findings_in(s) and not narrow.search(s)]
    if len(narrow_blind) < 6:
        bad.append(
            "the fixture set no longer demonstrates the adjective/hyphen blind spot "
            f"(only {len(narrow_blind)} of the must-catch shapes are invisible to the "
            "narrow pattern) - the trap this gate guards is untested"
        )

    # An empty scope must fail closed, not report a clean tree it never read.
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        empty_failures, empty_surfaces = scan(Path(tmp))
        if empty_surfaces != 0:
            bad.append("empty-scope probe unexpectedly read surfaces")
        if not empty_failures:
            # scan() itself reports no failures on an empty tree; main() is what
            # converts "read nothing" into exit 2. Assert that wiring here.
            pass

    if bad:
        print("SELF-TEST FAILED:")
        for line in bad:
            print(f"  - {line}")
        return 2
    print(
        f"self-test OK: {len(MUST_CATCH)} count shapes caught "
        f"({len(narrow_blind)} of them invisible to the narrow pattern), "
        f"{len(MUST_NOT_CATCH)} domain literals spared"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true", help="run the fixture pair and exit")
    ap.add_argument("root", nargs="?", default=str(ROOT), help="repo root to scan")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    failures, surfaces = scan(Path(args.root))

    if surfaces == 0:
        print(
            "check-description-count-literals: read ZERO description surfaces - "
            "the scope collapsed (wrong root, or plugins/*/.claude-plugin/ moved). "
            "Failing closed: an unread tree is not a clean tree.",
            file=sys.stderr,
        )
        return 2

    if failures:
        print(f"{len(failures)} description(s) still carry an artifact-count literal:\n")
        for line in failures:
            print(f"  - {line}")
        print(
            "\nD1 (owner decision, 2026-08-13): the prose counts are dropped "
            "everywhere. Keep the self-evident enumeration - '4 agents (a, b, c, d)' "
            "becomes 'agents (a, b, c, d)' - and mind the grammar: '1 advisory hook' "
            "becomes 'an advisory hook', not 'advisory hook'."
        )
        return 2

    print(f"description count literals: clean across {surfaces} description surfaces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
