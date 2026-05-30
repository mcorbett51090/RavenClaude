# Materialize large facts incrementally — with a `unique_key` and a bounded lookback window

**Status:** Pattern — strong default once a fact table's full rebuild stops fitting the refresh window or the cost budget; deviate by staying `table`-materialized while the fact is small.

**Domain:** dbt modeling / materialization

**Applies to:** `data-platform`

---

## Why this exists

A `table`-materialized fact rebuilds from scratch on every `dbt build` — fine at a million rows, ruinous at a billion (full scan of upstream, full warehouse-write, blown refresh window). The fix is `materialized = 'incremental'`: only process rows newer than what's already in the table. But incremental has two footguns that silently corrupt data. **(1) No `unique_key`** → late-arriving or updated source rows get *appended* as duplicates instead of merged, double-counting metrics. **(2) An off-by-one lookback** → an `is_incremental()` filter of `> max(loaded_at)` drops rows that arrived during the run; a bounded **lookback window** (`>= max(loaded_at) - interval '3 days'`) re-processes a safe overlap and the `unique_key` MERGE dedups it. Get both right and incremental is safe; get either wrong and the dashboard quietly lies. This is the dbt-layer analogue of the connector incremental-with-backfill rule.

## How to apply

Set `unique_key`, gate the new-rows filter with `is_incremental()`, and overlap the lookback so late data isn't lost.

```sql
-- models/marts/finance/fct_revenue_daily.sql
{{ config(
    materialized='incremental',
    unique_key=['tenant_id', 'revenue_date'],     -- MERGE key — dedups re-processed rows
    incremental_strategy='merge',
    on_schema_change='append_new_columns'
) }}

select tenant_id, date_trunc('day', charged_at) as revenue_date, sum(amount_usd) as revenue
from {{ ref('stg_stripe__charges') }}
{% if is_incremental() %}
  -- bounded lookback OVERLAP, not a strict '>' — re-process 3 days so late data is captured
  where charged_at >= (select max(revenue_date) from {{ this }}) - interval '3 days'
{% endif %}
group by 1, 2
```

```shell
dbt build --full-refresh --select fct_revenue_daily   # the escape hatch: rebuild from scratch
```

**Do:**
- Always set a `unique_key` (composite is fine) so re-processed rows MERGE instead of duplicating.
- Use a **bounded lookback window** in the `is_incremental()` filter, not a strict `> max()`, so late-arriving rows are captured.
- Keep a `--full-refresh` path documented and runnable — schema changes and logic fixes need it.
- Pair with warehouse partitioning so the incremental window also prunes the scan (the partition rule).

**Don't:**
- Run incremental without a `unique_key` — that's append-only, and updated/late rows duplicate.
- Filter with a strict `>` on the cursor (drops rows that landed mid-run).
- Make a small fact incremental "to be safe" — the complexity doesn't pay back until the rebuild actually hurts.

## Edge cases / when the rule does NOT apply

- **Small facts** (rebuild is seconds, cost negligible) — stay `table`-materialized; incremental is premature complexity.
- **Append-only immutable event logs** with a stable event ID — `insert_overwrite` or append-with-event-ID-dedup can be simpler than MERGE; the `unique_key` is still the event ID.
- **Snapshots (SCD Type 2)** — use dbt `snapshots`, not an incremental model; the history-capture semantics differ.
- **Case A (Evidence.dev)** — no dbt; the page query is recomputed at render, no materialization decision.

## See also

- [`./dbt-stage-then-mart-never-skip-the-layer.md`](./dbt-stage-then-mart-never-skip-the-layer.md) — what incremental models are allowed to reference
- [`./dbt-test-the-floor-unique-not-null-relationships.md`](./dbt-test-the-floor-unique-not-null-relationships.md) — the `unique` test that protects the `unique_key`
- [`./warehouse-partition-and-cluster-for-cost.md`](./warehouse-partition-and-cluster-for-cost.md) — partition so the incremental window prunes the scan
- [`./connector-incremental-with-backfill.md`](./connector-incremental-with-backfill.md) — the ingestion-layer analogue
- [`../skills/dbt-project-scaffolding/SKILL.md`](../skills/dbt-project-scaffolding/SKILL.md)

## Provenance

Distilled from the `dbt-project-scaffolding` skill (materialization + layer rules) and dbt-core incremental-model semantics (`unique_key`, `incremental_strategy='merge'`, `is_incremental()`, `--full-refresh`). The bounded-lookback-overlap pattern is standard practice for late-arriving data. dbt incremental config is stable dbt-core; no volatile vendor facts.

---

_Last reviewed: 2026-05-30 by `claude`_
