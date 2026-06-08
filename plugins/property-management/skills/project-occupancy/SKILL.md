---
name: project-occupancy
description: "Project ending occupancy as a flow of move-ins, move-outs, and renewals against a target. Reach for this on an occupancy question."
---

# Skill: Project occupancy

A point-in-time occupancy % hides the flow that fills units (§3 #1).

## Step 1 — Set the unit count and start
Total units and units occupied at period start.

## Step 2 — Net the flow
Move-ins minus move-outs, plus renewals via `property_management_calc.py occupancy-rev` (§3 #1).

## Step 3 — Compute ending occupancy and revenue
Ending occupied ÷ total units × avg rent.

## Step 4 — Name the gap to target
Units short of the target occupancy and the lease-up need.

## Output
An ending-occupancy projection with the gap to target named.
