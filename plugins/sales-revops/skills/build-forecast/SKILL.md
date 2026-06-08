---
name: build-forecast
description: "Build a stage-weighted, aged forecast with coverage — surface the at-risk deals. Reach for this on a forecast question."
---

# Skill: Build forecast

A forecast that sums rep commits over-forecasts (§3 #2).

## Step 1 — Pull the pipeline
Open deals by stage, value, close-date, and age.

## Step 2 — Weight by stage win-rate
Σ(value × historical stage win-rate); a commit is an input, not the model (§3 #2).

## Step 3 — Age and haircut
Flag deals past expected close or beyond stage-normal dwell; apply a slip haircut (§3 #6).

## Step 4 — Compare to coverage
Open pipeline ÷ remaining quota vs target ratio via `revops_calc.py coverage` (§3 #1).

## Output
A stage-weighted, aged forecast with the coverage ratio and at-risk deals named. Traverse Tree 1 in the decision-trees file.
