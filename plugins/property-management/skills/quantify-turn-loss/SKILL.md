---
name: quantify-turn-loss
description: "Quantify lost rent during unit turns and frame the work-order backlog as a retention risk. Reach for this on a turn or maintenance question."
---

# Skill: Quantify turn loss

Slow turns are lost rent and a satisfaction signal, not just a cost (§3 #3).

## Step 1 — Count vacant units and turn days
Vacant units awaiting turn and average turn days.

## Step 2 — Compute lost rent
Vacant units × turn days × daily rent via `property_management_calc.py turn-time` (§3 #3).

## Step 3 — Annualize the drag
Scale the per-turn loss to an annual run-rate.

## Step 4 — Frame the backlog risk
Read the work-order backlog age as a renewal risk (§3 #6).

## Output
A lost-rent read annualized with the backlog framed as retention risk.
