---
scenario_id: 2026-06-05-zero-downtime-schema-migration
contributed_at: 2026-06-05
plugin: backend-engineering
product: postgres
product_version: "unknown"
scope: likely-general
tags: [migration, zero-downtime, expand-contract, backfill, not-null, deploy]
confidence: high
reviewed: false
---

## Problem

A "simple" migration — rename a column and add a `NOT NULL` constraint to it — took the service down for 4 minutes during a rolling deploy. Two separate failures: the `ALTER TABLE ... ADD COLUMN ... NOT NULL DEFAULT` (on an older engine) rewrote the whole table and held a lock that blocked all reads/writes; and the rename broke the *old* application code that was still running during the rolling deploy, because old pods and new pods were live at the same time and the old ones queried the old column name.

## Constraints context

- Rolling deploy (Kubernetes) — old and new application versions run **simultaneously** for the duration of the rollout. The DB schema must satisfy *both* code versions at once.
- A large table (tens of millions of rows) where a full rewrite under lock is a multi-minute outage.
- Single primary Postgres; the migration ran as one transactional step coupled to the deploy.

## Attempts

- Tried: the one-shot migration (rename + add NOT NULL + deploy new code) as a single pre-deploy step. Failed twice over — the table-rewriting `ALTER` locked the table, and even after it finished, old pods still referenced the renamed column and threw `column does not exist`.
- Tried: putting the app in maintenance mode for the migration. "Worked" but *is* the downtime we were trying to avoid; rejected.
- Tried: the **expand/contract** (a.k.a. parallel-change) pattern across multiple deploys, plus a batched backfill and a separately-validated constraint. Zero downtime. This is the resolution.

## Resolution

**A schema change that must coexist with running old code is a multi-step expand/contract, never a single coupled step.** Sequence:

1. **Expand (additive only).** Add the *new* column as nullable, no default rewrite. Adding a nullable column is a cheap metadata change on a modern engine. Don't rename — add the new name alongside the old.
2. **Deploy code that writes both.** New app version writes to *both* old and new columns (dual-write) and still reads the old. Now both deployed versions are satisfiable.
3. **Backfill in batches.** Copy old → new in bounded batches (e.g. 5–10k rows per statement with a short sleep) so no single statement holds a long lock or bloats one transaction. This runs *outside* the deploy, on its own schedule.
4. **Add the constraint without a full-table lock.** Add `NOT NULL` via a `CHECK (col IS NOT NULL) NOT VALID` then `VALIDATE CONSTRAINT` (Postgres validates with a weaker lock that doesn't block writes), rather than a blocking `SET NOT NULL` that scans under a strong lock. `[verify-at-use]` — the exact non-blocking incantation is engine- and version-specific; confirm against the target engine's docs before running on prod.
5. **Switch reads.** Deploy code that reads the new column.
6. **Contract.** Once no running code references the old column, drop the dual-write, then drop the old column in a final deploy.

Each step is independently deployable and reversible, and at no point is there a schema state that only one code version can run against. The rename became "add new, dual-write, backfill, switch reads, drop old" — five boring steps instead of one four-minute outage.

**Action for the next engineer:** before any migration, ask "will old and new code both be live against this schema during the rollout?" If yes (any rolling deploy), the migration must be additive-then-contract across multiple deploys. A rename or a `NOT NULL` add in a single step coupled to the deploy is the classic rolling-deploy outage.

Cross-reference: the **schema/index/lock-behavior** specifics belong to `database-engineering`; this team owns the **dual-write application code, the batched backfill job, and sequencing the change across deploys**. Related: [`../best-practices/keep-transactions-short-and-off-the-network.md`](../best-practices/keep-transactions-short-and-off-the-network.md).
