---
name: plan-commitments
description: "Model RI/Savings-Plan coverage on the rightsized baseline, balancing discount vs utilization risk. Reach for this on a commitment question."
---

# Skill: Plan commitments

Never commit on an un-rightsized baseline — it locks in waste (§3 #4).

## Step 1 — Rightsize first
Current vs utilization-implied size via `finops_cloud_cost_calc.py rightsizing` (§3 #4).

## Step 2 — Set the lean baseline
Commit against the rightsized, waste-free baseline only (§3 #4 #5).

## Step 3 — Model coverage
Blended cost + savings + utilization risk via `finops_cloud_cost_calc.py commitment` (§3 #3).

## Step 4 — Pick coverage, not max
Balance discount against the risk of unused locked-in capacity (§3 #3).

## Output
A commitment-coverage model on the lean baseline with the utilization risk named. Traverse Tree 3 in the decision-trees file.
