---
description: "Size agents from workload and a target occupancy band — not a fixed agent:ticket ratio. Reach for this on a staffing question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Size staffing

You are running `/customer-support-cx-operations:size-staffing` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Forecast volume by interval — Contacts per interval and handle time (AHT).
2. Compute workload hours — Contacts × AHT per interval.
3. Staff to occupancy — Agents = workload ÷ (interval hours × target occupancy) via `supportops_calc.py staffing` (§3 #2).
4. Sanity-check the band — Occupancy too high burns out; too low wastes cost (§3 #2).

## Output
A workload/occupancy staffing model with the target band stated. See [`../skills/size-staffing/SKILL.md`](../skills/size-staffing/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
