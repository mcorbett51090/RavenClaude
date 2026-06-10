---
name: size-cycle-capacity
description: "Measure app-to-close cycle, find the bottleneck stage, and size processor/LO capacity as a function of cycle — staff to the cycle, not a ratio. Reach for this on a cycle or staffing question."
---

# Skill: Size cycle and capacity

A fixed loans-per-processor ratio untied to cycle mis-staffs (§3 #4).

## Step 1 — Measure the cycle
App-to-close days and dwell by stage.

## Step 2 — Find the bottleneck
The stage whose dwell dominates the cycle (§3 #2).

## Step 3 — Compute capacity
Processors × loans-per-processor-at-cycle via `mortgage_lending_calc.py cycle-capacity` (§3 #4).

## Step 4 — Plan for the swing
Staff to the rate-cycle breakeven, not the peak (§3 #7).

## Output
A cycle/capacity read with the bottleneck stage and staffing gap named. Traverse Tree 2 in the decision-trees file.
