# Default to ELT — land raw, then transform in the warehouse — not ETL

**Status:** Pattern — strong default for every dashboard engagement; deviate only with a written reason (a hard pre-load redaction/compliance requirement).

**Domain:** ELT / pipeline architecture

**Applies to:** `data-platform`

---

## Why this exists

The classic ETL shape — transform in a middle tier, then load only the shaped result — throws away the raw source and couples the pipeline to today's understanding of the data. The modern shape is **ELT**: extract, **load the raw source verbatim** into the warehouse, then transform *in* the warehouse with dbt where the compute is cheap, version-controlled, and testable. The payoff is replayability — when a mart's logic is wrong (and it will be), you re-run dbt against raw rows that are already landed; you do not re-pull QBO at 10 req/s or re-hit a rate-limited API. Airbyte and Fivetran are EL tools by design (they land raw `_airbyte_*` / Fivetran-staged tables); dbt is the T. Bolting transform logic into the ingestion layer is fighting both tools.

## How to apply

Land the source untouched into a `*_raw` schema; let dbt staging own the first transform. Never let a connector pre-shape.

```
Airbyte / Fivetran  ──EL──▶  quickbooks_raw.customers   (verbatim, _airbyte_extracted_at)
                                        │
                              dbt staging  {{ source(...) }}  ── rename, cast, light clean
                                        │
                              dbt intermediate / marts  ── business logic, joins, aggregation
                                        │
                              BI / Cube / Metabase reads marts (never raw)
```

```yaml
# The connector's only job is to land raw. Transform belongs in dbt, downstream.
# models/staging/quickbooks/stg_quickbooks__customers.sql
select
  id::text                         as customer_id,
  lower(trim(display_name))        as customer_name,
  (balance)::numeric(18,2)         as balance,
  _airbyte_extracted_at            as loaded_at
from {{ source('quickbooks_raw', 'customers') }}
```

**Do:**
- Land raw verbatim, then transform with dbt staging → intermediate → marts (the [`dbt-project-scaffolding`](../skills/dbt-project-scaffolding/SKILL.md) contract).
- Keep raw immutable and retained — it is the replay substrate when mart logic changes.
- Push aggregation and joins as far downstream (warehouse / semantic layer) as the cost model allows.

**Don't:**
- Encode business logic in the connector or a pre-load script — that logic is invisible to `dbt build` and untestable.
- Drop or reshape raw columns on the way in "to save space"; storage is cheaper than a re-pull.
- Treat a webhook event stream as if it were a CRUD table — land the events raw, reconstruct state in dbt.

## Edge cases / when the rule does NOT apply

- **Pre-load redaction for compliance** — when PII/PHI must never touch the warehouse at all (a contractual or HIPAA boundary), redact/tokenize *before* load. That is a deliberate ETL exception; route through `ravenclaude-core/security-reviewer` and document it.
- **Case A (Evidence.dev portfolio)** — SQL fenced in `.md` pages *is* the transform layer; there is no separate raw schema to land into.
- **Snowflake/Databricks data sharing** — no pipeline at all; the data is already in the lakehouse (house opinion #10).

## See also

- [`./dbt-stage-then-mart-never-skip-the-layer.md`](./dbt-stage-then-mart-never-skip-the-layer.md) — the in-warehouse transform discipline this rule lands into
- [`./ingest-idempotent-and-replayable.md`](./ingest-idempotent-and-replayable.md) — why raw retention makes replay safe
- [`../skills/dbt-project-scaffolding/SKILL.md`](../skills/dbt-project-scaffolding/SKILL.md) — the sources → staging → marts contract
- [`../agents/etl-pipeline-engineer.md`](../agents/etl-pipeline-engineer.md) — owns the EL layer; routes the T to dbt

## Provenance

Distilled from `etl-pipeline-engineer.md` ("dbt Core integration — orthogonal to the iPaaS choice; ships with every engagement"; "schema-on-read … when the dashboard's value depends on dimensional modeling — the dbt layer is non-negotiable") and the `dbt-project-scaffolding` skill's layer rules (staging references sources only). ELT-over-ETL is the dbt-ecosystem standard; the redaction exception is the only documented ETL case.

---

_Last reviewed: 2026-05-30 by `claude`_
