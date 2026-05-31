---
description: Design a cost- and isolation-aware warehouse schema — pick the engine by workload (not brand), partition/cluster on the columns dashboards actually filter, lay the staging→marts contract, and make tenant_id both indexed and a clustering key.
argument-hint: "[the subject + workload, e.g. 'daily revenue facts for a 6-tenant SaaS on BigQuery']"
---

# Design a warehouse schema

You are running `/data-platform:design-warehouse-schema`. Design the analytical schema for what the user described (`$ARGUMENTS`), following this plugin's `database-setup-guide` + `etl-pipeline-engineer` discipline. The recurring failure is a schema that scans the whole table for one tenant's last 30 days and bills accordingly.

## When to use this

A new analytical store is being designed, or an existing one is too expensive / too slow per query. Not for the OLTP system-of-record table design (that's the multi-tenant database command) and not when the client is already on Snowflake/Databricks — there you use data sharing, not a new schema.

## Steps

1. **Pick the engine by workload, not brand** (`warehouse-select-by-workload-not-brand`): name the workload shape (OLTP-plus-reads vs embedded read-heavy vs genuine OLAP) and the engagement economics (ACV, viewer count, handoff owner) *first*, then take the cheapest option that serves it — Supabase Pro for non-Microsoft SMB, Fabric F2 for M365, DuckDB for embedded analytics. Snowflake/Databricks/Redshift Serverless are override-with-rationale below ~$25K ACV, not the default.
2. **Partition and cluster on the columns the dashboards filter** (`warehouse-partition-and-cluster-for-cost`): partition on the **date the dashboards window on** (the real `WHERE`/`GROUP BY` column, never an arbitrary load date), cluster on `tenant_id` first then the hottest dimension. Verify pruning actually fires by reading the query plan / dry-run bytes-scanned — a partition key the queries don't use buys nothing.
3. **Lay the staging→intermediate→marts contract** (`dbt-stage-then-mart-never-skip-the-layer`): staging is the only layer touching `{{ source() }}` (one model per source table, casts/renames/dedup here); marts reference only `ref()`. A mart reading a raw source is a layering defect the semantic layer will inherit.
4. **Make tenant_id both indexed and a clustering key** (`enforce-tenant-isolation-closest-to-data`): for multi-tenant facts, `tenant_id` is simultaneously the RLS-scanned column (index it in Postgres) and a warehouse clustering key — so the tenant filter prunes *and* the RLS scan stays cheap. Single-tenant? Document the missing-axis assumption so a future pivot doesn't inherit a silently-absent control.
5. **Define each metric once in the semantic layer** (`model-semantic-layer-single-source-of-truth`): the marts are the stable contract a Cube / dbt-MetricFlow / Power BI model reads — "revenue" gets one definition, one query plan, one access-control surface, never re-derived per widget.

## Guardrails

- Don't partition on a high-cardinality column (a UUID, a raw second-resolution timestamp) — too many tiny partitions costs more than it saves.
- Carry a retrieval date on every pricing claim ("Vendor X tier $Y/mo as of YYYY-MM-DD") — pricing moves quarterly.
- Any tenant_id schema change routes the isolation review through `ravenclaude-core/security-reviewer`; enterprise Fabric topology (lakehouse, capacity FinOps, medallion) hands off to `microsoft-fabric`.
