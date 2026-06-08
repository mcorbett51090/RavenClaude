---
name: segment-client-profitability
description: "Segment clients by revenue net of cost-to-serve and find breakeven AUM — not AUM alone. Reach for this on a client-value question."
---

# Skill: Segment client profitability

AUM rank and profitability rank are different lists (§3 #2).

## Step 1 — Pull revenue per client
Effective fee × AUM per client.

## Step 2 — Estimate cost-to-serve
Service intensity by client/segment.

## Step 3 — Compute margin and breakeven
Revenue − cost; breakeven AUM via `riaops_calc.py client-profitability` (§3 #2).

## Step 4 — Re-segment
Rank by profit, not AUM; act on the unprofitable tail (§3 #2).

## Output
A profitability segmentation with breakeven AUM. Traverse Tree 2 in the decision-trees file.
