---
name: size-demand
description: "Back-solve the lead volume a win target requires through each stage conversion. Reach for this on a 'how many leads' question."
---

# Skill: Size demand

A lead target set without the downstream conversion math is a guess (§3 #1).

## Step 1 — Set the win target
Target closed-won deals for the period and segment.

## Step 2 — Pull stage conversion
Lead→MQL→SQL→opp→win rates from clean trailing data (§3 #7).

## Step 3 — Back-solve volume
Required leads = target wins ÷ product of stage rates via `marketingops_calc.py funnel`.

## Step 4 — Check the leak first
If a stage leaks, fix it before scaling volume (§3 #1).

## Output
A required-lead model with the leaking stage flagged.
