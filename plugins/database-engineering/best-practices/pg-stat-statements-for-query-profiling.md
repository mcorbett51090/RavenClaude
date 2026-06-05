# Enable pg_stat_statements for continuous query profiling

**Status:** Primary diagnostic
**Domain:** Query performance / observability
**Applies to:** `database-engineering`

---

## Why this exists

Without `pg_stat_statements`, you can only investigate a slow query you happened to observe. With it enabled, the database accumulates execution statistics for every normalized query pattern — total calls, mean and max latency, rows read, shared buffer hits and misses — so you can find the queries accounting for the most total time (not just the slowest single execution). This is the difference between reactive "this query is slow right now" debugging and proactive "these five query patterns are responsible for 80% of our database CPU" optimization.

## How to apply

```sql
-- 1. Enable the extension (requires superuser; set in postgresql.conf or RDS parameter group)
-- shared_preload_libraries = 'pg_stat_statements'  -- [verify-at-build] managed DB platforms differ
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 2. Find the highest-total-time queries (the real targets)
SELECT
  LEFT(query, 80) AS query_preview,
  calls,
  ROUND(total_exec_time::NUMERIC, 0) AS total_ms,
  ROUND(mean_exec_time::NUMERIC, 2) AS mean_ms,
  ROUND(max_exec_time::NUMERIC, 2) AS max_ms,
  rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- 3. Reset stats after a tuning cycle
SELECT pg_stat_statements_reset();
```

**Do:**
- Enable `pg_stat_statements` on every production database (it has negligible overhead).
- Review the top-20 queries by `total_exec_time` before adding any index — optimize the highest-impact queries first.
- Track `stddev_exec_time` as well; high variance means intermittent slowness that won't show in mean.
- Reset stats at the start of a performance investigation so the baseline is clean.

**Don't:**
- Optimize queries by `max_exec_time` alone — a query called once slowly matters less than one called 10,000 times at 5 ms.
- Add an index based on a single slow EXPLAIN run without confirming the query appears in `pg_stat_statements` top-20.
- Trust `pg_stat_statements` data that hasn't been reset in months — old stats from defunct queries pollute the rankings.

## Edge cases / when the rule does NOT apply

Managed database services (AWS RDS, Cloud SQL, Azure Database) require enabling `pg_stat_statements` via a parameter group or extension flag — it is not always on by default. Verify the platform-specific enablement procedure. `[verify-at-build]`

## See also

- [`../agents/query-performance-engineer.md`](../agents/query-performance-engineer.md) — owns query analysis and index tuning.
- [`./read-the-plan-before-tuning.md`](./read-the-plan-before-tuning.md) — `pg_stat_statements` identifies which queries to optimize; EXPLAIN ANALYZE shows how.

## Provenance

PostgreSQL documentation on `pg_stat_statements` (postgresql.org/docs). Standard production DBA practice. Codifies `query-performance-engineer`'s observability tooling.

---

_Last reviewed: 2026-06-05 by `claude`_
