---
name: run-close
description: "Run the period-end close on a cadence: critical-path checklist, days-to-close, bottleneck. Reach for this on a close question."
---

# Skill: Run close

A close with no target drifts into open-ended cleanup (§3 #1).

## Step 1 — Set the target
Days-to-close goal for the period (§3 #1).

## Step 2 — Lay out the critical path
Dependency-ordered close tasks; gate on reconciliation (§3 #1 #2).

## Step 3 — Compute days-to-close
Critical-path days + bottleneck via `acctgops_calc.py close-cycle` (§3 #1).

## Step 4 — Attack the bottleneck
Parallelize the rest; remove the longest dependent task (§3 #1).

## Output
A critical-path days-to-close read with the bottleneck named. Traverse Tree 1 in the decision-trees file.
