---
name: diagnose-attrition
description: "Diagnose an attrition spike with cost and cause — split regretted from non-regretted, localize to team/manager, price the loss, name the driver. Reach for this on a retention question."
---

# Skill: Diagnose attrition

A turnover number with no split, no cost, and no segment is noise (§3 #1).

## Step 1 — Split regretted vs non-regretted
Non-regretted (managed-out) is often intended; only the regretted share is a loss to recover (§3 #1).

## Step 2 — Localize it
Segment by team / manager / level / tenure cohort. A concentrated spike is a manager/span problem (§3 #7); broad-based is structural.

## Step 3 — Name the driver
Comp, manager, growth, or workload — usually two co-occur. Route a comp driver to `total-rewards-comp-analyst`.

## Step 4 — Cost it
Regretted exits × replacement cost (recruiting + ramp + vacancy). Use [`../../scripts/people_calc.py`](../../scripts/people_calc.py) `attrition`.

## Output
An annualized, regretted-split, segmented attrition read with a dollar cost and a named driver — and a ranked action list with owners/dates. Traverse Tree 1 in [`../../knowledge/people-ops-decision-trees.md`](../../knowledge/people-ops-decision-trees.md).
