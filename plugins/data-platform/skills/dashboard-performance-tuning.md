---
name: dashboard-performance-tuning
description: Tune interactive-dashboard performance against a per-widget-class budget — Cube pre-aggregation design, Postgres / DuckDB materialized views, cache layers (Cube + Redis + browser TanStack Query), the per-widget profile loop (measure → identify the slow stage → fix at the lowest-cost layer). Reach for this skill when a dashboard exceeds the 1-2s widget target, or proactively before adding a heavy widget. Used by `dashboard-builder` (primary).
---

# Skill: dashboard-performance-tuning

> **Invoked by:** `dashboard-builder` (primary). Also consulted by `etl-pipeline-engineer` when a slow widget traces back to a missing materialized view or mart-shape problem.
>
> **When to invoke:** a dashboard widget exceeds its budget; a viewer reports "the dashboard is slow"; *before* adding a known-heavy widget (cohort retention, attribution waterfall, large-N tables); a Cube / warehouse cost spike traces to dashboard query volume.
>
> **Output:** widgets within their budget, a per-widget profile log committed to the repo, pre-aggregation / materialized-view design documented in the schema, alerts for hot-path regressions.

## Per-widget budgets (the floor)

These are the engagement-default budgets. Bake them into the dashboard's acceptance criteria. **Time-to-first-interactive widget render**, end-to-end (network + query + render):

| Widget class | Budget (p95) | Budget (p99) | Notes |
|---|---|---|---|
| KPI tile (single value) | 200ms | 400ms | Pre-aggregated; cache-eligible |
| Sparkline | 300ms | 600ms | Same as KPI but time series |
| Bar / line / pie chart | 800ms | 1500ms | Pre-agg; 5-50 buckets typical |
| Table (≤100 rows) | 1.5s | 2.5s | Server-paginated; sorted on indexed column |
| Cohort / retention heatmap | 2s | 3.5s | Often the slowest; pre-aggregate or materialize |
| Deep filter (5+ dimensions) | 2s | 3.5s | Push compute into Cube pre-agg |
| Geo / map | 1.5s | 3s | Aggregated to admin level, not raw lat/lon |

> If you can't hit the budget on a class, **the widget design is wrong**, not the infra. Re-scope before adding shards / replicas.

## The per-widget profile loop

For every widget that misses budget, run the loop. **Don't fix the symptom at the highest-cost layer (more warehouse compute) when a lower-cost layer (pre-agg, cache, smaller query) solves it.**

```
1. Measure → which stage is slow?
   - Cube query log:            cube.dev/docs/observability  (request_id, time spent in pre-agg vs orchestration vs source)
   - EXPLAIN ANALYZE on warehouse: where time goes for raw queries (seq scan vs index, hash join vs nested loop)
   - Browser DevTools: Network tab → identify TTFB vs render time
   - Lighthouse: render-blocking JS / hydration cost

2. Identify the slow stage:
   - Network / TTFB (>200ms)        → upstream caching, CDN, region routing
   - Cube orchestration (>50ms)     → pre-agg design, smaller index, partition key
   - Source query (>500ms)          → materialized view, indexed columns, partition pruning
   - Render time (>500ms)           → fewer DOM nodes, virtualization, code-split heavy widgets
   - Hydration (>1s)                → react-server-components, defer non-critical JS

3. Fix at the LOWEST-COST layer that solves it:
   - Browser cache → Cube pre-agg → materialized view → indexed raw → more compute (last resort)

4. Re-measure with the same load profile. Document the fix in the widget's README.
```

## Cube pre-aggregations (the workhorse for Case B / C)

Pre-aggregations are Cube's killer feature. They turn O(N) source scans into O(log buckets) reads from a compacted rollup table. Three tiers, pick the lowest that meets budget:

### Tier 1 — `rollup` (default)

```yaml
cubes:
  - name: orders
    pre_aggregations:
      - name: daily_by_tenant
        type: rollup
        measures: [total_revenue, order_count]
        dimensions: [tenant_id, product_category]
        time_dimension: order_date
        granularity: day
        partition_granularity: month     # one physical table per month
        refresh_key:
          every: 1 hour
          incremental: true
          update_window: 7 days          # rebuild last 7d on each refresh
        indexes:
          - name: by_tenant_category
            columns: [tenant_id, product_category]
        scheduled_refresh: true
```

- **`partition_granularity`** — one table per month means refresh only rebuilds the current month, not the whole rollup
- **`incremental: true` + `update_window: 7 days`** — handles late-arriving data without full rebuild
- **`indexes`** — Cube creates indexed columns on the rollup; queries against these dimensions hit them

### Tier 2 — `originalSql` (when the rollup shape is wrong)

```yaml
pre_aggregations:
  - name: orders_with_customer_segment
    type: originalSql
    external: true
```

Materializes the cube's underlying SQL as-is into Cube's pre-agg store. Use when the rollup math doesn't compose (e.g., distinct counts that can't roll up from a daily grain).

### Tier 3 — `rollupJoin` (cross-cube pre-aggs at scale)

For Case C at very high QPS, pre-compute the join of two cubes (e.g., `orders × customers`) into one rollup, queried as a single read.

### Pre-agg footguns

- **Missing `tenant_id` in `dimensions`** — pre-agg shared across tenants; cross-tenant leak. See [`./cube-schema-scaffolding.md`](cube-schema-scaffolding.md).
- **`partition_granularity` too coarse** — annual partitions mean every refresh rebuilds the whole year; storage and refresh cost both grow.
- **`refresh_key: every: 1 minute`** — turns the pre-agg into a thrash loop; warehouse cost explodes.
- **No `indexes` block on hot dimensions** — Cube does a full pre-agg scan; budget blown on a "fast" pre-agg.
- **Pre-aggs for queries that aren't on the hot path** — pre-aggs cost storage; only build them for the top 5-10 queries per cube.

## Postgres / DuckDB materialized views (the warehouse-side equivalent)

When there's no semantic layer (raw-Postgres-backed Metabase / Superset), or when Cube's pre-agg shape doesn't match the source-side problem, use materialized views.

### Postgres

```sql
CREATE MATERIALIZED VIEW mv_revenue_daily AS
  SELECT tenant_id, date_trunc('day', order_date) AS day, sum(amount) AS revenue, count(*) AS orders
  FROM fact_orders
  GROUP BY 1, 2;

CREATE UNIQUE INDEX ON mv_revenue_daily (tenant_id, day);   -- enables CONCURRENTLY refresh

-- Refresh: REFRESH MATERIALIZED VIEW CONCURRENTLY mv_revenue_daily;
-- Concurrently = no lock on readers; requires unique index.
```

Schedule the refresh via `pg_cron` or an Airbyte / dbt scheduled job. **`CONCURRENTLY` is non-negotiable** — locks during refresh = dashboard freezes.

### Incremental refresh

Postgres doesn't ship native incremental MVs. Options ranked by complexity:

1. **dbt incremental model** with `materialized='incremental'` → managed table, dbt handles the delta logic (preferred — see [`./dbt-project-scaffolding.md`](dbt-project-scaffolding.md))
2. **pg_ivm extension** (incremental view maintenance) — production-ready on Postgres 14+ but adds operational burden
3. **TimescaleDB continuous aggregates** if you're on Timescale — first-class incremental rollups

### DuckDB (Case A portfolio + MotherDuck)

```sql
CREATE TABLE revenue_daily AS
  SELECT tenant_id, order_date::DATE AS day, sum(amount) AS revenue
  FROM fact_orders GROUP BY 1, 2;
```

DuckDB doesn't have MVs in the Postgres sense; you replace the table on each refresh. Cheap because DuckDB columnar storage rewrites in seconds for typical Case A volumes.

## Materialized views vs Cube pre-aggregations — decision

| Situation | Pick |
|---|---|
| Cube is in the stack | Cube pre-agg (closer to the consumer; tenant-aware) |
| Cube is in the stack but the join is expensive at source | Source materialized view PLUS Cube pre-agg on top |
| No semantic layer (Metabase/Superset on raw Postgres) | Postgres materialized view + indexes |
| Snowflake / Databricks under the hood | Warehouse-native materialized view / Delta Live Table |
| DuckDB / MotherDuck | Replace-on-refresh table (CTAS) |

## Cache layers (browser → semantic → warehouse)

Three layers, ordered cheapest-to-most-expensive to hit:

### 1. Browser cache (TanStack Query / SWR)

```tsx
const { data } = useQuery({
  queryKey: ['revenue-daily', tenantId, dateRange],
  queryFn: () => cubeApi.load({ ... }),
  staleTime: 5 * 60_000,    // 5 min — same as JWT expiration
  gcTime: 30 * 60_000,
});
```

- **`staleTime` ≤ JWT expiration** — don't serve cached results past token validity
- **`queryKey` includes `tenantId`** — otherwise tenant-A user sees tenant-B cached data on session reuse
- **Invalidate on the write path** — `queryClient.invalidateQueries({ queryKey: ['revenue-daily'] })` after a mutation

### 2. Cube cache (in-memory or Redis)

```yaml
# cube.js or cube-deployment.yml
cubeStore:
  driver: redis           # Cube Cloud manages this; self-hosted = your Redis
  host: redis.example
  ttl: 600                # 10 min default
```

Cube's Redis cache stores compiled query results keyed by SQL hash + `securityContext`. Cross-tenant safe because the key includes `tenant_id`. Tune TTL to match data freshness expectations (5-15 min typical).

### 3. Warehouse / source-side cache

- **Postgres** — pg_buffercache, materialized view = the cache
- **Snowflake** — result cache (24h, automatic) + warehouse cache
- **BigQuery** — query result cache (24h, automatic)

The warehouse cache is mostly automatic. The leverage is in shaping queries so they hit it — same SQL string, same parameters.

## Cache invalidation that doesn't thrash

The classic anti-pattern: every dashboard refresh invalidates every query, defeating the cache. Rules:

1. **Invalidate on write, not on read.** Dashboard refresh button reads stale-while-revalidate, doesn't blow the cache.
2. **Scope invalidation to the entity that changed.** `invalidateQueries(['orders', tenantId])`, not `invalidateQueries()`.
3. **TTL ≤ refresh cadence.** If pre-aggs refresh hourly, browser cache TTL of 5 min is fine; 4h is wrong (stale data served).
4. **`stale-while-revalidate` is your friend.** Serve cached → background revalidate → swap in. The viewer never sees a spinner.

## Anti-patterns this skill flags

- **Raw SQL to the viewer** — customer-facing dashboard issuing arbitrary SQL against the warehouse. Use a semantic layer (Cube) or a curated mart (dbt) — never both bypassed.
- **No pre-aggregations on hot-path queries** in Cube — every viewer click bills warehouse compute
- **Pre-aggregations on cold-path queries** — paying storage for a rollup nobody hits
- **`REFRESH MATERIALIZED VIEW` without `CONCURRENTLY`** — readers freeze during refresh
- **Browser cache `staleTime` longer than JWT expiration** — serving data past token validity
- **`queryKey` missing `tenantId`** — cross-tenant cache leak on session reuse
- **No measurement before optimization** — "the dashboard is slow" without `EXPLAIN ANALYZE` / Cube query log = guessing
- **Optimization at the wrong layer** — adding warehouse compute when a missing index would solve it; building a materialized view when a Cube pre-agg is the right layer
- **No regression alerts** — pre-agg silently breaks (e.g., refresh job fails) and the dashboard returns to raw-query land. Set up alerts on pre-agg cache hit rate.
- **Heavy widget added without budget review** — cohort retention dropped into a dashboard without first sizing the source query

## Hygiene checklist before shipping a dashboard

- [ ] Every widget class measured against its budget (p95 + p99) under realistic load
- [ ] Cube query log enabled; baseline cache-hit-rate captured per widget
- [ ] `EXPLAIN ANALYZE` run for any widget whose underlying query exceeds 500ms at source
- [ ] Pre-aggs (or MVs) declared for the top 5-10 hot-path queries; cold-path queries documented as "raw OK"
- [ ] `partition_granularity` set on every pre-agg (month default; week for high-volume)
- [ ] `indexes` block on every pre-agg's hot dimensions
- [ ] `refresh_key` / refresh cadence matches data freshness needs (not faster, not slower)
- [ ] Browser cache `staleTime` ≤ JWT expiration
- [ ] `queryKey` includes `tenantId`
- [ ] Regression alert on pre-agg cache hit rate (<80% = investigate)

## See also

- Skill: [`./cube-schema-scaffolding.md`](cube-schema-scaffolding.md) — the `securityContext` + pre-agg authoring layer
- Skill: [`./dbt-project-scaffolding.md`](dbt-project-scaffolding.md) — dbt incremental models as the materialized-view alternative
- Skill: [`./data-quality-tests.md`](data-quality-tests.md) — row-count drift tests catching silent pre-agg breaks
- Skill: [`./rls-policy-authoring.md`](rls-policy-authoring.md) — tenant-aware pre-aggs respect RLS by including `tenant_id` in dimensions
- Knowledge: [`../knowledge/embedded-analytics-landscape-2026.md`](../knowledge/embedded-analytics-landscape-2026.md) — semantic-layer landscape
- Cube docs: [cube.dev/docs/caching](https://cube.dev/docs/caching) (pre-agg + caching reference)
- Postgres docs: `REFRESH MATERIALIZED VIEW CONCURRENTLY` requires PG 9.4+ and a unique index (current as of PG 17, retrieved 2026-05-21)
