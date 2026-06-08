---
name: compute-total-gross
description: "Compute total gross per unit as front plus F&I back, with penetration. Reach for this on a deal-profitability question."
---

# Skill: Compute total gross

Front gross alone understates deal profitability (§3 #3).

## Step 1 — Set front and back
Front (vehicle) gross and F&I back-end gross per the period.

## Step 2 — Combine per unit
(front + back) × units, then per-unit, via `automotive_dealership_calc.py gross-per-unit` (§3 #3).

## Step 3 — Derive F&I penetration
Back-end gross relative to units retailed (PVR) (§3 #4).

## Step 4 — Separate deal quality
A thin-front/strong-back deal vs a fat-front/no-back one (§3 #3).

## Output
A total-gross read per unit with F&I penetration and deal-quality separation.
