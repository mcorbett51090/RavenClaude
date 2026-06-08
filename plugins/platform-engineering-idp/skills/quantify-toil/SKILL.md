---
name: quantify-toil
description: "Quantify manual toil and the automation ROI in engineer-hours per year. Reach for this on an automate-or-not question."
---

# Skill: Quantify toil

Every recurring ticket is platform debt with a measurable cost (§3 #4).

## Step 1 — Inventory the task
Manual minutes per occurrence, frequency, and engineers affected.

## Step 2 — Compute hours/yr
minutes × frequency × engineers ÷ 60 via `platform_engineering_idp_calc.py toil` (§3 #4).

## Step 3 — Compare to build cost
Hours/yr saved vs the build-and-maintain cost of the self-service action.

## Step 4 — Rank against adoption
Prioritize toil on high-adoption paths, not rare edge cases (§3 #7).

## Output
A toil ROI read in engineer-hours/yr with the build-vs-buy-vs-leave call.
