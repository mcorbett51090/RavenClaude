---
name: data-migration-and-cutover
description: "Migrate data off a legacy store with dual-write / parallel-run / reconciliation, then cut over with go/no-go gates and a tested rollback. Reach for this for any zero-downtime move or final switch-over."
---

# Skill: Data migration & cutover

Move the data in parallel, reconcile before you switch, and never cut over without a rehearsed rollback (§2 #6).

## Step 1 — Choose the migration pattern
- **Dual-write** — write to old and new, read old, then flip reads to new once reconciled.
- **Shadow read / parallel-run** — serve old, compute new in parallel, compare outputs without serving them.
- **Backfill + reconcile** — copy historical data, then continuously reconcile the delta.
- **Expand/contract** for schema shape changes (route the DDL to `database-engineering`).

## Step 2 — Run in parallel and reconcile
Keep old and new in sync until a reconciliation check shows they agree to your tolerance. Discrepancies are findings to resolve, not noise to ignore.

## Step 3 — Define go/no-go gates
The objective conditions (reconciliation clean, SLOs healthy, rollback rehearsed) that must hold before the switch. Write them down before the day.

## Step 4 — Rehearse the rollback
Actually exercise the rollback in a non-prod (or canary) run. A rollback that was only theorized is not a rollback.

## Step 5 — Cut over incrementally and watch
Shift traffic one cohort/capability at a time, watching reconciliation + SLOs, ready to flip back. Capture the steps in the [`cutover-runbook`](../../templates/cutover-runbook.md) template; the traffic-shift automation is `devops-cicd`'s.
