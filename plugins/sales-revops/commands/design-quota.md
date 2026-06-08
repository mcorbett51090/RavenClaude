---
description: "Design quota to ramped-rep capacity and read the attainment distribution it implies. Reach for this on a quota or territory question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Design quota

You are running `/sales-revops:design-quota` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Size capacity — Ramped reps × productivity/rep × ramp factor.
2. Fit quota under capacity — Quota must be achievable by the median rep via `revops_calc.py quota-capacity` (§3 #4).
3. Read the distribution — P25/P50/P75 attainment a quota implies; a low median is a design error.
4. Check territory balance — TAM and account quality, separating design from performance (§3 #7).

## Output
A capacity-tied quota with its attainment distribution and the over-set segments flagged. See [`../skills/design-quota/SKILL.md`](../skills/design-quota/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer/rep PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
