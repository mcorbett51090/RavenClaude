# Acquire locks in a consistent order to prevent deadlocks

**Status:** Absolute rule
**Domain:** Transaction design
**Applies to:** `database-engineering`

---

## Why this exists

A deadlock occurs when two transactions each hold a lock the other needs. PostgreSQL detects these and kills one transaction, but every deadlock is a retried request, a failed user action, and a warning in the logs. Deadlocks are not random — they are deterministic once you know the locking order. A team that agrees on a canonical lock-acquisition order (always lock parent before child; always process rows in primary-key order) eliminates this class of deadlock entirely.

## How to apply

```sql
-- Bad: Transaction A locks users then orders; Transaction B locks orders then users
-- -> Deadlock potential

-- Transaction A
BEGIN;
SELECT ... FROM users WHERE id = $1 FOR UPDATE;
SELECT ... FROM orders WHERE user_id = $1 FOR UPDATE;
COMMIT;

-- Transaction B (concurrent)
BEGIN;
SELECT ... FROM orders WHERE id = $2 FOR UPDATE;
SELECT ... FROM users WHERE user_id = $2 FOR UPDATE;  -- deadlock with A
COMMIT;

-- Good: both transactions lock in the same order (parent → child)
-- Transaction A and B both: users FOR UPDATE first, then orders FOR UPDATE

-- Good: when processing a batch of rows, always sort by primary key
BEGIN;
SELECT ... FROM orders WHERE id = ANY($1::bigint[])
  ORDER BY id   -- consistent ordering eliminates row-level deadlocks
  FOR UPDATE;
COMMIT;
```

**Do:**
- Document the lock acquisition order for every multi-table transaction in the team's schema guide.
- When updating a batch of rows, always `ORDER BY primary_key` before locking.
- Use `SELECT ... FOR UPDATE SKIP LOCKED` for queue-like patterns where you can skip a locked row.
- In the migration plan, review every new multi-table transaction for lock-order consistency with existing ones.

**Don't:**
- Acquire locks in arbitrary order based on the order arguments arrive in the request.
- Lock child rows before parent rows — this is the most common source of parent/child deadlocks.
- Ignore deadlock warnings in the database logs — they point to a locking order bug that needs fixing.

## Edge cases / when the rule does NOT apply

Advisory locks (used for application-level mutual exclusion) have a different lock namespace and their ordering is application-defined. The same principle applies: always acquire advisory locks in a documented, consistent order.

## See also

- [`../agents/db-reliability-engineer.md`](../agents/db-reliability-engineer.md) — owns transaction isolation and lock management.
- [`./choose-isolation-deliberately.md`](./choose-isolation-deliberately.md) — isolation level selection; `SERIALIZABLE` eliminates certain deadlocks at higher cost.

## Provenance

PostgreSQL documentation on lock conflicts and deadlocks (postgresql.org/docs). Standard transaction-design discipline taught in database concurrency courses. Codifies `db-reliability-engineer`'s transaction safety posture.

---

_Last reviewed: 2026-06-05 by `claude`_
