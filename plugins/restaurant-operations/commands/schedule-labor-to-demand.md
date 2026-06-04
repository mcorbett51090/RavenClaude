---
description: "Build a labor plan to forecast demand by daypart that holds the service line, so a labor cut doesn't cost more than it saves. Reach for this on a labor problem."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Schedule labor to demand

You are running `/restaurant-operations:schedule-labor-to-demand` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Forecast demand by daypart — Build a covers/sales forecast per daypart from history.
2. Set labor to the ratio — Target labor % per daypart against the forecast (§3 #4).
3. Hold the service line — Identify the staffing floor below which speed-of-service and turnover costs exceed the savings.
4. Stress the cut — Show what a requested cut does to the service line before committing.

## Output
A daypart labor plan, the service-line floor, and the cost of an over-cut. See [`../skills/schedule-to-demand/SKILL.md`](../skills/schedule-to-demand/SKILL.md). Traverse the matching tree in [`../knowledge/restaurant-decision-trees.md`](../knowledge/restaurant-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
