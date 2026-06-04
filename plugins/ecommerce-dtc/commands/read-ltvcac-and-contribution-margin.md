---
description: "Read LTV:CAC against the 3:1 line and contribution margin after the real costs, so a profitability problem is diagnosed correctly. Reach for this on any growth/profit question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read LTV:CAC and contribution margin

You are running `/ecommerce-dtc:read-ltvcac-and-contribution-margin` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Compute CAC by channel — Acquisition spend ÷ new customers, by channel (avg ~$45–$70) (§3 #5).
2. Compute LTV by cohort — Realized lifetime value per cohort, not a projection.
3. Read the ratio — LTV:CAC against 3:1 (below 2:1 is urgent) (§3 #1).
4. Net to contribution margin — Revenue minus COGS, CAC, shipping, returns (§3 #2, #6).

## Output
A by-channel CAC, a cohort LTV, the LTV:CAC ratio, and contribution margin after real costs. See [`../skills/read-ltv-cac/SKILL.md`](../skills/read-ltv-cac/SKILL.md). Traverse the matching tree in [`../knowledge/ecommerce-decision-trees.md`](../knowledge/ecommerce-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
