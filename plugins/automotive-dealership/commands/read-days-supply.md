---
description: "Read inventory days-supply against a target and quantify floorplan carrying cost. Reach for this on an inventory question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read days-supply

You are running `/automotive-dealership:read-days-supply` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set the sales rate — Units in stock and the average daily sales rate.
2. Compute days-supply — Units ÷ daily sales rate via `automotive_dealership_calc.py days-supply` (§3 #2).
3. Cost the floorplan — Units × per-unit daily carry → monthly carrying cost.
4. Flag the aged units — Price-to-turn the units past target days-supply (§3 #2).

## Output
A days-supply read vs target with the floorplan carrying cost quantified. Traverse Tree 1 in the decision-trees file. See [`../skills/read-days-supply/SKILL.md`](../skills/read-days-supply/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
