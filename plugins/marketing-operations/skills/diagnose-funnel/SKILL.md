---
name: diagnose-funnel
description: "Diagnose MQL→SQL→opp→win conversion stage-by-stage — find the leaking stage before adding lead volume. Reach for this on a funnel question."
---

# Skill: Diagnose funnel

More leads into a leaking funnel wastes spend (§3 #1).

## Step 1 — Map the stages
Lead → MQL → SQL → opp → win with conversion + dwell each.

## Step 2 — Find the leak
Lowest conversion or longest dwell via `marketingops_calc.py funnel` (§3 #1).

## Step 3 — Localize the cause
Lead quality, routing, qualification, or follow-up behind the leaking stage.

## Step 4 — Fix the constraint first
Then add volume — not before (§3 #1).

## Output
A stage-by-stage funnel read naming the leaking stage and required-lead volume. Traverse Tree 1 in the decision-trees file.
