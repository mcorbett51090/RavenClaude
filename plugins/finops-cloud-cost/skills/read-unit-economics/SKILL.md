---
name: read-unit-economics
description: "Compute cost per customer/transaction/feature and read the trend, not the gross bill. Reach for this on a scaling-health question."
---

# Skill: Read unit economics

A rising total bill can be healthy or decay — only the unit cost says which (§3 #2).

## Step 1 — Pick the unit
Customers, transactions, or features — the denominator that matters to the business.

## Step 2 — Compute cost-per-unit
Allocated cost ÷ units via `finops_cloud_cost_calc.py unit-cost` (§3 #2).

## Step 3 — Read the trend
Rising bill + falling unit cost = healthy; flat bill + rising unit cost = decay (§3 #2).

## Step 4 — Attribute the driver
Which service moves the unit cost, on allocated (not gross) spend (§3 #1).

## Output
A cost-per-unit read with the trend and the driving service named. Traverse Tree 2 in the decision-trees file.
