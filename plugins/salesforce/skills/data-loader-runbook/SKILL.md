---
name: data-loader-runbook
description: A safe data-load runbook — sandbox-first, backup, dedup, and verify — for any bulk data operation. Use before loading, updating, or deleting production data at volume.
---

# Data Loader Runbook

A disciplined, reversible procedure for bulk data operations so a load never becomes an irreversible production incident.

## When to use

Any bulk insert/update/upsert/delete against an org — especially production.

## Steps

1. **Sandbox-first.** Run the full load in a sandbox that mirrors prod config; validate row counts and side effects (triggers, Flows, sharing recalc).
2. **Back up.** Export the target records (and any cascade-affected children) before mutating. Confirm the export is complete and restorable.
3. **Map and dedup.** Validate field mappings; dedup the source (and against existing records — prefer **upsert on an external ID** over blind insert).
4. **Disable noise deliberately.** Consider deferring sharing calculation and, where safe and documented, pausing non-essential automation for the load window (`knowledge/large-data-volume-design.md`).
5. **Load in batches.** Use Bulk API 2.0 (`skills/bulk-rest-api-client`) for volume; capture success/error files.
6. **Verify.** Reconcile counts, spot-check records, confirm automation fired as intended, re-enable anything paused.
7. **Rollback plan.** Keep the backup and the inserted-Id set ready to reverse.

## Output

A filled-in runbook: environment, backup location, mapping, batch plan, verification queries, and the rollback step. This is high-blast — confirm prod actions with the human.
