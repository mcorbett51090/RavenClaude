---
description: "Read driver turnover as a quantified unit-economics cost across recruiting, training, and unseated trucks. Reach for this when turnover is high."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Quantify driver retention cost

You are running `/fleet-logistics:quantify-driver-retention-cost` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure turnover — Annualized turnover, benchmarked (often 90%+ at large TL) (§3 #4).
2. Cost a replacement — Recruiting + training + unseated-truck revenue loss per driver.
3. Find the cause — Pay, home time, equipment, or dispatch treatment.
4. Model the retention ROI — Compare a retention investment to the replacement cost.

## Output
A turnover rate, a per-driver replacement cost, the cause, and the retention ROI. See [`../skills/quantify-driver-retention/SKILL.md`](../skills/quantify-driver-retention/SKILL.md). Traverse the matching tree in [`../knowledge/fleet-decision-trees.md`](../knowledge/fleet-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
