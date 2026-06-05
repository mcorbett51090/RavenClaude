# Add row-count and freshness anomaly tests — not just schema tests

**Status:** Pattern
**Domain:** dbt / data quality
**Applies to:** `analytics-engineering`

---

## Why this exists

Schema tests (not_null, unique, relationships) catch structural defects. They do not catch "the mart built fine but it has 40% fewer rows than yesterday" — which is the real production failure mode. A source that half-loaded (connector paused mid-run, rate limit hit, the Freshdesk silent-skip) produces a structurally valid mart with a silently wrong count. Row-count drift detection and freshness checks are the second test tier that catches what schema tests miss.

## How to apply

**Source freshness (in `sources.yml`):**
```yaml
sources:
  - name: stripe
    freshness:
      warn_after:
        count: 12
        period: hour
      error_after:
        count: 24
        period: hour
    loaded_at_field: _sdc_received_at
    tables:
      - name: charges
```

**Row-count drift (custom singular test or dbt-utils):**
```sql
-- tests/fct_orders__row_count_drift.sql
-- Fail if today's row count is <70% or >200% of the 7-day average
with daily_counts as (
    select
        date_trunc('day', order_date) as build_date,
        count(*) as row_count
    from {{ ref('fct_orders') }}
    where order_date >= current_date - interval '8 days'
    group by 1
),
baseline as (
    select avg(row_count) as avg_7d
    from daily_counts
    where build_date < current_date
),
today as (
    select row_count as today_count
    from daily_counts
    where build_date = current_date
)
select 1
from today, baseline
where today_count < baseline.avg_7d * 0.70
   or today_count > baseline.avg_7d * 2.00
```

Run this in CI and in the scheduled production `dbt build`.

**Do:**
- Add source freshness checks to every source with a load timestamp.
- Add row-count drift tests to every high-stakes mart (revenue facts, customer spine).
- Set `severity: error` on drift thresholds that would produce wrong dashboard numbers; use `warn` for expected-volatile sources.

**Don't:**
- Rely solely on not_null + unique tests and call the model "tested."
- Set drift thresholds so wide (e.g., warn at 99% drop) that they never fire.
- Skip the freshness check on "reliable" sources — reliability is what the check verifies.

## Edge cases / when the rule does NOT apply

- A mart with genuinely high row-count variance (e.g., a daily snapshot fact) may need a rate-of-change test instead of an absolute drift band. Document the chosen threshold and its rationale.

## See also

- [`../agents/data-quality-testing-engineer.md`](../agents/data-quality-testing-engineer.md) — owns the full test taxonomy including anomaly detection
- [`./gate-on-source-freshness.md`](./gate-on-source-freshness.md) — the source freshness gating rule this extends

## Provenance

Codifies the `skills/data-quality-tests/SKILL.md` (row-count drift bands; cross-source reconciliation; the test tier above schema tests) as a standalone best-practice rule for the analytics-engineering plugin.

---

_Last reviewed: 2026-06-05 by `claude`_
