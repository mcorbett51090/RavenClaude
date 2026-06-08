---
name: model-cost-to-originate
description: "Compute cost-to-originate (fixed + variable per loan) and the breakeven volume that the rate swing must clear. Reach for this on a unit-economics question."
---

# Skill: Model cost-to-originate

A shop that doesn't know its cost-to-originate dies in the downturn (§3 #5).

## Step 1 — Split the cost
Fixed cost and variable cost per loan.

## Step 2 — Compute cost-to-originate
(fixed + variable × loans) ÷ loans via `mortgage_lending_calc.py cost-to-originate` (§3 #5).

## Step 3 — Find the breakeven
Fixed cost ÷ margin-per-loan = breakeven volume (§3 #5).

## Step 4 — Stress the rate swing
Compare breakeven to a downturn volume projection (§3 #7).

## Output
A cost-to-originate and breakeven read stressed against the rate-cycle volume swing.
