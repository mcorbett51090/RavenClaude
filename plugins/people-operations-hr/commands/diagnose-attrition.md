---
description: "Diagnose an attrition spike with cost and cause — split regretted from non-regretted, localize to team/manager, price the loss, name the driver. Reach for this on a retention question."
argument-hint: "[the situation, e.g. the segment / cohort / period in question]"
---

# Diagnose attrition

You are running `/people-operations-hr:diagnose-attrition` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Split regretted vs non-regretted — only the regretted share is a loss to recover (§3 #1).
2. Localize it — segment by team / manager / level / tenure cohort (§3 #7).
3. Name the driver — comp / manager / growth / workload; usually two co-occur.
4. Cost it — regretted exits × replacement cost via `scripts/people_calc.py attrition`.

## Output
A regretted-split, segmented, dollar-costed attrition read with a named driver. See [`../skills/diagnose-attrition/SKILL.md`](../skills/diagnose-attrition/SKILL.md). Traverse Tree 1 in [`../knowledge/people-ops-decision-trees.md`](../knowledge/people-ops-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No employee PII in the output; cite a source + date for every external benchmark (or mark it).
- End with owner / date / expected movement on each recommendation.
