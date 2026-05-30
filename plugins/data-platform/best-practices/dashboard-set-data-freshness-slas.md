# Set an explicit data-freshness SLA per dashboard — and sync no faster than it needs

**Status:** Pattern — strong default for every engagement; deviate only when a documented real-time requirement justifies streaming.

**Domain:** Data freshness / pipeline cadence

**Applies to:** `data-platform`

---

## Why this exists

"How fresh is this number?" is the question every dashboard implicitly answers and most never state. Two failures follow from leaving it implicit. **(1) Silent staleness** — an ELT job fails Tuesday night, the dashboard keeps rendering Monday's data, and the client makes a decision on a stale number because nothing told them the pipe broke. **(2) Over-syncing** — a dashboard the client looks at once a day is fed by a pipeline running every 15 minutes, burning MAR/credits and rate-limit budget for freshness nobody consumes. The fix is to make freshness a **declared SLA** (this dashboard is current as of ≤ N hours), enforce it with a dbt `source freshness` check that *alerts* when the SLA is breached, **surface the as-of timestamp on the dashboard itself**, and then set the sync cadence to *just meet* the SLA — no faster. Freshness is a contract, not a side effect.

## How to apply

Declare the freshness window on the source, alert on breach, show the as-of time, and match sync cadence to the SLA.

```yaml
# dbt source freshness = the SLA, machine-checked. Runs in CI separately from dbt build.
sources:
  - name: quickbooks_raw
    loaded_at_field: _airbyte_extracted_at
    freshness:
      warn_after:  { count: 12, period: hour }   # SLA soft breach → warn
      error_after: { count: 24, period: hour }   # SLA hard breach → alert/page
```

```sql
-- Surface the as-of timestamp ON the dashboard (house opinion #7: provenance on every claim).
select max(loaded_at) as data_as_of from {{ ref('fct_revenue_daily') }};
-- Widget footer: "Revenue current as of 2026-05-30 06:00 UTC (QBO sync every 6h)."
```

```yaml
# Sync cadence MATCHES the SLA — don't run 15-min syncs for a daily-viewed dashboard.
schedule: { cron: "0 */6 * * *" }   # 6-hourly meets a ≤12h freshness SLA; no faster
```

**Do:**
- Declare a freshness SLA per source/dashboard (≤ N hours) and encode it as a dbt `source freshness` check that alerts on breach.
- Show the **as-of timestamp** on the dashboard so a stale number is visible, not silent.
- Set sync cadence to *just meet* the SLA — webhooks/streaming only where real-time is genuinely required.
- Run `dbt source freshness` as a distinct CI/scheduled alert, separate from `dbt build`, so stale data is its own signal.

**Don't:**
- Run a pipeline more frequently than the dashboard refresh actually needs (wasted MAR/credits/rate-limit budget).
- Ship a dashboard with no visible as-of time — a broken pipe then renders stale data with full confidence.
- Conflate "the job ran" with "the data is fresh" — a job that ran and loaded nothing still fails freshness.

## Edge cases / when the rule does NOT apply

- **Genuine real-time needs** (fraud signals, live ops, inventory) — stream via webhooks/CDC; the SLA is minutes/seconds and the cadence rule inverts toward *faster*. Document why.
- **Case A (Evidence.dev portfolio)** — refresh is on the build cadence (monthly/quarterly); the "as-of" is the last static deploy date, shown on the page.
- **Snowflake/Delta Sharing** — freshness is the provider's, not yours; surface *their* as-of and the share's latency, not a pipeline SLA you don't own.

## See also

- [`./ingest-idempotent-and-replayable.md`](./ingest-idempotent-and-replayable.md) — a freshness breach often means re-running the load; it must be replay-safe
- [`./connector-incremental-with-backfill.md`](./connector-incremental-with-backfill.md) — cadence is the incremental sync schedule
- [`../skills/dbt-project-scaffolding/SKILL.md`](../skills/dbt-project-scaffolding/SKILL.md) — `dbt source freshness` as a distinct CI alert
- [`../skills/data-quality-tests/SKILL.md`](../skills/data-quality-tests/SKILL.md) — freshness as part of the test taxonomy + runbook-per-alert
- [`../agents/dashboard-builder.md`](../agents/dashboard-builder.md) / [`../agents/etl-pipeline-engineer.md`](../agents/etl-pipeline-engineer.md)

## Provenance

Distilled from CLAUDE.md house opinion #7 (provenance/as-of on every widget claim) + anti-pattern "a pipeline that runs more frequently than the dashboard refresh actually needs," the `dbt-project-scaffolding` skill's `source freshness` separation, and the QBO 6-hourly Airbyte cadence in the source declarations. dbt `source freshness` semantics are stable dbt-core practice; no volatile vendor facts.

---

_Last reviewed: 2026-05-30 by `claude`_
