# Test the floor — every model carries unique / not_null / relationships, and CI runs `dbt build`

**Status:** Absolute rule — a model with no tests on its identifying columns is unshippable, and CI runs `dbt build` (not `dbt run`) so the tests actually gate the marts.

**Domain:** dbt modeling / data quality

**Applies to:** `data-platform`

---

## Why this exists

The marts layer is a published contract; an untested contract is a rumor. The cheap, high-leverage floor is four generic tests — `unique` and `not_null` on every surrogate key, `relationships` on every foreign key, `accepted_values` on every enum — because they catch the failures that silently corrupt a dashboard: a fan-out join that duplicates a primary key (revenue suddenly doubles), a null `tenant_id` that escapes RLS scoping, an orphaned foreign key that drops rows from a chart. The other half of the rule is the **runner**: `dbt run` materializes models and *skips tests*; only `dbt build` runs `seed` + `run` + `snapshot` + `test` in dependency order so a failing test actually blocks the broken mart from shipping. Running `dbt run` in CI is how teams convince themselves they have tests while shipping untested marts.

## How to apply

Put the four generic tests on identifying columns in `_<layer>__models.yml`; run `dbt build --fail-fast` in CI.

```yaml
# models/staging/stripe/_stripe__models.yml — the floor on every model
version: 2
models:
  - name: stg_stripe__charges
    columns:
      - name: charge_id
        tests: [unique, not_null]              # surrogate key: both, always
      - name: tenant_id
        tests:
          - not_null                            # a null here escapes RLS scoping
          - relationships: { to: ref('dim_tenant'), field: tenant_id }
      - name: status
        tests:
          - accepted_values: { values: ['succeeded', 'pending', 'failed'] }
```

```yaml
# CI: dbt BUILD, never dbt run — build runs the tests; run skips them.
- run: dbt build --fail-fast --select state:modified+ --defer --state ./prod-manifest/
```

**Do:**
- Put `unique` + `not_null` on **every** surrogate/primary key, in every layer (staging too — bad keys caught early are cheap).
- Put `relationships` on every foreign key so orphaned rows surface before a chart silently drops them.
- Use severity tiers — `error` blocks the build; `warn` for drift bands you want visible but not blocking (see data-quality-tests skill).
- Add a singular reconciliation test where a number must tie out cross-source (Stripe charges ↔ revenue mart within 0.1%).

**Don't:**
- Ship a model with no tests in `_models.yml` — at minimum every identifying column needs `unique` + `not_null`.
- Run `dbt run` in CI (it skips tests) — run `dbt build`.
- Leave a failing singular test unowned — every test maps to a runbook entry.

## Edge cases / when the rule does NOT apply

- **Case A (Evidence.dev)** — no dbt project; the SQL-in-markdown pages don't have a dbt test harness. Validate the query result instead (the page IS the transform).
- **Genuinely nullable business columns** — `not_null` belongs on keys and required fields, not on a column that legitimately can be null; don't cargo-cult it everywhere.
- **`warn`-severity drift checks** — a row-count band that exceeds its threshold should warn, not fail the build, until a human triages — that's a deliberate non-blocking test, not a missing one.

## See also

- [`./dbt-stage-then-mart-never-skip-the-layer.md`](./dbt-stage-then-mart-never-skip-the-layer.md) — the layering the tests gate
- [`./dbt-incremental-with-unique-key-for-large-facts.md`](./dbt-incremental-with-unique-key-for-large-facts.md) — incremental models need the `unique_key` the `unique` test protects
- [`../skills/data-quality-tests/SKILL.md`](../skills/data-quality-tests/SKILL.md) — severity tiers, drift bands, cross-source reconciliation, runbook discipline
- [`../skills/dbt-project-scaffolding/SKILL.md`](../skills/dbt-project-scaffolding/SKILL.md) — the test floor + `dbt build` CI shape
- [`../agents/etl-pipeline-engineer.md`](../agents/etl-pipeline-engineer.md) — owns the modeling layer

## Provenance

Codifies the "Generic tests (the floor)" and "`dbt run` in CI instead of `dbt build`" anti-pattern from the `dbt-project-scaffolding` skill, plus the test taxonomy + severity tiers from `data-quality-tests`. `unique`/`not_null`/`relationships`/`accepted_values` are the four built-in dbt generic tests — stable dbt-core practice.

---

_Last reviewed: 2026-05-30 by `claude`_
