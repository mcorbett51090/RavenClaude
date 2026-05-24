---
name: dbt-project-scaffolding
description: Scaffold a dbt project that ships — sources → staging → intermediate → marts → metrics layer discipline, generic + custom tests, doc-blocks for every model, exposure tracking, RLS-safe role separation (build-role vs query-role), CI shape (`dbt build` on PR), and a dev/prod env-promotion shape. Reach for this skill at engagement start (greenfield warehouse) or when a dbt project has decayed into ungoverned models. Used by `etl-pipeline-engineer` (primary) + `dashboard-builder`.
---

# Skill: dbt-project-scaffolding

> **Invoked by:** `etl-pipeline-engineer` (primary — owns the modeling layer between raw and the dashboard) + `dashboard-builder` (consumer — reads marts and metrics).
>
> **When to invoke:** engagement start with a greenfield warehouse; ELT lands raw but no transform layer exists; a dbt project has decayed into ungoverned models (no tests, no docs, marts depending on raw sources); inheriting a dbt project that fails `dbt build` on a fresh checkout.
>
> **Output:** dbt project on disk with the canonical layout, tested sources, the build-role / query-role pair, a CI workflow that runs `dbt build`, and a populated `README.md` documenting the env-promotion shape.

## When dbt is the right modeling layer

dbt (dbt-core OSS, MIT-licensed) is the strongest transform layer for:

- **Case B** (per-client deliverable) where the dashboard needs cleaned, tested marts rather than raw landing tables
- **Case C** (productized SaaS) — same plus stable contracts between the warehouse and the semantic layer
- **Case D** (pipes-only) — modeling is often the bulk of the engagement scope
- **Any engagement** where Airbyte / Fivetran land raw and a downstream layer (Metabase, Superset, Cube, Power BI) needs governed reads

dbt is NOT the right choice for:

- Case A (Evidence.dev portfolio) — SQL fenced in `.md` pages is the transform layer; dbt overhead doesn't pay back
- Pure aggregation needs on small data already in the dashboard tool — Metabase models / Power BI semantic model can do it
- When the client already runs dataform / Coalesce / Matillion — don't replatform without an explicit reason

## Canonical layout (sources → staging → intermediate → marts → metrics)

```
my_dbt_project/
├── dbt_project.yml
├── profiles.yml.example          # checked in; profiles.yml is gitignored
├── packages.yml                  # dbt-utils, dbt-expectations, codegen
├── README.md                     # engagement-onboarding, env-promotion shape
├── .github/workflows/dbt-ci.yml  # dbt build + dbt test on PR
├── models/
│   ├── staging/                  # 1 model per source table; renaming, casting, light cleaning ONLY
│   │   ├── quickbooks/
│   │   │   ├── _quickbooks__sources.yml      # source declarations + freshness
│   │   │   ├── _quickbooks__models.yml       # tests + docs for every staging model
│   │   │   ├── stg_quickbooks__customers.sql
│   │   │   ├── stg_quickbooks__invoices.sql
│   │   │   └── stg_quickbooks__payments.sql
│   │   └── stripe/...
│   ├── intermediate/             # business logic that's reused; never queried by BI directly
│   │   ├── int_customer_lifecycle.sql
│   │   └── int_revenue_recognized.sql
│   ├── marts/                    # fact + dimension tables; the BI-facing contract
│   │   ├── finance/
│   │   │   ├── fct_revenue_daily.sql
│   │   │   └── dim_customer.sql
│   │   └── _marts__models.yml
│   └── metrics/                  # dbt-semantic-layer / MetricFlow (optional v1.6+)
│       └── revenue.yml
├── seeds/                        # CSVs checked into git (e.g., manual mapping tables)
├── snapshots/                    # SCD Type 2 history captures
├── macros/                       # custom SQL helpers
├── tests/                        # singular tests (project-specific assertions)
└── analyses/                     # ad-hoc SQL that doesn't materialize
```

### Layer rules — non-negotiable

1. **Staging models ONLY reference sources via `{{ source(...) }}`.** Never `{{ ref('raw_...') }}` and never raw schema-qualified table names.
2. **Marts NEVER reference sources.** Marts only reference staging or intermediate via `{{ ref(...) }}`.
3. **Intermediate is private.** No exposure points at an `int_*` model. No dashboard query reads from `int_*`.
4. **One staging model per source table.** Don't merge two QBO tables in a staging model; that's an intermediate concern.
5. **Cleaning happens in staging, not marts.** Marts assume staging has already cast types, renamed columns, deduplicated, etc.

## Source declarations + freshness

Every source table is declared in a `_<source>__sources.yml` file with a freshness expectation. ELT failures show up as freshness failures before downstream models break.

```yaml
# models/staging/quickbooks/_quickbooks__sources.yml
version: 2
sources:
  - name: quickbooks_raw
    schema: "{{ var('quickbooks_raw_schema', 'quickbooks_raw') }}"
    loaded_at_field: _airbyte_extracted_at
    freshness:
      warn_after: { count: 12, period: hour }
      error_after: { count: 24, period: hour }
    tables:
      - name: customers
        description: "QBO Customer entity. Loaded by Airbyte every 6h."
        columns:
          - name: id
            description: "QBO customer ID (string, opaque)."
            tests:
              - unique
              - not_null
      - name: invoices
        freshness:
          warn_after: { count: 6, period: hour }   # overrides source-level
          error_after: { count: 12, period: hour }
```

`dbt source freshness` runs in CI separately from `dbt build` so stale data is a distinct alert.

## Generic tests (the floor)

Every model in `_<layer>__models.yml` carries at least these tests on its identifying columns:

```yaml
# models/staging/quickbooks/_quickbooks__models.yml
version: 2
models:
  - name: stg_quickbooks__customers
    description: "QBO customers, renamed + cast."
    columns:
      - name: customer_id
        description: "Surrogate primary key."
        tests:
          - unique
          - not_null
      - name: customer_status
        tests:
          - accepted_values:
              values: ['active', 'inactive', 'archived']
      - name: tenant_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_tenant')
              field: tenant_id
```

**Generic tests every plugin agent expects to see:** `unique`, `not_null`, `accepted_values`, `relationships`.

## Custom tests (singular + dbt-utils)

For assertions that don't fit the generic mold, write **singular tests** in `tests/`:

```sql
-- tests/assert_revenue_reconciles_to_stripe.sql
-- Fails if dbt's daily revenue mart disagrees with Stripe's raw charges total by >0.1%.
with dbt_revenue as (
  select sum(revenue) as total from {{ ref('fct_revenue_daily') }}
),
stripe_raw as (
  select sum(amount) / 100.0 as total from {{ source('stripe_raw', 'charges') }} where status = 'succeeded'
)
select dbt_revenue.total, stripe_raw.total
from dbt_revenue, stripe_raw
where abs(dbt_revenue.total - stripe_raw.total) > (stripe_raw.total * 0.001)
```

Any row returned = test fails. Use `dbt-utils` for common patterns: `equal_rowcount`, `mutually_exclusive_ranges`, `not_constant`, `expression_is_true`.

For deeper data-quality coverage, see [`../data-quality-tests/SKILL.md`](../data-quality-tests/SKILL.md).

## Doc-blocks — every model

The marts layer is a contract. Every column gets a description.

```yaml
- name: fct_revenue_daily
  description: |
    Daily revenue mart. One row per tenant per day per revenue stream.
    Reconciles to Stripe raw within 0.1% (see tests/assert_revenue_reconciles_to_stripe.sql).
  columns:
    - name: tenant_id
      description: "{{ doc('col_tenant_id') }}"   # reusable doc-block
    - name: revenue_date
      description: "Calendar date in tenant's reporting timezone."
    - name: revenue
      description: "Recognized revenue in USD. Excludes refunds; includes adjustments."
```

`dbt docs generate && dbt docs serve` produces the consumer-facing lineage graph + column glossary. Ship a CI step that runs `dbt docs generate` and uploads the artifact to S3 / Azure Blob for client review.

## Exposures (downstream consumers)

Declare every dashboard, BI tool, or downstream pipeline that reads marts. Breaks become impact-aware.

```yaml
# models/marts/finance/_exposures.yml
version: 2
exposures:
  - name: revenue_dashboard
    type: dashboard
    maturity: high
    url: https://dashboards.client.example/revenue
    description: "Client-facing revenue dashboard (Cube + Next.js)."
    depends_on:
      - ref('fct_revenue_daily')
      - ref('dim_customer')
    owner:
      name: Matt Corbett
      email: matt@ravenclaude.example
```

When a mart change breaks an exposure, `dbt build --select state:modified+ +exposure:revenue_dashboard` surfaces it.

## Packages worth installing

```yaml
# packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.1.0", "<2.0.0"]
  - package: calogica/dbt_expectations
    version: [">=0.10.0", "<0.11.0"]
  - package: dbt-labs/codegen
    version: [">=0.12.0", "<0.13.0"]
```

- **dbt-utils** — `surrogate_key`, `pivot`, `unpivot`, `date_spine`, the extra test macros
- **dbt-expectations** — Great Expectations-style tests (`expect_column_values_to_be_between`, `expect_table_row_count_to_be_between`)
- **codegen** — `generate_source`, `generate_base_model`, `generate_model_yaml` macros for fast scaffolding

## RLS-safe role separation (the load-bearing piece)

Per the data-platform house opinion #3 (closeness-to-data invariant), dbt's connection account is NOT the same role that powers the dashboard.

```sql
-- Build role: full DDL on the analytics schema; BYPASSRLS allowed.
CREATE ROLE dbt_build_role WITH LOGIN PASSWORD '<env>';
GRANT USAGE, CREATE ON SCHEMA analytics TO dbt_build_role;
ALTER ROLE dbt_build_role BYPASSRLS;   -- only if marts include RLS-protected sources

-- Query role: SELECT-only on marts; NO BYPASSRLS; RLS enforced.
CREATE ROLE dbt_query_role WITH LOGIN PASSWORD '<env>';
GRANT USAGE ON SCHEMA analytics TO dbt_query_role;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO dbt_query_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics
  GRANT SELECT ON TABLES TO dbt_query_role;
-- dbt_query_role does NOT have BYPASSRLS — Metabase/Superset/Cube connect as this role.
```

**Why this matters:** if the semantic layer or BI tool connects as the build role, RLS is silently bypassed because dbt needs BYPASSRLS to truncate/rebuild tables. The query role is the one that respects [`../rls-policy-authoring/SKILL.md`](../rls-policy-authoring/SKILL.md) policies.

## CI shape — `dbt build` on PR

```yaml
# .github/workflows/dbt-ci.yml
name: dbt
on: { pull_request: { branches: [main] } }
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      DBT_PROFILES_DIR: ./
      DBT_TARGET: ci
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install dbt-core dbt-postgres
      - run: dbt deps
      - run: dbt source freshness  # non-blocking; warnings are OK
        continue-on-error: true
      - run: dbt build --fail-fast --select state:modified+ --defer --state ./prod-manifest/
```

`dbt build` runs `seed` + `run` + `snapshot` + `test` in dependency order, fast-failing on the first error. `--defer` reads unchanged models from the prod manifest so PRs only rebuild what changed.

## Env-promotion shape — dev/prod schemas, never branch-per-env

```yaml
# profiles.yml.example
my_dbt_project:
  target: dev
  outputs:
    dev:
      type: postgres
      host: "{{ env_var('DBT_HOST') }}"
      user: dbt_build_role
      password: "{{ env_var('DBT_PASSWORD') }}"
      schema: "dbt_{{ env_var('USER') }}"   # per-developer schema in shared dev DB
      threads: 4
    ci:
      type: postgres
      schema: "dbt_ci_{{ env_var('GITHUB_RUN_ID') }}"
      threads: 4
    prod:
      type: postgres
      schema: analytics
      threads: 8
```

**Per-developer schemas in shared dev DB → CI schema per PR run → prod schema for `main`.** Don't try to maintain a separate dbt project per environment; the variable substitution is enough.

## Anti-patterns this skill flags

- **Marts depending on raw sources** (`{{ source(...) }}` in `marts/`) — the staging contract has been bypassed
- **Logic in marts that belongs in staging** — type casts, column renames, deduplication in a mart is misplaced
- **A model with no tests in `_models.yml`** — at minimum every identifying column needs `unique` + `not_null`
- **A model with no description / column docs** — marts are a contract; undocumented columns are unshippable
- **Dashboard / BI tool connecting as `dbt_build_role`** — silently bypasses RLS; closeness-to-data invariant violation
- **No `dbt source freshness` check** — ELT failure silently propagates as stale dashboards
- **No exposures declared** — mart changes break dashboards with no impact warning
- **Branch-per-environment dbt projects** instead of per-developer schemas in shared dev DB
- **`dbt run` in CI instead of `dbt build`** — `run` skips tests; you ship untested marts
- **Singular tests in `tests/` that nobody owns** — every failing test maps to a runbook entry; see [`../data-quality-tests/SKILL.md`](../data-quality-tests/SKILL.md)
- **`packages.yml` pinned to `>=`** with no upper bound — silent breakage when dbt-utils ships a major version

## Hygiene checklist before merging a dbt PR

- [ ] `dbt build` passes locally and in CI
- [ ] `dbt source freshness` runs (non-blocking is fine, but it runs)
- [ ] Every new model has at least one test in `_models.yml`
- [ ] Every new mart column has a description (use doc-blocks for shared definitions)
- [ ] New exposures declared if a dashboard now consumes a new mart
- [ ] `dbt_query_role` grants checked — Metabase / Superset / Cube can still SELECT
- [ ] CI's `--defer` state manifest is up to date in main
- [ ] Migration notes in PR description if a mart's columns changed (downstream breakage)

## See also

- Skill: [`../data-quality-tests/SKILL.md`](../data-quality-tests/SKILL.md) — going beyond the test floor; severity tiers + runbook integration
- Skill: [`../rls-policy-authoring/SKILL.md`](../rls-policy-authoring/SKILL.md) — the RLS contract `dbt_query_role` respects
- Skill: [`../multi-tenant-migration/SKILL.md`](../multi-tenant-migration/SKILL.md) — propagating `tenant_id` through the staging → marts layers
- Skill: [`../dashboard-performance-tuning/SKILL.md`](../dashboard-performance-tuning/SKILL.md) — when a mart should be a materialized view + how Cube pre-aggs relate
- Template: [`../../templates/dbt-project-starter/`](../../templates/dbt-project-starter/) — copy-paste scaffold
- Knowledge: [`../../knowledge/ipaas-connector-landscape-2026.md`](../../knowledge/ipaas-connector-landscape-2026.md) — what lands raw before dbt picks it up
- dbt docs: [docs.getdbt.com](https://docs.getdbt.com/) (current API reference)
- dbt-core pricing: free / OSS (Apache 2.0); dbt Cloud Developer free for 1 dev, Team $100/dev/mo, Enterprise quoted (retrieved 2026-05-21)
