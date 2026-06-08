---
description: "Model RI/Savings-Plan coverage on the rightsized baseline, balancing discount vs utilization risk. Reach for this on a commitment question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Plan commitments

You are running `/finops-cloud-cost:plan-commitments` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Rightsize first — Current vs utilization-implied size via `finops_cloud_cost_calc.py rightsizing` (§3 #4).
2. Set the lean baseline — Commit against the rightsized, waste-free baseline only (§3 #4 #5).
3. Model coverage — Blended cost + savings + utilization risk via `finops_cloud_cost_calc.py commitment` (§3 #3).
4. Pick coverage, not max — Balance discount against the risk of unused locked-in capacity (§3 #3).

## Output
A commitment-coverage model on the lean baseline with the utilization risk named. Traverse Tree 3 in the decision-trees file. See [`../skills/plan-commitments/SKILL.md`](../skills/plan-commitments/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No billing/account PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
