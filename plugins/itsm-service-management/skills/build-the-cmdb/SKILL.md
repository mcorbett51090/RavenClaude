---
name: build-the-cmdb
description: "Stand up a maintainable CMDB — configuration items scoped to what earns its place, automated discovery, the relationships needed for impact analysis, and a drift-audit discipline. Reach for this when you need a configuration/asset source of truth."
---

# Skill: Build the CMDB

A CMDB is only as good as its maintenance discipline; an unmaintained one gives confident wrong answers (§2 #6).

## Step 1 — Decide what's a CI (and why)
A configuration item earns its place by serving a use: impact analysis for change, faster incident diagnosis, dependency mapping. If a CI type serves no decision, don't track it — scope drives maintainability.

## Step 2 — Model the relationships
The value of a CMDB is in the relationships (this service runs on these servers, depends on this database). Model the relationships your use cases need, not an exhaustive graph.

## Step 3 — Automate discovery
Feed the CMDB from automated discovery wherever possible; manual entry rots. Reconcile discovered data against the model.

## Step 4 — Set the drift-audit discipline
Define how often you audit the CMDB against reality and who owns fixing drift. Without this, accuracy decays silently and the CMDB becomes a liability.

## Step 5 — Wire it to the practices
Connect the CMDB to incident (faster diagnosis), problem (impact), and change (blast-radius assessment). The CMDB exists to serve those practices. See [`../../knowledge/itil4-practices-reference.md`](../../knowledge/itil4-practices-reference.md); asset cost/license routes to `finops-cloud-cost`.
