# Analytics Engineering — best-practice docs

Named, citable rules for the `analytics-engineering` plugin's specialists. Each file is **one rule**, grounded in this plugin's house opinions, knowledge bank, and the dbt/semantic-layer craft. Read, applied, and cited as a whole.

---

## Index

_22 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`contract-the-consumer-boundary.md`](./contract-the-consumer-boundary.md) | Absolute rule | Enforcing a published mart API so BI tools and downstream consumers break loudly on schema changes. |
| [`one-definition-per-metric.md`](./one-definition-per-metric.md) | Absolute rule | A KPI is computed differently in two dashboards — find and centralize the governed definition. |
| [`test-data-like-code.md`](./test-data-like-code.md) | Absolute rule | A dbt model ships without tests — add not_null, unique, accepted_values, and relationships before merge. |
| [`transform-in-layers.md`](./transform-in-layers.md) | Absolute rule | A model mixes raw source references, business logic, and mart outputs — split it into staging/intermediate/marts. |
| [`state-the-grain-explicitly.md`](./state-the-grain-explicitly.md) | Absolute rule | A mart's grain is ambiguous — state it in the model description and enforce it with a unique test. |
| [`make-transforms-idempotent-and-rerunnable.md`](./make-transforms-idempotent-and-rerunnable.md) | Absolute rule | A dbt model produces different results when re-run — fix it so rebuilds are safe. |
| [`key-incremental-models-correctly.md`](./key-incremental-models-correctly.md) | Absolute rule | An incremental model is silently dropping or duplicating rows — verify the unique_key covers all update scenarios. |
| [`stay-in-the-transform-lane.md`](./stay-in-the-transform-lane.md) | Absolute rule | A request crosses into ingestion (data-platform) or OLTP (database-engineering) — route it to the right team. |
| [`models-are-owned-and-documented.md`](./models-are-owned-and-documented.md) | Absolute rule | A mart has no owner or description — add both before any BI tool is connected to it. |
| [`run-the-dbt-project-in-ci.md`](./run-the-dbt-project-in-ci.md) | Absolute rule | CI runs only dbt compile — add dbt build with tests so the mart gate is enforced on every PR. |
| [`gate-on-source-freshness.md`](./gate-on-source-freshness.md) | Absolute rule | A build proceeds on stale source data — add freshness checks that fail the build, not just warn. |
| [`materialize-by-the-trade.md`](./materialize-by-the-trade.md) | Absolute rule | A large fact is view-materialized (slow) or a small lookup is table-materialized (wasteful) — match materialization to workload. |
| [`document-col-descriptions-in-schema-yml.md`](./document-col-descriptions-in-schema-yml.md) | Absolute rule | A mart column has no description — add it to schema.yml before merging the model. |
| [`never-ref-a-source-outside-staging.md`](./never-ref-a-source-outside-staging.md) | Absolute rule | An intermediate or mart model contains a `{{ source(...) }}` reference — move it to a staging model. |
| [`use-exposures-to-declare-downstream-consumers.md`](./use-exposures-to-declare-downstream-consumers.md) | Pattern | A mart is being refactored and it is unclear which dashboards or BI tools will break — add exposures. |
| [`metrics-as-code-not-as-dashboard-sql.md`](./metrics-as-code-not-as-dashboard-sql.md) | Absolute rule | A business KPI is re-derived as SQL inside a dashboard tool — move the definition to the semantic layer. |
| [`set-model-owner-in-meta.md`](./set-model-owner-in-meta.md) | Absolute rule | A mart has no owner in its meta block — add one before the first external consumer is connected. |
| [`test-relationships-across-mart-joins.md`](./test-relationships-across-mart-joins.md) | Absolute rule | A mart FK join produces null or inflated rows — add a dbt relationships test to every FK column. |
| [`separate-dev-and-prod-targets.md`](./separate-dev-and-prod-targets.md) | Absolute rule | A developer ran dbt to the production schema from a local machine — separate dev and prod targets, prod deploys from CI only. |
| [`anomaly-test-row-count-and-freshness.md`](./anomaly-test-row-count-and-freshness.md) | Pattern | Schema tests pass but a mart has suspiciously fewer rows than expected — add row-count drift and freshness anomaly tests. |
| [`stage-one-source-one-file.md`](./stage-one-source-one-file.md) | Absolute rule | A staging model joins two source tables — move the join to intermediate. |
| [`contract-break-warn-not-silent.md`](./contract-break-warn-not-silent.md) | Absolute rule | A mart column was renamed and downstream consumers silently broke — enforce dbt model contracts on published boundaries. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — analytics-engineering team constitution (§2 house opinions, §3 seams).
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
