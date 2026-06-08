---
name: read-cac-ltv
description: "Read LTV:CAC and CAC-payback to gate acquisition spend on unit economics, not lead count. Reach for this on a CAC or sustainability question."
---

# Skill: Read CAC and LTV

Cheap leads that never convert are expensive (§3 #3).

## Step 1 — Compute fully-loaded CAC
All acquisition cost ÷ customers acquired.

## Step 2 — Compute LTV
Gross-margin lifetime value per customer.

## Step 3 — Ratio and payback
LTV:CAC and CAC ÷ monthly margin contribution via `marketingops_calc.py cac-ltv` (§3 #3).

## Step 4 — Gate the spend
Compare to a dated health frame; mark benchmarks unverified (§3 #8).

## Output
An LTV:CAC and payback read gating spend, with benchmarks dated. Traverse Tree 2 in the decision-trees file.
