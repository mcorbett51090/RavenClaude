---
description: "Compute the service absorption rate against total fixed overhead — the survival metric. Reach for this on a fixed-ops question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Compute absorption

You are running `/automotive-dealership:compute-absorption` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Total fixed-ops gross — Service + parts gross profit for the period.
2. Total fixed overhead — The store's total fixed expense to cover.
3. Compute absorption — Fixed-ops gross ÷ total fixed overhead via `automotive_dealership_calc.py absorption` (§3 #5).
4. Flag the position — At/above 100% the store self-covers; below is fragility (§3 #1 #5).

## Output
An absorption read with the over/under-100% flag. Traverse Tree 2 in the decision-trees file. See [`../skills/compute-absorption/SKILL.md`](../skills/compute-absorption/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
