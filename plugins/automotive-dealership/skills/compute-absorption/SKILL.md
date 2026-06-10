---
name: compute-absorption
description: "Compute the service absorption rate against total fixed overhead — the survival metric. Reach for this on a fixed-ops question."
---

# Skill: Compute absorption

A store below absorption is structurally fragile regardless of sales volume (§3 #5).

## Step 1 — Total fixed-ops gross
Service + parts gross profit for the period.

## Step 2 — Total fixed overhead
The store's total fixed expense to cover.

## Step 3 — Compute absorption
Fixed-ops gross ÷ total fixed overhead via `automotive_dealership_calc.py absorption` (§3 #5).

## Step 4 — Flag the position
At/above 100% the store self-covers; below is fragility (§3 #1 #5).

## Output
An absorption read with the over/under-100% flag. Traverse Tree 2 in the decision-trees file.
