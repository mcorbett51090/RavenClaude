---
name: size-advisor-capacity
description: "Size advisor capacity in households per advisor and treat over-capacity as a leading retention risk. Reach for this on a capacity question."
---

# Skill: Size advisor capacity

Over-capacity degrades service, which surfaces later as attrition (§3 #4 #5).

## Step 1 — Count households per advisor
Households ÷ advisors (§3 #4).

## Step 2 — Compare to target band
Against a defensible households-per-advisor band via `riaops_calc.py advisor-capacity`.

## Step 3 — Read the retention risk
Over-capacity is a leading attrition indicator (§3 #4 #5).

## Step 4 — Tie to review cadence
Capacity must allow the compliance review cadence (§3 #6).

## Output
A households-per-advisor capacity read flagged as retention risk. Traverse Tree 3 in the decision-trees file.
