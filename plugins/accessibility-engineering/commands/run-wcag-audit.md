---
description: "Audit a page set against a named WCAG version and level, classify issues by severity/level, and compute a weighted conformance score. Reach for this on a conformance question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Run WCAG audit

You are running `/accessibility-engineering:run-wcag-audit` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Name the target — WCAG version + level (A/AA/AAA) and the page set in scope — conformance is per-criterion at the target level (§3 #1).
2. Scan, then test by hand — Run the automated scan as a first pass, then manually check the human-judgment criteria it cannot detect (§3 #2).
3. Classify each issue — By severity and WCAG level; one failing Level-A criterion fails the page (§3 #2).
4. Score conformance — Weighted score + critical-blocker flag via `accessibility_calc.py conformance` (§3 #1).

## Output
A criterion-level audit with severity/level classification, critical blockers, and a weighted conformance score. Traverse Tree 1 in the decision-trees file. See [`../skills/run-wcag-audit/SKILL.md`](../skills/run-wcag-audit/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No user PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
