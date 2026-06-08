---
name: flag-chronic-absenteeism
description: "Compute the chronic-absentee rate, flag it early, and size the attendance-recovery funding upside. Reach for this on an attendance question."
---

# Skill: Flag chronic absenteeism

A year-end absenteeism count is a post-mortem; flag early to act (§3 #5).

## Step 1 — Define the threshold
Students at/over the chronic-absence threshold (source + date the definition, §3 #5 #8).

## Step 2 — Compute the rate
At/over-threshold ÷ enrolled via `k12_school_administration_calc.py absenteeism` (§3 #5).

## Step 3 — Flag against a trigger
Raise the early-warning flag, not at year-end (§3 #5).

## Step 4 — Size the recovery upside
The funding recoverable by lifting attendance (§3 #2).

## Output
A chronic-absentee read with the early-warning flag and recovery funding upside. Traverse Tree 3 in the decision-trees file.
