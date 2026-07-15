---
name: zero-downtime-migration
description: "Plan a schema change on a live production database with no downtime using expand-contract — additive expand, dual-write, batched/throttled backfill, cutover, then contract — with lock duration and replication lag managed. Reach for this before any non-additive change to a hot table (NOT NULL, rename, type change, drop) or a large backfill. Pairs with db-incident-triage if a migration goes wrong."
---

# Skill: Zero-downtime migration (expand-contract)

Change a running database without an outage. The default shape is
**expand-contract**; the enemies are **lock duration** and **replication lag**.

## Step 0 — One opinion up front
**Never a destructive change in one step.** Add the new shape, move to it, *then*
remove the old — each step individually reversible. A one-shot `ALTER` on a hot
table is how migrations become outages.

## Step 1 — Classify the change
Trace [`../../knowledge/dbre-decision-trees.md`](../../knowledge/dbre-decision-trees.md) §3:
- **Purely additive** (nullable column, new table, new index) → apply directly;
  build indexes **concurrently/online** on hot tables.
- **Anything else** (NOT NULL, rename, type change, drop, constraint) → full
  expand-contract.

## Step 2 — Expand
Add the new shape additively and reversibly: new column (nullable), new table, new
index (online). Deploy this first, alone.

## Step 3 — Dual-write + backfill
- **Dual-write:** application writes both old and new shapes.
- **Backfill:** copy existing rows in **batches**, **throttled**, **idempotent**,
  **resumable**, with **progress tracking** and a **kill switch**. Pace against
  replication lag — if lag climbs, slow down. **Never one big `UPDATE`.**

## Step 4 — Cutover
Move reads to the new shape. Verify parity (old vs new) before and after.

## Step 5 — Contract
Once nothing reads the old shape, drop it — as its own reversible step, off-peak.

## Step 6 — Guard the locks
For every step, know the lock it takes and its duration under production load. Set a
`lock_timeout`; if a step would hold a hot lock, re-plan into smaller steps or an
online tool (gh-ost / pt-online-schema-change) before considering a window.

## Step 7 — Hand off
- If a step triggers a **live incident** → `db-incident-triage` /
  `database-incident-responder`.
- The **target schema design** → `database-engineering`.
- The **CI/CD** that ships each step → `devops-cicd`.

## Output
An expand-contract migration plan: each step (expand → dual-write → backfill →
cutover → contract) with its lock/lag risk, the batched backfill parameters, the
per-step rollback, and the parity checks.
