# When the client is already on a lakehouse, use data sharing — don't build a pipeline

**Status:** Pattern — strong default whenever both source and destination sit on the same (or share-compatible) lakehouse; deviate only when a real transform/landing requirement makes a share insufficient.

**Domain:** ELT / no-pipeline architecture

**Applies to:** `data-platform`

---

## Why this exists

The most invisible win in a dashboard engagement is *not building the pipeline at all*. When a client says "our data is already in Snowflake" or "...in Databricks," the reflex to stand up an Airbyte/Fivetran pipeline copies data that's already where you need it — adding an ELT cost line, a sync-latency window, a freshness SLA to operate, and a second copy to keep consistent, all for zero benefit. **Snowflake Data Sharing** and **Databricks Delta Sharing** expose the source data to your analytics layer with zero ETL, zero copy, and near-zero latency, across regions and clouds. Most SMB consultants don't reach for it because it's outside the iPaaS mental model — which is exactly why surfacing it is high-leverage. The rule is simply: before designing a pipeline, ask where the data already lives; if it's on a share-capable lakehouse, the share *is* the integration.

## How to apply

Check the source platform first. If it's lakehouse-resident, grant a share into your analytics account instead of configuring a connector.

```sql
-- Snowflake: provider grants a share; consumer mounts it as a read-only DB. No ELT.
-- (provider side)
CREATE SHARE revenue_share;
GRANT USAGE ON DATABASE prod TO SHARE revenue_share;
GRANT SELECT ON prod.public.fct_orders TO SHARE revenue_share;
-- (consumer side) the shared data appears as a database — query it like any table.
CREATE DATABASE client_shared FROM SHARE provider_acct.revenue_share;
```

```python
# Databricks Delta Sharing: open protocol; read the share directly, no copy.
import delta_sharing
df = delta_sharing.load_as_pandas("config.share#prod.default.fct_orders")
```

**Do:**
- Ask "where does the data already live?" before designing any pipeline.
- Use Snowflake Data Sharing / Delta Sharing when source and destination are on (or compatible across) the same lakehouse — it replaces the ELT line entirely.
- Surface this proactively whenever a client mentions Snowflake/Databricks — it's the underused, cost-saving answer.
- Document the share-grant management as the "handoff" artifact (there's no pipeline runbook to write).

**Don't:**
- Stand up an Airbyte/Fivetran pipeline to copy data that's already in a share-capable lakehouse.
- Treat a share as something to operate like a pipeline — there's no sync job, no freshness SLA you own.
- Force a share when the engagement genuinely needs to *land and transform* the data in a different warehouse (then it's a real pipeline).

## Edge cases / when the rule does NOT apply

- **Cross-platform with no share path** — source on Snowflake, mandatory destination on Postgres for a Supabase-embedded dashboard → a pipeline (or a one-hop export) is unavoidable; the share doesn't bridge incompatible engines.
- **Heavy transform required before exposure** — if the deliverable needs dbt-modeled marts the provider doesn't expose, you still land + transform; the share can be the *source* of an ELT, but you're back to a pipeline for the T.
- **Provider won't grant a share** (org policy, security posture) — fall back to ELT; document why the cheaper path was unavailable.

## See also

- [`./etl-elt-load-then-transform-in-warehouse.md`](./etl-elt-load-then-transform-in-warehouse.md) — the pipeline shape this rule lets you skip
- [`./warehouse-select-by-workload-not-brand.md`](./warehouse-select-by-workload-not-brand.md) — "client already on a lakehouse" is a first-class branch there too
- [`../knowledge/ipaas-connector-landscape-2026.md`](../knowledge/ipaas-connector-landscape-2026.md) — "Direct warehouse-to-warehouse sharing (skip the iPaaS)"
- [`../knowledge/data-platform-decision-trees.md`](../knowledge/data-platform-decision-trees.md) — the ELT-tool tree's first branch
- [`../agents/etl-pipeline-engineer.md`](../agents/etl-pipeline-engineer.md) — owns this recommendation

## Provenance

Distilled from CLAUDE.md house opinion #10 ("Don't reinvent the warehouse … recommend data sharing, not a new ELT pipeline"), the `etl-pipeline-engineer.md` data-sharing opinion, and `ipaas-connector-landscape-2026.md` ("Direct warehouse-to-warehouse sharing … the right answer is often 'we'll use a data share, not build a pipeline.'"). `[verify-at-build]` Snowflake `CREATE SHARE` / Delta Sharing `delta_sharing` API surface — confirm against current Snowflake / Databricks docs before quoting in code; the sharing primitives have been evolving (Iceberg share support, 2025/2026).

---

_Last reviewed: 2026-05-30 by `claude`_
