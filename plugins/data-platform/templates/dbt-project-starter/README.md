# dbt project starter

> Companion to `data-platform` plugin templates. Provides a 3-layer dbt project (staging / intermediate / marts) with source declarations, sample staging + mart models, profile examples, and engagement-ready configuration.
>
> **Last reviewed:** 2026-05-21
>
> **Used together with:**
> - `templates/airbyte-source-config.yaml` — feeds the raw_<source> schemas
> - `templates/database-schema-starter.sql` — the destination Postgres schema (with RLS)
> - `skills/connector-configuration/SKILL.md` — source-system specifics

## Layout

```
dbt-project-starter/
├── dbt_project.yml              # Project config (3-layer materialization, vars, tests)
├── profiles.yml.example         # Connection profiles (Postgres/Snowflake/BQ/Databricks)
├── models/
│   ├── staging/                 # stg_<source>__<entity> — views, thin renaming + casting
│   │   ├── _sources.yml         # Source declarations + freshness tests
│   │   └── stg_quickbooks__customers.sql  # Example
│   ├── intermediate/            # int_<entity>__<action> — ephemeral, composed logic
│   └── marts/                   # mart-layer + dim_ + fact_ — tables, dashboard-facing
│       ├── _schema.yml          # Tests + docs for marts
│       └── dim_customer.sql     # Example
├── macros/                      # Custom macros (often: tenant-aware surrogate keys)
├── tests/                       # Custom singular tests
└── seeds/                       # Reference CSVs (account hierarchies, etc.)
```

## Conventions

- **Naming:** `stg_<source>__<entity>` (staging), `int_<entity>__<action>` (intermediate), `dim_<entity>` / `fact_<grain>` / `mart_<domain>` (marts)
- **Materializations:** views (staging) → ephemeral (intermediate) → tables (marts)
- **Tests:** required on every mart's primary key + at least one not_null on a load-bearing attribute
- **Freshness:** sources have `warn_after: 26h, error_after: 48h` for daily-cadence ELT (tighten if hourly)

## Usage

1. **Copy the starter** into a new engagement's repo:
   ```bash
   cp -r data-platform/templates/dbt-project-starter/ ./my-engagement-dbt/
   cd my-engagement-dbt
   ```

2. **Replace placeholders:**
   - `{{client_slug}}` in `dbt_project.yml` and `profiles.yml.example` → your client's identifier
   - Update `_sources.yml` schemas to match what Airbyte / Fivetran populated

3. **Configure your profile:**
   ```bash
   cp profiles.yml.example ~/.dbt/profiles.yml
   # Edit + add real credentials (via env vars)
   ```

4. **Run:**
   ```bash
   dbt deps        # Install dbt-utils etc. (see packages.yml — add as needed)
   dbt seed        # Load reference CSVs if any
   dbt run         # Run all models (staging → intermediate → marts)
   dbt test        # Run all tests (including freshness on sources)
   ```

5. **Extend per engagement:**
   - Add staging models for each source entity needed
   - Add intermediate models for matching, dedup, derivation
   - Add mart models per dashboard surface
   - Common QBO engagement marts listed in `data-platform/knowledge/quickbooks-online-integration.md`

## Packages worth adding (in `packages.yml`)

```yaml
# packages.yml — install with: dbt deps
packages:
  - package: dbt-labs/dbt_utils
    version: ">=1.1.0"
  - package: calogica/dbt_date
    version: ">=0.10.0"
  - package: calogica/dbt_expectations
    version: ">=0.10.0"
```

## Multi-tenant pattern (when engagement is multi-tenant)

For multi-tenant engagements where dbt models flow into a tenant-scoped warehouse:

1. **Tenant-aware surrogate keys** — include `tenant_id` in `generate_surrogate_key` calls
2. **Filter at staging** — every `stg_<source>__<entity>` filters `WHERE tenant_id = '{{ var("current_tenant_id") }}'` if running per-tenant builds
3. **OR: tenant_id column on every fact/dim** — surfaces to the dashboard layer for RLS
4. **dbt + Postgres RLS coordination** — dbt's connection role typically has BYPASSRLS for the mart layer; the read-time role for the dashboard does NOT (per `templates/database-schema-starter.sql`)

See `data-platform/skills/rls-policy-authoring/SKILL.md` for the closeness-to-data invariant and how dbt fits.

## Refresh triggers for this starter

- dbt-core major version bump (template targets 1.7+)
- New layer convention adopted by the team
- Engagement-specific materialization tuning (Snowflake / Databricks defaults differ)
- New source pattern repeated across engagements (promote into the starter)
