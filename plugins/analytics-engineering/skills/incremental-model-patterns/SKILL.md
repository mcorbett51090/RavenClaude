---
name: incremental-model-patterns
description: "Build reliable incremental dbt models: choose the right unique_key and strategy (append, merge, delete+insert), handle late-arriving data and out-of-order events, write a safe is_incremental filter, and design the full-refresh fallback — so the model is idempotent from day one."
---

# Skill: incremental-model-patterns

**Purpose:** Produce incremental dbt models that are correct under rerun, late-data, and full-refresh scenarios. Used by `analytics-engineer` (primary) and `data-quality-testing-engineer` (testing incremental correctness).

## When to use

- A fact table is large enough that a full rebuild is expensive or violates SLA (general rule: > 10M rows or > 30 minutes for a full table scan).
- A source grows mostly via append — new events, new orders, new log lines.
- The model must remain idempotent: running it twice must produce the same result as running it once.

---

## Step 1: Choose the incremental strategy

| Strategy | When to use | Key constraint |
|---|---|---|
| `append_only` (no deduplication) | Source is truly append-only and no row is ever updated | Reruns will create duplicate rows — only safe if you NEVER rerun on overlapping data |
| `merge` (default for most warehouses) | Source rows can be updated (e.g. order status changes), or you need upsert behaviour | Requires a `unique_key`; most expensive at scale |
| `delete+insert` (BigQuery, Snowflake) | Bulk-replace a time-partition or date-range in one operation | Requires a `partition_by` clause; excellent for date-partitioned fact tables with late updates |
| `insert_overwrite` (Spark/Databricks) | Partition-level replacement on Spark | Partition column must be in the `partition_by` block |

**Recommendation for most fact tables:** `merge` with a `unique_key` on the natural event grain. Upgrade to `delete+insert` only when merge cost becomes prohibitive.

---

## Step 2: Define the unique key correctly

The `unique_key` is the identifier dbt uses to decide whether to UPDATE (existing row) or INSERT (new row).

**Rules:**
1. The unique key must identify a row's grain — the combination of attributes that make one row distinct from all others.
2. For event tables, this is usually `event_id` or a composite of (`session_id`, `event_sequence_number`).
3. For slowly changing dimensions in an incremental model, it may be (`entity_id`, `valid_from`).

**Common mistakes:**

| Mistake | Symptom | Fix |
|---|---|---|
| `unique_key` is too narrow (e.g. just `date`) | Entire day's data is merged into one row | Add the natural event grain to the key |
| `unique_key` is too wide (includes a mutable field) | Rows are never matched; duplicates accumulate | Remove mutable fields from the key |
| No `unique_key` with `merge` strategy | dbt falls back to append; duplicates on rerun | Always specify `unique_key` with `merge` |

---

## Step 3: Write the is_incremental filter

The `is_incremental()` macro filters source data to only the new or updated rows when running incrementally. It is the most failure-prone part of the model.

**Standard pattern (timestamp-based, with a lookback window):**

```sql
-- models/marts/fct_orders.sql
{{
  config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='append_new_columns'
  )
}}

select
    order_id,
    customer_id,
    order_status,
    order_amount,
    created_at,
    updated_at

from {{ ref('stg_orders') }}

{% if is_incremental() %}
  -- Lookback window handles late-arriving records and CDC lag
  -- Adjust the interval to 2x the expected source lag
  where updated_at >= (
    select dateadd(hour, -6, max(updated_at)) from {{ this }}
  )
{% endif %}
```

**Why the lookback window:**
Without it, a source record updated 2 hours after the last dbt run is missed because `updated_at > max(updated_at)` is exactly false at the boundary. A 6–24 hour lookback is a safe default; tune it to `2 × max observed source lag`.

**For event tables without an `updated_at` field (true append-only sources):**

```sql
{% if is_incremental() %}
  where event_timestamp > (select max(event_timestamp) from {{ this }})
{% endif %}
```

This is safe only when the source guarantees no late arrivals and no retroactive updates.

---

## Step 4: Handle late-arriving data

Late-arriving data — records that arrive in the source after the model has already processed their time window — are the most common cause of incremental model data quality failures.

**Detection:** run a row-count comparison between the incremental model and a reference full-scan query over the same time window. Any shortfall indicates missed late arrivals.

**Strategies:**

| Approach | How | Trade-off |
|---|---|---|
| Lookback window (recommended) | Extend `is_incremental()` filter back N hours/days | Slightly more data processed per run; simplest to reason about |
| Source watermark table | Write the last successful run timestamp to a watermark table; read it in the filter | More precise; adds operational complexity |
| Partition reprocessing | `delete+insert` strategy reprocesses the last N date partitions each run | Correct for date-partitioned sources; expensive if partitions are large |

---

## Step 5: Full-refresh fallback

Every incremental model must be safe to full-refresh. This means:

1. The full-refresh produces the same result as N sequential incremental runs over all history.
2. There is no state outside the model's own table that would cause a full-refresh to differ from the incremental result.
3. `dbt build --full-refresh` is tested in the CI pipeline at least on a subset of the model's data.

**On schema change:**
Add `on_schema_change='append_new_columns'` to the config so that new columns added to the model don't require an out-of-band table migration. For breaking schema changes (column rename, type change), a full-refresh is required; plan accordingly.

---

## Pitfalls

- **Missing lookback window** — the most common cause of silent data loss in incremental models on sources with CDC or batch lag.
- **`unique_key` on a mutable column** — the key changes, so rows are never matched; duplicates accumulate silently until a full-refresh.
- **`is_incremental()` filter references a column not in the target table** — the first run (full build) passes, but incremental runs fail because the subquery hits the not-yet-existing column. Always reference columns that exist in both the source and the target model.
- **No full-refresh test in CI** — the model appears to work incrementally but is broken for full-refresh; this surfaces as a disaster during a first production deployment or a schema migration.
- **Incremental model used for a dimension** — dimension tables with history management (SCD2) need a different pattern (dbt snapshots), not a raw incremental model; conflating them produces incorrect history.
