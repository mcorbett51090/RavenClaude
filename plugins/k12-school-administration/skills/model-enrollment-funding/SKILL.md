---
name: model-enrollment-funding
description: "Translate enrollment and ADA into funding and quantify the dollar value of each attendance point. Reach for this on a funding question."
---

# Skill: Model enrollment funding

Per-pupil funding means enrollment and ADA are dollars, not just a headcount (§3 #1 #2).

## Step 1 — Set enrollment and per-pupil
Enrollment count and the per-pupil funding rate (source + date it, §3 #8).

## Step 2 — Apply the ADA rate
Funding scaled by average daily attendance via `k12_school_administration_calc.py enrollment-funding` (§3 #2).

## Step 3 — Value an attendance point
The dollar value of each ADA point — the dual lever (§3 #2).

## Step 4 — Frame the retention flow
Mid-year attrition that erodes the funded base (§3 #1).

## Output
An enrollment-to-funding read with the per-attendance-point dollar value named. Traverse Tree 1 in the decision-trees file.
