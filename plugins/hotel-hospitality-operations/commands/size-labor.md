---
description: "Size labor to the occupancy forecast by hours-per-occupied-room and protect flow-through. Reach for this on a labor question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Size labor

You are running `/hotel-hospitality-operations:size-labor` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set occupied rooms — Forecast occupied rooms for the period.
2. Apply the labor standard — Occupied rooms × target hours-per-occupied-room via `hotel_hospitality_operations_calc.py labor` (§3 #4).
3. Compute cost per occupied room — Labor cost ÷ occupied rooms — the productivity number.
4. Protect flow-through — Balance the cut against GOPPAR and service level (§3 #4 #5).

## Output
A labor-hours and cost-per-occupied-room read flexed to the forecast. Traverse Tree 2 in the decision-trees file. See [`../skills/size-labor/SKILL.md`](../skills/size-labor/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No guest PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
