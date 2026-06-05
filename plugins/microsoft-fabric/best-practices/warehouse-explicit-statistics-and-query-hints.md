# Keep warehouse statistics current and use query hints only when the optimizer is provably wrong

**Status:** Pattern
**Domain:** Fabric Warehouse performance
**Applies to:** `microsoft-fabric`

---

## Why this exists

Fabric Warehouse uses a distributed SQL engine with a cost-based optimizer. The optimizer's plan quality degrades when statistics are stale — after a large initial load or after significant `INSERT`/`MERGE`/`DELETE` activity, the optimizer may choose a hash join where a merge join would cost less, or broadcast a large table that should be shuffled. The instinct to add `OPTION (HASH JOIN)` or `OPTION (LOOP JOIN)` hints is understandable when a specific query is slow, but query hints lock in a plan that becomes wrong as data distributions change. The correct first move is always to update statistics and re-measure; hints are a last resort for a proven optimizer failure.

## How to apply

After any significant data load (> 10% of table rows changed):

```sql
-- Update statistics on the affected tables
UPDATE STATISTICS fact_sales;
UPDATE STATISTICS dim_customer;

-- For a full warehouse statistics refresh (run after initial load or a major ETL):
EXEC sys.sp_updatestats;
```

Before adding a query hint:
1. Run `EXPLAIN` or check the query plan via the Fabric portal Monitoring hub.
2. Identify the specific join or scan step that is wrong.
3. Update statistics on the tables involved and re-run.
4. Only if the optimizer still chooses the wrong plan after fresh statistics, add the targeted hint on that single query.

**Do:**
- Schedule a statistics refresh as a pipeline activity at the end of any daily or weekly full-load step.
- Use `CREATE STATISTICS <name> ON <table>(<column>)` to create column-level statistics on high-cardinality join keys that the auto-stats mechanism may miss.
- Document every query hint with a comment explaining why the optimizer is wrong and a date to re-evaluate.

**Don't:**
- Add `OPTION (FORCE ORDER)` or `OPTION (RECOMPILE)` as a first response to a slow query — these suppress optimizer learning entirely.
- Use `NOLOCK` hints in the Fabric Warehouse — the engine does not support read-committed snapshot isolation in the same way; hint behavior differs from SQL Server.
- Carry a query hint forward without re-testing after a statistics update or a schema change — a valid hint today may be harmful in six months.

## Edge cases / when the rule does NOT apply

For a read-only reporting warehouse where the data distribution never changes (snapshots, historical archives), statistics can be refreshed only at load time, and hints may be stable. Document the static-distribution assumption.

## See also

- [`../agents/warehouse-engineer.md`](../agents/warehouse-engineer.md) — owns Fabric Warehouse T-SQL and performance optimization
- [`./warehouse-scd-and-merge-patterns.md`](./warehouse-scd-and-merge-patterns.md) — the dimensional load patterns that produce the row changes that require statistics updates

## Provenance

Codifies standard distributed-SQL best practice applied to the Fabric Warehouse engine; Microsoft Learn Fabric Warehouse statistics documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
