# database-engineering — best-practice docs

Named, citable rules for the `database-engineering` plugin's specialists. Each file is **one rule**.

---

## Index

_22 rules across schema design, query performance, migrations, and database operations._

| Doc | Status | Use when |
|---|---|---|
| [`normalize-first-denormalize-deliberately.md`](./normalize-first-denormalize-deliberately.md) | Absolute rule | Designing a schema — start at 3NF; denormalize only with a measured, named reason. |
| [`constraints-belong-in-the-database.md`](./constraints-belong-in-the-database.md) | Absolute rule | Data integrity — FKs, NOT NULL, UNIQUE, CHECK belong in the DB, not only in app code. |
| [`be-explicit-about-null-semantics.md`](./be-explicit-about-null-semantics.md) | Absolute rule | Nullable columns — make nullability intentional and document what NULL means for each column. |
| [`model-for-the-query-not-just-the-entities.md`](./model-for-the-query-not-just-the-entities.md) | Pattern | Schema design — shape the schema for the real read patterns, not just the entity graph. |
| [`never-select-star-in-application-code.md`](./never-select-star-in-application-code.md) | Absolute rule | Every application query — select the columns you need; SELECT * is fragile and wasteful. |
| [`use-timestamptz-not-timestamp.md`](./use-timestamptz-not-timestamp.md) | Absolute rule | Every timestamp column — use TIMESTAMPTZ to store UTC; TIMESTAMP is timezone-ambiguous. |
| [`avoid-hot-spots-in-sequential-primary-keys.md`](./avoid-hot-spots-in-sequential-primary-keys.md) | Pattern | High-insert tables — use UUID v7 or ULID for distributed, time-ordered primary keys. |
| [`foreign-keys-need-indexes-on-the-referencing-side.md`](./foreign-keys-need-indexes-on-the-referencing-side.md) | Absolute rule | Every FK column — index the referencing (child) column or parent deletes become full scans. |
| [`read-the-plan-before-tuning.md`](./read-the-plan-before-tuning.md) | Primary diagnostic | Any slow query — read EXPLAIN (ANALYZE) before adding an index or rewriting. |
| [`match-the-index-to-the-predicate.md`](./match-the-index-to-the-predicate.md) | Absolute rule | Adding an index — match the type (B-tree/partial/GIN/composite) to the actual predicate shape. |
| [`partition-only-when-size-demands-it.md`](./partition-only-when-size-demands-it.md) | Pattern | Large tables — partition by range or hash only when size genuinely degrades query performance. |
| [`pg-stat-statements-for-query-profiling.md`](./pg-stat-statements-for-query-profiling.md) | Primary diagnostic | Performance investigation — use pg_stat_statements to find the highest total-time query patterns. |
| [`migrations-expand-contract.md`](./migrations-expand-contract.md) | Absolute rule | Any schema change — use expand/contract across separate deploys for zero-downtime migrations. |
| [`backfill-in-batches-not-one-transaction.md`](./backfill-in-batches-not-one-transaction.md) | Absolute rule | Any bulk data backfill — update in small batches with commits between them, not one transaction. |
| [`pool-connections.md`](./pool-connections.md) | Absolute rule | Any application with a database — use a connection pooler; raw connections are not the pool. |
| [`size-connection-pools-to-the-database-not-the-app.md`](./size-connection-pools-to-the-database-not-the-app.md) | Absolute rule | Sizing PgBouncer / the app pool — size to DB vCPU capacity, not to app instance count. |
| [`choose-isolation-deliberately.md`](./choose-isolation-deliberately.md) | Absolute rule | Opening a transaction — choose the isolation level by the anomalies you must prevent. |
| [`lock-ordering-prevents-deadlocks.md`](./lock-ordering-prevents-deadlocks.md) | Absolute rule | Multi-table transactions — always acquire locks in a documented, consistent order. |
| [`a-backup-is-only-real-if-restored.md`](./a-backup-is-only-real-if-restored.md) | Absolute rule | Backups — a backup is only real when you've verified a restore. |
| [`test-restores-not-just-backups.md`](./test-restores-not-just-backups.md) | Absolute rule | Restore testing — run automated restore tests weekly; record restore duration as the RTO. |
| [`vacuum-and-bloat-are-operational-concerns.md`](./vacuum-and-bloat-are-operational-concerns.md) | Primary diagnostic | PostgreSQL health — monitor autovacuum health, dead-tuple percentage, and XID age actively. |
| [`replication-lag-is-a-consistency-risk.md`](./replication-lag-is-a-consistency-risk.md) | Primary diagnostic | Read replicas — monitor lag and route freshness-requiring reads to the primary. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
