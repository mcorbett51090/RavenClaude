---
name: size-caseload
description: "Size clinician caseload capacity against measured demand and the no-show-adjusted fill rate, not a guessed ratio. Reach for this on a staffing or utilization question."
---

# Skill: Size caseload to demand

A fixed headcount ratio untied to demand under- or over-staffs (§3 #4).

## Step 1 — Measure demand
Visit demand and the no-show-adjusted fill rate by program.

## Step 2 — Compute capacity
FTEs × target weekly billable hours ÷ avg session length via `behavioral_health_practice_calc.py caseload` (§3 #4).

## Step 3 — Read the gap
Capacity in sessions vs demand → utilization and the staffing gap (§3 #4).

## Step 4 — Tie to margin
Connect filled capacity to reimbursement per visit (§3 #5).

## Output
A caseload-capacity read vs demand with utilization and the staffing gap named.
