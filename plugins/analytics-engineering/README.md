# Analytics Engineering (dbt)

The **analytics-engineering** plugin — the transformation layer between raw warehouse data and trustworthy analytics — dbt modeling (staging -> marts), a governed semantic layer, and data-quality tests/contracts -- distinct from data-platform's ingestion/BI and database-engineering's OLTP.

## Agents

- **`analytics-engineer`** — dbt modeling: the staging/intermediate/marts layering, materialization choice, incremental models, the Kimball-vs-OBT decisions, model structure, refs/sources, and warehouse-aware SQL
- **`semantic-layer-engineer`** — The governed semantic/metrics layer: one definition per metric (revenue, active user, churn), metrics-as-code (dbt Semantic Layer / MetricFlow or equivalent), dimensions/entities, and the contract every BI tool consumes
- **`data-quality-testing-engineer`** — Data quality in the transform layer: dbt tests (not_null/unique/accepted_values/relationships), source freshness, model contracts, custom/singular tests, anomaly detection, and gating the warehouse in CI and production

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install analytics-engineering@ravenclaude
```

## Seams

- **Ingestion/ELT into the warehouse and the warehouse choice/provisioning** → `data-platform` (Airbyte/Fivetran, warehouse selection); this team transforms what's landed.
- **The transactional OLTP database (schema, indexes, migrations)** → `database-engineering`; we work in the analytics warehouse (OLAP), not the app's DB.
- **BI/dashboards consuming the marts and semantic layer** → `tableau` / `data-platform` (embedded analytics).
- **Enterprise Microsoft lakehouse / Direct Lake semantic models** → `microsoft-fabric` (we're the warehouse-neutral dbt lane).
- **Statistical validity of a metric ('is this difference real?')** → `applied-statistics`; we ensure the number is *correct and consistent*, they say if it's *significant*.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
