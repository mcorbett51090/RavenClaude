---
description: "Compute cost per customer/transaction/feature and read the trend, not the gross bill. Reach for this on a scaling-health question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read unit economics

You are running `/finops-cloud-cost:read-unit-economics` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Pick the unit — Customers, transactions, or features — the denominator that matters to the business.
2. Compute cost-per-unit — Allocated cost ÷ units via `finops_cloud_cost_calc.py unit-cost` (§3 #2).
3. Read the trend — Rising bill + falling unit cost = healthy; flat bill + rising unit cost = decay (§3 #2).
4. Attribute the driver — Which service moves the unit cost, on allocated (not gross) spend (§3 #1).

## Output
A cost-per-unit read with the trend and the driving service named. Traverse Tree 2 in the decision-trees file. See [`../skills/read-unit-economics/SKILL.md`](../skills/read-unit-economics/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No billing/account PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
