---
scenario_id: 2026-06-05-online-add-not-null-column-lock-storm
contributed_at: 2026-06-05
plugin: database-engineering
product: postgres
product_version: "13"
scope: likely-general
tags: [migration, not-null, lock, expand-contract, backfill]
confidence: high
reviewed: false
---

## Problem

A migration to add a `region` column (`NOT NULL`, backfilled from a join on `customers`) to a 60M-row `orders` table took the application down for ~6 minutes during deploy. The single migration statement was effectively `ALTER TABLE orders ADD COLUMN region text NOT NULL DEFAULT '...'` followed by an `UPDATE` to compute the real values. The `ALTER` grabbed an `AccessExclusiveLock` and held it while it rewrote the table; every read and write queued behind it until it finished. The on-call dashboard showed a wall of `lock_timeout`/`statement_timeout` errors and a connection-pool pile-up as requests stacked waiting for the lock.

## Constraints context

- Postgres 13 (so the PG11+ instant-default optimization applies *only* for a constant default — but this default was **computed**, so it required a real backfill regardless).
- Hot table: thousands of writes/min, can't be taken offline.
- The backfill value came from a `JOIN` to `customers`, not a constant — so the "instant default" fast path did not apply.
- Migrations ran coupled to the deploy as one transactional step.

## Attempts

- Tried: the one-shot `ADD COLUMN ... NOT NULL DEFAULT <computed>` + `UPDATE`. Caused the full-table rewrite under `AccessExclusiveLock` → the outage. Even on PG11+, the instant-default fast path only covers a **constant** default; a computed/backfilled value still rewrites.
- Tried: keeping the one-shot but adding `SET lock_timeout = '2s'` so it would fail fast instead of blocking forever. Safer (the migration aborts instead of hanging the DB), but it just turned the outage into a failed deploy — it didn't make the change runnable. A guardrail, not a fix.
- Tried: the **expand/contract** sequence with a batched backfill and `NOT VALID` → `VALIDATE`. Zero downtime. This is the resolution.

## Resolution

**A `NOT NULL` column with a computed backfill on a hot table is a multi-step expand/contract, never one coupled statement.** The sequence that worked:

1. **Add the column nullable, no default.** `ALTER TABLE orders ADD COLUMN region text;` — a cheap metadata-only change, no rewrite, sub-millisecond lock.
2. **Backfill in bounded batches.** `UPDATE ... WHERE id BETWEEN ... AND ...` in chunks of ~5–10k rows, each its own transaction with a short pause, so no single statement holds a long lock or bloats one transaction. Runs on its own schedule, outside the deploy.
3. **Add the constraint without a full scan under a strong lock.** `ALTER TABLE orders ADD CONSTRAINT region_not_null CHECK (region IS NOT NULL) NOT VALID;` adds it for *new* rows immediately under a brief lock; then `ALTER TABLE orders VALIDATE CONSTRAINT region_not_null;` checks existing rows under a `ShareUpdateExclusiveLock` (write-compatible) rather than an `AccessExclusiveLock`.
4. **(Optional) promote to a real column `NOT NULL`.** On modern Postgres a validated matching `CHECK` lets `SET NOT NULL` skip its own scan; confirm the version behavior. `[verify-at-use]` — the exact non-blocking incantation is engine- and version-specific.

The application meanwhile dual-writes `region` so new rows always populate it, making step 3's `NOT VALID` constraint immediately true for new data.

The trap is treating "add a NOT NULL column" as one atomic operation. The lock cost lives in two places — the **table rewrite** (avoided by adding nullable + not forcing a default rewrite) and the **constraint validation** (avoided by `NOT VALID` then `VALIDATE`). Split both out and the change is boring.

**Action for the next engineer:** never couple a backfilled `NOT NULL` add to a deploy as one statement. Ask "is the default constant?" — if no, you need the expand/contract path. Always set a `lock_timeout` on migrations so a blocked `ALTER` fails fast instead of hanging the database.

Cross-reference: canonical rules [`../best-practices/migrations-expand-contract.md`](../best-practices/migrations-expand-contract.md) and [`../best-practices/backfill-in-batches-not-one-transaction.md`](../best-practices/backfill-in-batches-not-one-transaction.md); decision tree "Add a NOT NULL column to a live table — how?" in [`../knowledge/database-engineering-decision-trees.md`](../knowledge/database-engineering-decision-trees.md). The application-side dual-write + deploy sequencing is `backend-engineering`'s lane.
