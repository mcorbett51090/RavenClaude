# Monitor and manage autovacuum, bloat, and transaction ID wraparound

**Status:** Primary diagnostic
**Domain:** Database operations (PostgreSQL)
**Applies to:** `database-engineering`

---

## Why this exists

PostgreSQL's MVCC implementation leaves dead row versions in the heap until vacuum reclaims them. On high-update/delete tables, dead tuples accumulate faster than autovacuum removes them — a condition called table bloat. Bloat inflates table and index sizes, degrades sequential scan performance, and causes index-only scans to fail (visibility map entries are stale). Worse, PostgreSQL must wrap around 32-bit transaction IDs every ~2 billion transactions; if `VACUUM` does not advance the frozen XID before wraparound, the database enters emergency read-only mode and refuses writes. This is one of the few PostgreSQL failure modes that cannot be fixed without downtime.

## How to apply

```sql
-- Check bloat and autovacuum health on high-write tables
SELECT
  schemaname,
  tablename,
  n_dead_tup,
  n_live_tup,
  ROUND(n_dead_tup::NUMERIC / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 1) AS dead_pct,
  last_autovacuum,
  last_autoanalyze,
  autovacuum_count
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;

-- Check XID age per database (alert if age > 1 billion)
SELECT datname,
       age(datfrozenxid) AS xid_age,
       2000000000 - age(datfrozenxid) AS xids_remaining
FROM pg_database
ORDER BY xid_age DESC;
```

**Do:**
- Alert when a table's dead-tuple percentage exceeds 20% and autovacuum is not keeping up.
- Alert when `age(datfrozenxid)` exceeds 1 billion — aggressive vacuum is needed; at 1.5 billion it is an emergency.
- Tune `autovacuum_vacuum_cost_delay` and `autovacuum_vacuum_scale_factor` for high-update tables; the defaults are too conservative.
- Run `VACUUM ANALYZE` manually after large bulk deletes or imports.

**Don't:**
- Disable autovacuum — this is a frequent "performance fix" that creates an XID wraparound emergency weeks later.
- Use long-running transactions on tables that receive concurrent updates — they block vacuum from reclaiming tuples.
- Ignore bloat because queries "still work" — bloat compounds over time and the eventual vacuum catch-up stalls the database.

## Edge cases / when the rule does NOT apply

Read-only replicas do not accumulate dead tuples from local writes, but they still need their `datfrozenxid` advanced by replication from the primary. The XID wraparound alarm applies to the primary.

## See also

- [`../agents/db-reliability-engineer.md`](../agents/db-reliability-engineer.md) — owns autovacuum tuning and bloat management.
- [`../agents/query-performance-engineer.md`](../agents/query-performance-engineer.md) — bloat degrades index-only scans and shows up in EXPLAIN plans.

## Provenance

PostgreSQL documentation on MVCC, autovacuum, and transaction ID wraparound (postgresql.org/docs). Codifies `db-reliability-engineer`'s bloat and vacuum management responsibility from CLAUDE.md §1.

---

_Last reviewed: 2026-06-05 by `claude`_
