---
name: model-fee-revenue
description: "Model tiered-fee revenue and the blended fee, flagging inconsistent application. Reach for this on a fee or revenue question."
---

# Skill: Model fee revenue

Ad-hoc fee exceptions leak revenue and create disclosure risk (§3 #3).

## Step 1 — Lay out the schedule
Tiered breakpoints and the fee at each tier.

## Step 2 — Compute revenue
Σ(tier AUM × tier fee) via `riaops_calc.py aum-revenue` (§3 #3).

## Step 3 — Compute the blended fee
Revenue ÷ total AUM.

## Step 4 — Flag exceptions
Inconsistent breakpoints or off-schedule fees route to compliance (§3 #3 #6).

## Output
A tiered-fee revenue model and blended fee with exceptions flagged.
