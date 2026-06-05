# Use separate dbt targets for dev and prod — never build to production from a local run

**Status:** Absolute rule
**Domain:** dbt / environment management
**Applies to:** `analytics-engineering`

---

## Why this exists

A local `dbt run` that writes to the production schema is an unreviewed deploy. There is no PR review, no CI test gate, no row-count anomaly check — just a developer's laptop overwriting the mart that a customer-facing dashboard reads. Even a "quick fix" in production creates a window where the mart is in a partially-rebuilt state and dashboards serve wrong data. The dev/prod target separation is the minimum guardrail: dev builds write to a developer-specific schema, and production deploys run only from CI on a reviewed branch.

## How to apply

In `profiles.yml`:

```yaml
analytics:
  target: dev
  outputs:
    dev:
      type: postgres
      host: "{{ env_var('DBT_HOST') }}"
      user: "{{ env_var('DBT_DEV_USER') }}"
      password: "{{ env_var('DBT_DEV_PASSWORD') }}"
      database: analytics
      schema: "dev_{{ env_var('DBT_USER', 'local') }}"   # dev_alice, dev_bob
      threads: 4

    prod:
      type: postgres
      host: "{{ env_var('DBT_HOST') }}"
      user: "{{ env_var('DBT_PROD_USER') }}"            # dbt_build_role credentials
      password: "{{ env_var('DBT_PROD_PASSWORD') }}"
      database: analytics
      schema: marts
      threads: 8
```

**CI pipeline (`.github/workflows/dbt.yml`):**
```yaml
- run: dbt build --target prod --profiles-dir .
  env:
    DBT_HOST: ${{ secrets.DBT_HOST }}
    DBT_PROD_USER: ${{ secrets.DBT_PROD_USER }}
    DBT_PROD_PASSWORD: ${{ secrets.DBT_PROD_PASSWORD }}
```

The `prod` credentials exist only in CI secrets — no developer has them locally.

**Do:**
- Default the `profiles.yml` target to `dev`.
- Make the `prod` connection credentials available only in CI (never in `.env` files committed to the repo).
- Run `dbt build --target dev` locally for development; let CI run `--target prod`.

**Don't:**
- Store prod credentials in a `.env` file on developer machines.
- Run `dbt run --target prod` from a local machine, even to "hot-fix" a mart.
- Use the same schema for dev and prod builds.

## Edge cases / when the rule does NOT apply

- A single-person engagement on a small non-production database may combine dev and prod if there are no customers reading the dashboard yet. Document the deviation and enforce the separation before the first customer uses the dashboard.

## See also

- [`../agents/analytics-engineer.md`](../agents/analytics-engineer.md) — sets up profiles and CI configuration
- [`./run-the-dbt-project-in-ci.md`](./run-the-dbt-project-in-ci.md) — the CI gate rule that this target separation enables

## Provenance

Codifies the `skills/dbt-project-scaffolding/SKILL.md` (dev/prod env-promotion via per-schema target) as a standalone rule. Standard dbt multi-environment practice.

---

_Last reviewed: 2026-06-05 by `claude`_
