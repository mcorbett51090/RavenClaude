---
description: "Size advisor capacity in households per advisor and treat over-capacity as a leading retention risk. Reach for this on a capacity question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Size advisor capacity

You are running `/wealth-management-ria:size-advisor-capacity` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Count households per advisor — Households ÷ advisors (§3 #4).
2. Compare to target band — Against a defensible households-per-advisor band via `riaops_calc.py advisor-capacity`.
3. Read the retention risk — Over-capacity is a leading attrition indicator (§3 #4 #5).
4. Tie to review cadence — Capacity must allow the compliance review cadence (§3 #6).

## Output
A households-per-advisor capacity read flagged as retention risk. Traverse Tree 3 in the decision-trees file. See [`../skills/size-advisor-capacity/SKILL.md`](../skills/size-advisor-capacity/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client financial PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
