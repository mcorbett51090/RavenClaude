---
name: model-payer-mix
description: "Read reimbursement net of variable cost by payer, compute blended margin, and model a mix shift — flagging parity for counsel. Reach for this on a payer or margin question."
---

# Skill: Model payer mix and margin

A blended reimbursement number hides which payers drag margin (§3 #5).

## Step 1 — Pull per-payer data
Visit volume, reimbursement, and variable cost per visit by payer.

## Step 2 — Compute blended margin
Blended reimbursement and margin via `behavioral_health_practice_calc.py payer-mix` (§3 #5).

## Step 3 — Model the shift
New blend vs current blend → mix-shift delta, with capacity caveats (§3 #4 #5).

## Step 4 — Flag parity
Parity gaps where behavioral-health rates lag — route the determination to counsel (§3 #5 #8).

## Output
A per-payer margin read with the blended figure, mix-shift delta, and parity flagged to counsel.
