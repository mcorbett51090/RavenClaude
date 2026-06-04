---
description: "Value a battery on its dispatch use-case — arbitrage, demand-charge reduction, capacity — not a flat $/kWh. Reach for this on a storage add."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Value storage by dispatch

You are running `/renewable-energy:value-storage-by-dispatch` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Define the use-case — Arbitrage, demand-charge reduction, backup, or capacity (§3 #7).
2. Model the dispatch — Value the battery's operation against the tariff/market.
3. Net against cost — Compare the dispatch value to the storage cost and incentive.
4. Recommend the sizing — Size the battery to the highest-value dispatch.

## Output
A use-case, a dispatch-value model, a cost comparison, and a sizing recommendation. See [`../skills/value-storage-dispatch/SKILL.md`](../skills/value-storage-dispatch/SKILL.md). Traverse the matching tree in [`../knowledge/renewables-decision-trees.md`](../knowledge/renewables-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
