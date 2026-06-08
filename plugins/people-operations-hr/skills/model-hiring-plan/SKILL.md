---
name: model-hiring-plan
description: "Model a capacity-tied hiring plan — back-solve the funnel pipeline for target hires, flag the leaking stage, size recruiter capacity, and hand off the comp envelope. Reach for this on a hiring-plan or stuck-req question."
---

# Skill: Model hiring plan

Hiring is a system, not a recruiter stat (§3 #3); the plan ties to the budget (§3 #6).

## Step 1 — Set the target
Target hires by level and function, tied to capacity/revenue, not a wish list.

## Step 2 — Back-solve the funnel
From accept / onsite→offer / screen→onsite / sourced→screen rates, compute the required pipeline at each stage. Use [`../../scripts/people_calc.py`](../../scripts/people_calc.py) `hiring-plan`.

## Step 3 — Find the leaking stage
The lowest conversion is the constraint — fix it before adding sourcing volume (§3 #3).

## Step 4 — Size capacity & budget
Recruiter load from required-sourced; comp envelope = Σ(hires × band midpoint) → hand to `total-rewards-comp-analyst` (§3 #6).

## Output
A hiring-plan model: required pipeline per stage, the leaking stage named, recruiter capacity, and the comp-budget handoff. Traverse Tree 2 in [`../../knowledge/people-ops-decision-trees.md`](../../knowledge/people-ops-decision-trees.md).
