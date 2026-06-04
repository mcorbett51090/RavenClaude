---
description: "Read return rate and its full cost as a contribution-margin line, so a high-return category isn't mistaken for a winner. Reach for this on a margin question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Cost the returns

You are running `/ecommerce-dtc:cost-the-returns` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure return rate by category — Returns ÷ orders, by product/category (§3 #6).
2. Cost the return — Restocking, return shipping, and write-off per return.
3. Net to margin — Subtract return cost from category contribution margin.
4. Act on the category — Fix sizing/expectations or reprice the high-return category.

## Output
A return-rate read by category, the full return cost, net margin, and a category action. See [`../skills/cost-the-returns/SKILL.md`](../skills/cost-the-returns/SKILL.md). Traverse the matching tree in [`../knowledge/ecommerce-decision-trees.md`](../knowledge/ecommerce-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
