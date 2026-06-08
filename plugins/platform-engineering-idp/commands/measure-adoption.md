---
description: "Read adoption as teams-on-golden-path ÷ total, name the gap, and segment the un-adopted teams. Reach for this on an adoption question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Measure adoption

You are running `/platform-engineering-idp:measure-adoption` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Define on-path — What counts as a team being on the golden path — concrete, not aspirational.
2. Compute the ratio — Teams on path ÷ total via `platform_engineering_idp_calc.py adoption` (§3 #7).
3. Name the gap — The un-adopted teams are the backlog; segment them by why.
4. Tie to friction — Route each gap cluster to a golden-path friction or a missing capability (§3 #2).

## Output
An adoption ratio with the gap named and the un-adopted teams segmented. See [`../skills/measure-adoption/SKILL.md`](../skills/measure-adoption/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No internal credentials/PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
