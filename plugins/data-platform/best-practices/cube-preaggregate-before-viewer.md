# Pre-aggregate in the semantic layer before a viewer query touches the warehouse

**Status:** Absolute rule
**Domain:** Semantic layer / query performance
**Applies to:** `data-platform`

---

## Why this exists

A customer-facing dashboard endpoint that ships raw SQL directly to the warehouse pays full scan cost on every load — and that cost is invisible until the bill arrives. Cube (or an equivalent semantic layer) owns the query plan, caching, and tenant-scoped access control. Pre-aggregations computed on a schedule or on first-miss collapse a full-table scan into a sub-second rollup read. Skipping this step couples viewer traffic to warehouse compute dollars in a way that scales linearly and breaks SLAs at busy hours.

## How to apply

1. Define at least one `pre_aggregations` block on every Cube that a viewer-facing dashboard consumes.
2. Start with `rollup` on the most-queried dimension/measure set; fall back to `originalSql` only when no rollup fits.
3. Set a `refreshKey` (time- or cron-based) so data freshness is deliberate, not accidental.
4. Pin the `granularity` of time dimensions to the coarsest unit the dashboard actually needs — daily is almost always cheaper than hourly.

```yaml
cubes:
  - name: orders
    sql_table: public.fct_orders

    measures:
      - name: total_revenue
        sql: amount
        type: sum

    dimensions:
      - name: created_date
        sql: created_at
        type: time

    pre_aggregations:
      - name: daily_revenue_by_tenant
        measures: [total_revenue]
        dimensions: [tenant_id]
        time_dimension: created_date
        granularity: day
        refresh_key:
          every: 1 hour
```

**Do:**
- Ship at least one pre-aggregation per customer-facing Cube before go-live.
- Set `access_policy` / `securityContext` so pre-aggregations are also tenant-scoped.
- Monitor pre-aggregation hit rate in Cube Developer Playground; aim for >90% hits on steady-state traffic.

**Don't:**
- Let dashboard widgets hit the warehouse with raw SELECT queries at viewer load time.
- Use `originalSql` as the default — it caches the full base query, not a rollup.
- Remove a pre-aggregation without checking downstream widget query plans first.

## Edge cases / when the rule does NOT apply

- Single-tenant deliverables with a single user and a warehouse that charges by the query (not the scan) may not need pre-aggregations — but document the assumption.
- Development / staging environments where real-time freshness is needed for debugging may intentionally bypass caching.

## See also

- [`../agents/dashboard-builder.md`](../agents/dashboard-builder.md) — primary consumer of this rule when generating Cube schemas
- [`./deny-test-every-stack.md`](./deny-test-every-stack.md) — the cross-boundary denial test that pre-aggregations must also pass

## Provenance

Codifies data-platform CLAUDE.md §3 house opinion #5 ("Pre-aggregate in the semantic layer. Don't ship raw SQL queries to a customer-facing dashboard endpoint") and the `skills/cube-schema-scaffolding/SKILL.md` pre-aggregation hints discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
