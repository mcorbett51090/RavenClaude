# Partition and cluster large facts on the columns you filter — pay for the rows you read

**Status:** Primary diagnostic — when a warehouse bill or a dashboard query is too expensive, check the partition/cluster keys against the actual filter columns first.

**Domain:** Warehouse / cost + performance

**Applies to:** `data-platform`

---

## Why this exists

On scan-priced warehouses (BigQuery `$/TiB` scanned, Snowflake credits, Redshift Serverless RPU-hours), an unpartitioned fact table means **every dashboard query scans the whole table** — you pay for billions of rows to return a single tenant's last 30 days. The fix is to partition on the column the dashboards filter on (almost always a **date**) and cluster/sort on the next-most-selective columns (tenant, then the common dimension). Partition pruning is what turns a 3 PB scan into a 2 GB scan and a $40 query into a $0.04 query. The recurring miss is partitioning on a column nobody filters on (an arbitrary load date) instead of the column the `WHERE` clause actually uses — pruning only fires when the query predicate matches the partition key. For multi-tenant facts this rule also compounds the isolation invariant: `tenant_id` should be both indexed (Postgres RLS) and a clustering key (warehouse) so the tenant filter prunes *and* the RLS scan stays cheap.

## How to apply

Partition on the date the dashboards window on; cluster on tenant + the hottest dimension. Match the keys to the real `WHERE`/`GROUP BY`.

```sql
-- BigQuery: partition on the filtered date, cluster on tenant + hot dimension.
create table analytics.fct_revenue_daily
partition by date_trunc(revenue_date, month)        -- dashboards window on revenue_date
cluster by tenant_id, customer_id                   -- then tenant, then the common join key
as select * from staging.revenue;

-- Snowflake: clustering key on the columns queries filter/join on.
alter table analytics.fct_orders cluster by (tenant_id, order_date);

-- Postgres (system-of-record): index the columns RLS + dashboards filter on.
create index idx_fct_orders_tenant_date on fct_orders (tenant_id, order_date);
-- huge facts → native range partitioning by month, plus the per-partition index.
```

**Do:**
- Partition on the **date the dashboards window on** — the column in the `WHERE`/`GROUP BY`, not an arbitrary load timestamp.
- Cluster/sort on `tenant_id` first for multi-tenant facts, then the hottest join/filter dimension.
- Verify pruning actually fires — read the query plan / dry-run bytes-scanned; a partition key the queries don't use buys nothing.
- Co-locate this with the materialization choice — a pre-aggregated mart on the right grain scans even less (see incremental-fact rule).

**Don't:**
- Partition on a high-cardinality column (a UUID, a raw timestamp to the second) — too many tiny partitions hurts more than it helps.
- Add clustering keys the queries never filter on — you pay maintenance cost for zero pruning.
- Assume Postgres "partitioning" without an index on the partition/tenant column — RLS still scans whole partitions without it.

## Edge cases / when the rule does NOT apply

- **Small tables** (well under the warehouse's partition-minimum, e.g. BigQuery's ~1 GB guidance) — partitioning adds metadata overhead for no scan saving; leave them flat.
- **DuckDB / embedded read paths** — pre-aggregate to the dashboard grain instead; column-pruning + the file format (Parquet) do most of the work, explicit partitioning matters less.
- **Flat-priced compute** (a fixed Postgres instance, Fabric reserved capacity) — the *cost* lever is weaker, but the *performance* lever (index/cluster for query latency) still applies.

## See also

- [`./dbt-incremental-with-unique-key-for-large-facts.md`](./dbt-incremental-with-unique-key-for-large-facts.md) — incremental materialization keeps the partition you rebuild small
- [`./warehouse-select-by-workload-not-brand.md`](./warehouse-select-by-workload-not-brand.md) — which warehouse you're optimizing on
- [`./model-semantic-layer-single-source-of-truth.md`](./model-semantic-layer-single-source-of-truth.md) — pre-aggregations in the semantic layer reduce scan further
- [`../skills/dashboard-performance-tuning/SKILL.md`](../skills/dashboard-performance-tuning/SKILL.md) — the measure → fix-at-lowest-cost-layer loop

## Provenance

Distilled from `dashboard-performance-tuning` skill (per-widget budgets + pre-aggregation tiers), `cloud-database-landscape-2026.md` scan-pricing facts (BigQuery `$6.25/TiB`, Redshift RPU-hours, Snowflake credits) and the multi-tenant `tenant_id`-index requirement in `multi-tenant-rls-patterns.md`. Partition-pruning / clustering is stable warehouse practice. `[verify-at-build]` BigQuery partition-minimum guidance and `$/TiB` scan price — re-confirm on the live pricing page.

---

_Last reviewed: 2026-05-30 by `claude`_
