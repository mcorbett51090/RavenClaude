---
name: data-quality-tests
description: Design data-quality tests that catch real bugs — uniqueness / not-null / referential integrity / freshness / row-count drift / value-range / cross-source reconciliation. dbt-test mechanics for each, severity tiers (error vs warn), the runbook-entry-per-failing-test discipline, and when to escalate to Great Expectations or Monte Carlo / Bigeye. Reach for this skill when launching a new pipeline OR after a "the numbers were wrong" incident. Used by `etl-pipeline-engineer` (primary).
---

# Skill: data-quality-tests

> **Invoked by:** `etl-pipeline-engineer` (primary — owns pipeline correctness). Also consulted by `dashboard-builder` when a widget shows nonsense and the root cause is upstream, and by `database-setup-guide` when establishing source-freshness contracts.
>
> **When to invoke:** new pipeline launch (greenfield); post-incident — "the dashboard numbers were wrong"; pipeline inheritance — testing what the previous engagement built; mart redesign where downstream dashboards exist.
>
> **Output:** test suite committed to the dbt project (or DQ-tool config), severity tiers documented, alert wiring + runbook entries per failing test, escalation criteria documented.

## The discipline (the floor, not the ceiling)

**Every failing test maps to a runbook entry with triage steps.** Tests without owners and runbook entries become noise the team learns to ignore. Two-line discipline:

1. **No test without an owner** — the runbook entry names the human or team that triages on failure
2. **No test without a runbook entry** — the alert tells someone what to *do*, not just that something broke

If you can't write the runbook entry, the test doesn't belong in the suite. Drop it or escalate the data-modeling problem.

## Test taxonomy

| Tier | Category | Examples |
|---|---|---|
| **Column** | not-null | `customer_id` must always be populated |
| | unique | surrogate keys |
| | accepted-values | `status IN ('active', 'inactive', 'archived')` |
| | range | `amount BETWEEN 0 AND 1000000` |
| | regex | email format, phone format |
| **Table** | row-count drift | this fact-table grows 1k-10k rows/day |
| | freshness | source loaded within last 24h |
| | composite uniqueness | `(tenant_id, order_id)` unique even if `order_id` alone isn't |
| | volume floor / ceiling | this table has ≥ 1k rows and ≤ 10M |
| **Cross-table** | referential integrity | every `order.customer_id` exists in `customers` |
| | reconciliation across sources | Stripe charges total = revenue GL account ± 0.1% |
| | conservation laws | sum(debits) = sum(credits) per period |

## dbt mechanics per category

### Generic tests (column level — declared in `_models.yml`)

```yaml
models:
  - name: stg_quickbooks__invoices
    columns:
      - name: invoice_id
        tests:
          - unique
          - not_null
      - name: status
        tests:
          - accepted_values:
              values: ['draft', 'sent', 'paid', 'void']
              severity: error
      - name: amount
        tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 1000000
              severity: warn
      - name: customer_id
        tests:
          - relationships:
              to: ref('stg_quickbooks__customers')
              field: customer_id
              severity: error
```

### Table-level generic tests

```yaml
models:
  - name: fct_revenue_daily
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns: [tenant_id, revenue_date, revenue_stream]
      - dbt_expectations.expect_table_row_count_to_be_between:
          min_value: 1000
          max_value: 10000000
          severity: warn
```

### Freshness (source-level)

```yaml
sources:
  - name: quickbooks_raw
    loaded_at_field: _airbyte_extracted_at
    freshness:
      warn_after: { count: 6, period: hour }
      error_after: { count: 24, period: hour }
    tables:
      - name: invoices
        freshness:
          warn_after: { count: 2, period: hour }
          error_after: { count: 6, period: hour }
```

Run separately from `dbt build`: `dbt source freshness`. Schedule every 15-30 min in CI. Freshness failure = ELT broken, not transform broken; separate alert channel.

### Singular tests (table-shape assertions that don't fit generic mold)

```sql
-- tests/assert_no_future_dated_invoices.sql
-- An invoice dated > today is almost always a typo or a timezone bug.
SELECT invoice_id, invoice_date
FROM {{ ref('stg_quickbooks__invoices') }}
WHERE invoice_date > current_date + interval '1 day'
{{ config(severity='warn') }}
```

Any row returned = test fails. Put project-specific business rules here.

### Row-count drift (the unsung hero)

The pattern that catches the most production issues. **A fact table that's growing should grow by a predictable band per day.**

```sql
-- tests/assert_revenue_row_count_in_band.sql
-- fct_revenue_daily should add 800-12000 rows/day (tenant_id × day × revenue_stream).
-- An outside-band day means: missing tenant data, duplicate load, or pipeline silently dropped rows.
with yesterday as (
  select count(*) as n from {{ ref('fct_revenue_daily') }}
  where revenue_date = current_date - 1
),
expected as (select 800 as floor, 12000 as ceiling)
select n, floor, ceiling
from yesterday, expected
where n < floor or n > ceiling
{{ config(severity='warn') }}
```

For more sophisticated drift detection (deviation from rolling average), `dbt_expectations.expect_row_count_to_be_close_to` or escalate to Great Expectations / Monte Carlo.

### Cross-source reconciliation (the killer)

If two sources should agree, *test that they do*. Catches: silent ELT drops, deduplication bugs, timezone bugs, transform errors.

```sql
-- tests/assert_stripe_revenue_matches_gl.sql
-- Daily Stripe captured charges (after refunds) should equal the GL revenue account ± 0.1%.
with stripe_daily as (
  select date_trunc('day', captured_at) as day, sum(amount_net) as stripe_total
  from {{ ref('stg_stripe__charges') }}
  where status = 'succeeded'
  group by 1
),
gl_daily as (
  select date_trunc('day', posted_at) as day, sum(amount) as gl_total
  from {{ ref('stg_quickbooks__gl_entries') }}
  where account = 'Revenue'
  group by 1
)
select s.day, s.stripe_total, g.gl_total, abs(s.stripe_total - g.gl_total) as variance
from stripe_daily s
join gl_daily g on s.day = g.day
where abs(s.stripe_total - g.gl_total) > (greatest(s.stripe_total, 1) * 0.001)
  and s.day >= current_date - interval '7 days'
{{ config(severity='error') }}
```

This is the test that proves "the numbers are right." Write at least one per material data source pair.

## Severity tiers

| Severity | Meaning | Behavior |
|---|---|---|
| `error` (dbt default) | Test failure halts the build / blocks downstream models | Pipeline does NOT proceed; on-call paged |
| `warn` | Test failure logs but pipeline continues | Slack channel notified; reviewed next business day |
| `error` with `--warn-error` flag | Promote warns to errors in production | Production-strict mode |
| `error` with `where: ...` | Test only fires on a subset (e.g., recent data) | Backfill-friendly; doesn't fight historical bad data |

**Tier-assignment rule of thumb:**

- **`error`** — anything that, if wrong, breaks a downstream dashboard's correctness or compliance posture
- **`warn`** — anything where you want visibility but the pipeline / dashboard can survive the failure (e.g., row count slightly outside band)
- **Configure thresholds** instead of binary pass/fail wherever the test allows it (`expect_column_values_to_be_between` with `row_condition`, `min_value`, `max_value`)

### Severity calibration anti-pattern

Setting every test to `error` so nothing slips → the team learns to bypass the build with `--no-fail-on-test` → tests become decorative. Calibrate carefully. **`warn` is not weakness; it's appropriate for tests where the right human response is "review tomorrow," not "wake me up."**

## Alerting + runbook integration

Every failing test = a Slack / PagerDuty alert that links to a runbook entry. Test names are the runbook key.

### Runbook entry template

```markdown
# Runbook: assert_stripe_revenue_matches_gl

**Owner:** etl-pipeline-engineer (primary), finance ops (downstream consumer)
**Severity:** error
**SLA:** triage within 1 business hour; resolve or escalate within 1 business day

## What this test checks
Daily Stripe captured-charge total vs. QBO GL Revenue account, ± 0.1% tolerance, last 7 days.

## Common causes when this fails
1. **Stripe refund landed but QBO refund hasn't posted yet** → wait 1 business day; will resolve at next QBO sync
2. **Timezone bug** — Stripe in UTC, QBO in tenant local time → check `date_trunc` arguments
3. **QBO connector missed an entry** → check `dbt source freshness` for `quickbooks_raw.gl_entries`
4. **Refund category mismapped in QBO** → check GL chart-of-accounts mapping table

## Triage steps
1. `dbt test --select assert_stripe_revenue_matches_gl --vars '{date: yyyy-mm-dd}'` for the failing date
2. Query the discrepancy: variance per day, which side is high
3. Check #2 above (timezone) by re-running with explicit tz cast
4. If variance > $500: escalate to finance ops within 1 business hour

## Recent incidents
- 2026-03-14: QBO sync delay during Intuit maintenance window; auto-resolved
- 2026-02-02: Refund mapping bug; fix in PR #142
```

Store under `docs/runbooks/<test_name>.md` in the dbt project. CI checks that every test has a corresponding runbook on PR.

## When to escalate beyond dbt tests

dbt tests cover the floor. Escalate when you hit any of these:

| Trigger | Escalate to |
|---|---|
| Volume > 10M rows/day, drift detection needs more than min/max bands | **Great Expectations** (Python, OSS) — richer expectation suite, profiling, data docs |
| Multi-warehouse, multi-pipeline org-wide observability | **Monte Carlo** (sales-quoted; retrieved 2026-05-21) — column-level lineage, ML-based anomaly detection |
| Same as above with a lower price point | **Bigeye** (sales-quoted) or **Sifflet** (sales-quoted) — newer entrants, similar shape |
| Regulated data (HIPAA, PCI-DSS, SOX) — need audit trail + signed test runs | **Soda Cloud** or **Anomalo** — compliance-oriented features |
| Real-time / streaming data | **dbt tests don't cover streaming.** Look at Confluent Schema Registry + ksqlDB tests, or stream-native DQ tools (Acceldata, Bigeye streaming) |

**Decision rule:** dbt tests are the floor; reach for a DQ tool when (a) the volume of tests becomes ungovernable, (b) regulatory / audit pressure requires evidence beyond CI logs, or (c) the engagement is large enough that the DQ tool's annual cost is < the cost of a single missed-data incident.

## Test selection — don't test everything

The wrong move: write a `not_null` + `unique` on every column of every model. The right move: think about **what could go wrong** and test that.

### Test selection checklist (per model)

- [ ] **Identifying columns** — `unique` + `not_null` (always)
- [ ] **Foreign keys** — `relationships` test (always)
- [ ] **Enums** — `accepted_values` (always)
- [ ] **Numeric columns with known bounds** — range tests (often)
- [ ] **Date columns** — sanity test (no future-dated invoices, no pre-launch-dated rows)
- [ ] **Tenant-scoped tables** — `tenant_id not_null` + composite uniqueness with `(tenant_id, ...)` (always for multi-tenant)
- [ ] **Aggregated marts** — row-count drift + at least one reconciliation against a source
- [ ] **Cross-source consistency** — at least one reconciliation test per material source pair (Stripe ↔ QBO, HubSpot ↔ Salesforce, etc.)

## Anti-patterns this skill flags

- **Tests without owners** — every test should have a runbook entry naming who triages
- **Tests that fail silently** — `warn` severity with no alert wiring = nobody knows
- **`error` on tests where the right response is "check tomorrow"** — desensitizes the team to alerts
- **`not_null` + `unique` on every column** — noise that buries the meaningful tests
- **No reconciliation tests** — uniqueness and not-null don't catch silent drops; only cross-source reconciliation does
- **No row-count drift band** — pipeline silently dropping rows is the most common production failure mode
- **`dbt run` in CI instead of `dbt build`** — `run` skips tests; you ship untested marts (see [`./dbt-project-scaffolding.md`](dbt-project-scaffolding.md))
- **Singular tests that don't have a `where` clause limiting to recent data** — historical bad data fails every build forever
- **Freshness tests bundled with `dbt build`** — they should fire on a separate schedule (every 15-30 min) so ELT failures alert independently of transform failures
- **Severity calibrated all-`error` then bypassed with `--no-fail-fast`** — defeats the purpose; calibrate carefully instead
- **DQ tool purchased before dbt tests are exhausted** — paying for sophistication you can't justify; start with the floor

## Hygiene checklist before shipping a pipeline

- [ ] Every staging model has `unique` + `not_null` on its identifying column
- [ ] Every FK has a `relationships` test
- [ ] Every enum column has `accepted_values`
- [ ] Multi-tenant tables: `tenant_id not_null` + composite uniqueness
- [ ] At least one row-count drift band per fact mart
- [ ] At least one cross-source reconciliation per material source pair
- [ ] `dbt source freshness` scheduled separately (every 15-30 min)
- [ ] Severity calibrated — not every test is `error`
- [ ] Every test has a runbook entry under `docs/runbooks/<test_name>.md`
- [ ] Alerts wired to a Slack channel (warn) + PagerDuty (error)
- [ ] CI fails the PR if a new test lacks a runbook entry

## See also

- Skill: [`./dbt-project-scaffolding.md`](dbt-project-scaffolding.md) — the layer that hosts these tests
- Skill: [`./dashboard-performance-tuning.md`](dashboard-performance-tuning.md) — row-count drift tests catch silent pre-agg refresh failures
- Skill: [`./multi-tenant-migration.md`](multi-tenant-migration.md) — `tenant_id not_null` + composite uniqueness as migration gates
- Skill: [`./connector-configuration.md`](connector-configuration.md) — source-side gotchas that DQ tests catch downstream
- Knowledge: [`../knowledge/quickbooks-online-integration.md`](../knowledge/quickbooks-online-integration.md) — QBO-specific reconciliation gotchas
- Knowledge: [`../knowledge/stripe-integration.md`](../knowledge/stripe-integration.md) — Stripe-specific reconciliation patterns
- dbt-expectations: [github.com/calogica/dbt-expectations](https://github.com/calogica/dbt-expectations) — Great Expectations port for dbt
- Great Expectations: [docs.greatexpectations.io](https://docs.greatexpectations.io) (current as of 2026-05-21)
- Monte Carlo pricing: sales-quoted; retrieved 2026-05-21
- Bigeye / Sifflet / Soda: sales-quoted; retrieved 2026-05-21
