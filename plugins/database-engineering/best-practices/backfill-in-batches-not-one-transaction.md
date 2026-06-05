# Backfill data in small batches, not a single large transaction

**Status:** Absolute rule
**Domain:** Schema migrations / data operations
**Applies to:** `database-engineering`

---

## Why this exists

A backfill `UPDATE users SET new_col = derive(old_col)` as a single transaction locks every row in the table for the duration of the update, holds those locks against concurrent reads that need them, bloats the WAL with one enormous transaction, and may exhaust temp file space or take the database offline. On a 50-million-row table, a single-transaction backfill can take hours and constitute an outage. Batching the backfill — updating a few thousand rows at a time, committing between batches, and sleeping briefly — spreads the I/O, releases locks between batches, and allows autovacuum to keep pace.

## How to apply

```python
#!/usr/bin/env python3
# Batched backfill script
import time
import psycopg2

conn = psycopg2.connect(DSN)
batch_size = 5000
sleep_ms = 50  # yield to autovacuum and other writers

last_id = 0
while True:
    with conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE users
            SET new_column = derive_value(old_column)
            WHERE id > %s
              AND new_column IS NULL
            ORDER BY id
            LIMIT %s
            RETURNING id
        """, (last_id, batch_size))
        rows = cur.fetchall()

    if not rows:
        break  # backfill complete

    last_id = rows[-1][0]
    print(f"Backfilled up to id={last_id}")
    time.sleep(sleep_ms / 1000)

print("Backfill complete")
```

**Do:**
- Use a cursor-based batch (`WHERE id > last_id LIMIT batch_size`) rather than offset pagination — offset degrades at scale.
- Commit after each batch to release row locks and allow replication to catch up.
- Sleep briefly between batches (50–200 ms) to reduce I/O pressure and let autovacuum run.
- Monitor replication lag during the backfill; pause if lag grows beyond your RTO.

**Don't:**
- Run a full-table `UPDATE` in production as a single transaction.
- Use `OFFSET n` for pagination in a batched backfill — rows can shift between batches.
- Start the backfill without a dry-run count of affected rows and an estimate of elapsed time.

## Edge cases / when the rule does NOT apply

Very small tables (< 50k rows) where the full-table update completes in under 100 ms can safely run in a single transaction. Staging/dev environments with no live traffic are also fine with single-transaction backfills.

## See also

- [`../agents/migration-engineer.md`](../agents/migration-engineer.md) — owns backfill strategy and expand/contract migration sequencing.
- [`./migrations-expand-contract.md`](./migrations-expand-contract.md) — the backfill is step 2 of the expand/contract sequence; this rule governs how to execute that step safely.

## Provenance

Standard database operations practice for large backfills (widely documented at Stripe, GitLab, and other high-scale Postgres shops). Codifies `migration-engineer`'s safe data-migration approach from CLAUDE.md §2.

---

_Last reviewed: 2026-06-05 by `claude`_
