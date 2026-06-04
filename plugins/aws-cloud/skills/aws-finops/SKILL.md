---
name: aws-finops
description: "Control AWS cost: cost allocation tags from day one, budgets + anomaly detection, rightsize before committing to Savings Plans/RIs, tested backups, and continuous zombie-resource cleanup."
---

# AWS FinOps

## Attribute
Cost allocation **tags** (owner/env/cost-center) — untagged spend is unmanageable.

## Catch early
**Budgets** + **anomaly detection** -> runaway spend caught in hours, not on the invoice.

## Commit last
**Rightsize** on utilization data, THEN buy **Savings Plans/RIs** for the steady baseline. Committing to oversized capacity locks in waste.

## Hygiene
Tested backups (restore, not just backup). Delete zombies (unattached EBS, idle LBs, old snapshots, forgotten dev envs).
