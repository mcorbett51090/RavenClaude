---
description: "Trace coding denials to documentation, code selection, or modifier use as decision-support, never to up-coding. Reach for this when coding denials rise."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read coding-driven denials

You are running `/medical-revenue-cycle:read-coding-driven-denials` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Isolate coding denials — Separate coding/documentation denials from eligibility/auth (§3 #5).
2. Trace the cause — Documentation gap, wrong code level, or modifier — as coder decision-support (§3 #7).
3. Fix the documentation — Prescribe the documentation/template change, not an up-code (§3 #7).
4. Re-measure — Track the coding-denial rate after the fix.

## Output
A coding-denial root-cause trace, a documentation fix, and the before/after — never up-coding. See [`../skills/read-coding-denials/SKILL.md`](../skills/read-coding-denials/SKILL.md). Traverse the matching tree in [`../knowledge/rcm-decision-trees.md`](../knowledge/rcm-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
