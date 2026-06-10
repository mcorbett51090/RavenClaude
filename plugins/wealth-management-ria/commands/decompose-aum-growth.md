---
description: "Separate AUM growth into net new flows vs market and compute the organic growth rate. Reach for this on a growth question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Decompose AUM growth

You are running `/wealth-management-ria:decompose-aum-growth` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set the AUM bridge — Beginning AUM, ending AUM, net new flows, withdrawals.
2. Separate flows from market — AUM growth − net new flows = market via `riaops_calc.py aum-revenue` (§3 #1).
3. Compute organic growth — Net new flows ÷ beginning AUM — the real health metric (§3 #7).
4. Read it against market — Strip market; organic growth is what survives a drawdown (§3 #7).

## Output
An AUM bridge separating net-new-vs-market with the organic growth rate. Traverse Tree 1 in the decision-trees file. See [`../skills/decompose-aum-growth/SKILL.md`](../skills/decompose-aum-growth/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client financial PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
