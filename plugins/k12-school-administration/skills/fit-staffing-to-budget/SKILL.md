---
name: fit-staffing-to-budget
description: "Model a student:teacher ratio into FTE and salary cost and check it against the budget envelope. Reach for this on a staffing question."
---

# Skill: Fit staffing to budget

A staffing ratio set as an aspiration untied to the budget sets the school up to overspend (§3 #3).

## Step 1 — Set the target ratio
The student:teacher ratio and current FTE.

## Step 2 — Compute teachers and cost
Enrollment ÷ ratio × avg teacher cost via `k12_school_administration_calc.py staffing-ratio` (§3 #3).

## Step 3 — Check the variance
FTE and dollar variance vs current and vs the budget envelope (§3 #3).

## Step 4 — Tie to retention
Turnover cost that the ratio decision interacts with (§3 #7).

## Output
A staffing-to-budget read with the FTE and dollar variance vs the envelope. Traverse Tree 2 in the decision-trees file.
