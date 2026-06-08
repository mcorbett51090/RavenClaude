---
description: "Compute total gross per unit as front plus F&I back, with penetration. Reach for this on a deal-profitability question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Compute total gross

You are running `/automotive-dealership:compute-total-gross` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set front and back — Front (vehicle) gross and F&I back-end gross per the period.
2. Combine per unit — (front + back) × units, then per-unit, via `automotive_dealership_calc.py gross-per-unit` (§3 #3).
3. Derive F&I penetration — Back-end gross relative to units retailed (PVR) (§3 #4).
4. Separate deal quality — A thin-front/strong-back deal vs a fat-front/no-back one (§3 #3).

## Output
A total-gross read per unit with F&I penetration and deal-quality separation. See [`../skills/compute-total-gross/SKILL.md`](../skills/compute-total-gross/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
