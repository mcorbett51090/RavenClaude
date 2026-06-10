---
description: "Model self-service/KB deflection and the cost avoided before sizing headcount. Reach for this first on a cost-to-serve question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Model deflection

You are running `/customer-support-cx-operations:model-deflection` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Cluster contact drivers — Group tickets by reason; the top drivers are deflection targets (§3 #1).
2. Estimate deflectable share — Which drivers self-service can actually handle — measured, not assumed.
3. Compute savings — Deflection-rate × volume × cost-per-contact via `supportops_calc.py deflection` (§3 #1).
4. Compare to hiring — Recurring deflection savings vs the cost a hire adds (§3 #1).

## Output
A deflection model with cost avoided and deflectable drivers named. Traverse Tree 1 in the decision-trees file. See [`../skills/model-deflection/SKILL.md`](../skills/model-deflection/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
