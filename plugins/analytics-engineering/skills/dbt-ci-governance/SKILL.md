---
name: dbt-ci-governance
description: "Design a dbt CI pipeline that gates every pull request: compile, run, test, and check source freshness in an isolated developer schema; enforce model contracts on published marts; run slim CI on changed models only using dbt state comparison; and block merges on test failures or contract violations."
---

# Skill: dbt-ci-governance

**Purpose:** Build the CI gate that enforces data quality and schema contracts before any dbt model reaches production. Used by `analytics-engineer` (pipeline design) and `data-quality-testing-engineer` (test gate and contract enforcement).

## When to use

- Setting up CI for a new dbt project.
- Adding a CI gate to an existing project that only runs `dbt compile`.
- Enforcing model contracts on published mart boundaries.
- Reducing CI cost on large projects by running only changed models (slim CI).

---

## The dbt CI gate — what must run on every PR

A CI pipeline that only runs `dbt compile` is not a CI gate — it proves only that the SQL is syntactically valid. A real gate runs in this order:

| Step | Command | Fails on | Why it's required |
|---|---|---|---|
| 1. Compile | `dbt compile` | Syntax errors, missing refs | Fastest check; catches broken references |
| 2. Source freshness | `dbt source freshness` | Stale source data | Prevents building on yesterday's data |
| 3. Build (run + test) | `dbt build --select state:modified+` | Model failures, test failures | Proves the models and their tests pass |
| 4. Contract check | `dbt build --select state:modified+` with contracts enabled | Column drops, type changes on mart models | Prevents breaking downstream consumers |

**On small projects (< 50 models):** run `dbt build` against all models. On large projects, use slim CI (step 3 above uses `state:modified+`) to keep CI time under 10 minutes.

---

## Slim CI — run only what changed

Slim CI uses dbt's `state:` selector to run only models affected by the PR's changes.

**How it works:**
1. In CI, download the production manifest (`manifest.json`) from the last successful production run.
2. Pass it as the `--state` argument.
3. Use `state:modified+` to select models that changed **and all their downstream dependents**.

**GitHub Actions example (simplified):**

```yaml
- name: Download production manifest
  run: |
    aws s3 cp s3://your-bucket/dbt-artifacts/manifest.json ./prod-manifest/manifest.json

- name: dbt build (slim CI)
  run: |
    dbt build \
      --select state:modified+ \
      --state ./prod-manifest \
      --target ci \
      --profiles-dir ./profiles
  env:
    DBT_TARGET_SCHEMA: dbt_ci_${{ github.event.pull_request.number }}
```

**The CI schema isolation rule:** every CI run writes to an isolated schema (`dbt_ci_<PR_NUMBER>`). This prevents CI runs from corrupting dev or prod data and allows parallel PRs to run without interfering.

---

## Model contracts — enforce the mart boundary

A dbt model contract declares the columns and data types that the model guarantees to its consumers. Any breaking change (column removed, type changed) fails the `dbt build` with a `ContractError` rather than silently breaking downstream dashboards.

**Add a contract to a published mart model:**

```yaml
# models/marts/schema.yml
models:
  - name: fct_orders
    config:
      contract:
        enforced: true
    columns:
      - name: order_id
        data_type: bigint
        constraints:
          - type: not_null
          - type: unique
      - name: customer_id
        data_type: bigint
        constraints:
          - type: not_null
      - name: order_amount_usd
        data_type: numeric
      - name: order_status
        data_type: varchar
      - name: created_at
        data_type: timestamp
```

**Contract enforcement rules:**
- Enforce contracts only on **published mart models** (the consumer boundary). Staging and intermediate models are internal; over-contracting them makes refactoring painful.
- Any model referenced in an `exposure` (a declared downstream consumer) should have a contract.
- Adding a new column is non-breaking (allowed without a full-refresh signal). Removing a column or changing a type is breaking and will fail the contract check — this is the desired behaviour.

---

## Source freshness in CI

Source freshness checks verify that the source data the models depend on is not stale before building.

**Configuration in `sources.yml`:**

```yaml
sources:
  - name: raw_orders
    database: raw
    schema: orders
    freshness:
      warn_after:
        count: 6
        period: hour
      error_after:
        count: 24
        period: hour
    loaded_at_field: _loaded_at
    tables:
      - name: orders
      - name: order_items
```

**In CI:** run `dbt source freshness` before `dbt build`. If the source is stale, fail the build before spending compute on downstream models that would be built on outdated data.

**Freshness severity:**
- `warn_after` — prints a warning but does not fail CI; useful for sources with irregular but acceptable lag.
- `error_after` — fails CI; use this for sources that feed time-sensitive marts or dashboards.

---

## Test gates — what must pass before merge

Every PR that adds or modifies a dbt model must pass the following test categories before merge:

| Test type | Tool | Required for merge |
|---|---|---|
| `not_null` on key columns | dbt generic test | YES |
| `unique` on the grain column | dbt generic test | YES |
| `accepted_values` on low-cardinality categoricals | dbt generic test | YES (if applicable) |
| `relationships` on every FK column in a mart | dbt generic test | YES (for mart models) |
| Source freshness | `dbt source freshness` | YES |
| Contract check (for published marts) | dbt contract enforcement | YES |
| Row-count anomaly (large fact tables) | dbt-utils or custom singular test | Recommended |

**Test coverage policy (minimum):**
```
Every model in marts/: not_null + unique + relationships + contract
Every model in staging/: not_null + unique on primary key
Every model in intermediate/: not_null on critical path columns
```

---

## Pitfalls

- **CI runs only `dbt compile`** — this is the most common CI shortcut; it catches syntax but not logic failures, stale sources, or test failures. Always run `dbt build`.
- **No schema isolation in CI** — concurrent PR pipelines overwrite each other's tables in a shared schema; use `dbt_ci_<PR>` schemas.
- **Contracts on internal models** — enforcing contracts on staging and intermediate models prevents normal refactoring; contracts belong at the mart boundary.
- **Slim CI without state comparison** — `state:modified+` without a valid `--state` manifest falls back to running all models; download the latest prod manifest as an explicit CI step.
- **Source freshness not integrated into CI** — the build passes on data that is 30 hours old; the dashboard is correct SQL on stale numbers.
