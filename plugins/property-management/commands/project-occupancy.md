---
description: "Project ending occupancy as a flow of move-ins, move-outs, and renewals against a target. Reach for this on an occupancy question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Project occupancy

You are running `/property-management:project-occupancy` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set the unit count and start — Total units and units occupied at period start.
2. Net the flow — Move-ins minus move-outs, plus renewals via `property_management_calc.py occupancy-rev` (§3 #1).
3. Compute ending occupancy and revenue — Ending occupied ÷ total units × avg rent.
4. Name the gap to target — Units short of the target occupancy and the lease-up need.

## Output
An ending-occupancy projection with the gap to target named. See [`../skills/project-occupancy/SKILL.md`](../skills/project-occupancy/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No tenant PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
