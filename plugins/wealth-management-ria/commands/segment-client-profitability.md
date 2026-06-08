---
description: "Segment clients by revenue net of cost-to-serve and find breakeven AUM — not AUM alone. Reach for this on a client-value question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Segment client profitability

You are running `/wealth-management-ria:segment-client-profitability` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Pull revenue per client — Effective fee × AUM per client.
2. Estimate cost-to-serve — Service intensity by client/segment.
3. Compute margin and breakeven — Revenue − cost; breakeven AUM via `riaops_calc.py client-profitability` (§3 #2).
4. Re-segment — Rank by profit, not AUM; act on the unprofitable tail (§3 #2).

## Output
A profitability segmentation with breakeven AUM. Traverse Tree 2 in the decision-trees file. See [`../skills/segment-client-profitability/SKILL.md`](../skills/segment-client-profitability/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client financial PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
