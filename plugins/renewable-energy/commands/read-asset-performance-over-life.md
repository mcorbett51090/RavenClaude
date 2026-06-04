---
description: "Read availability, degradation, and O&M cost over the 25-year asset life so the IRR rests on real operations. Reach for this on an operating-asset question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read asset performance over life

You are running `/renewable-energy:read-asset-performance-over-life` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure availability and yield — Actual vs P50/P90 expected production (§3 #6).
2. Track degradation — Module degradation and inverter health over time (§3 #5).
3. Read O&M cost — O&M and replacement cost against the pro-forma.
4. Reforecast the IRR — Update the return with realized performance.

## Output
An availability/yield read, a degradation track, an O&M-vs-pro-forma view, and a reforecast IRR. See [`../skills/read-asset-performance/SKILL.md`](../skills/read-asset-performance/SKILL.md). Traverse the matching tree in [`../knowledge/renewables-decision-trees.md`](../knowledge/renewables-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
