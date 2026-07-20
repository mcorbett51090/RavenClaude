---
name: design-medallion-lakehouse
description: "Design a Databricks lakehouse from the query and freshness SLO backward: the medallion layering (what earns bronze/silver/gold), the Delta table & partitioning strategy per layer (low-cardinality partition vs liquid clustering, OPTIMIZE/Z-ORDER/VACUUM cadence, MERGE/CDC vs append/overwrite write pattern), the batch-vs-streaming call (scheduled batch is the default; Auto Loader / Structured Streaming / DLT only for a real sub-hour SLO), the Unity Catalog governance layout (catalog/schema, managed vs external, grants to groups, PII tagging), and the compute + DBU cost envelope. Reach for this when the ask is 'how should we structure this on Databricks?', 'bronze/silver/gold + table layout', 'batch or streaming?', or 'Unity Catalog setup'. Used by `lakehouse-architect` (primary)."
---

# Skill: design-medallion-lakehouse

> **Invoked by:** `lakehouse-architect` (primary). Consulted by `databricks-platform-engineer` for the layer/table contract the code must honor.
>
> **When to invoke:** "how should we structure this on Databricks?"; "bronze/silver/gold + how to lay out the Delta tables"; "batch, streaming, Auto Loader, or DLT?"; "how do we set up Unity Catalog?"; "what compute and what will it cost?"
>
> **Output:** a medallion design + per-layer Delta table strategy + batch-vs-streaming call + Unity Catalog governance layout + compute/DBU cost envelope, captured in the lakehouse design template.

## Procedure

1. **Start from the reader and the SLO, not the tool.** Who queries this, at what shape, and how fresh must it be? Write those down first — the whole design flows from them. Traverse [`../../knowledge/databricks-decision-tree.md`](../../knowledge/databricks-decision-tree.md).
2. **Run the batch-vs-streaming gate (Tree 1).** Default to a scheduled **batch** job. Only choose Auto Loader (files landing), Structured Streaming (continuous events), or DLT (declarative managed) when a **real sub-hour SLO** forces it — and name the checkpoint/trigger/exactly-once implication when you do.
3. **Layer with the medallion pattern (Tree 2).** Bronze = raw, append-only, replayable. Silver = conformed, deduped, validated, typed. Gold = serving tables shaped to the reader. Justify each layer by what it earns; don't collapse a replay-valuable hop, don't add a gold table no one reads.
4. **Design each Delta table for its queries (Tree 3).** Partition **only** on a low-cardinality column that filters real queries — or use liquid clustering (verify GA/behavior at use). Never partition on a high-cardinality column (small-file explosion). Name file-size target, `OPTIMIZE`/`Z-ORDER`/`VACUUM` cadence, and the write pattern (MERGE/upsert/CDC vs append vs overwrite).
5. **Lay out Unity Catalog governance from the start.** Catalog-per-env or per-domain, schema boundaries, managed vs external tables/volumes, **grants to groups not users**, lineage/audit, and PII tagging. Retrofitting governance is expensive.
6. **Set the compute & DBU envelope (Tree 5).** Jobs compute for jobs, serverless/right-sized SQL warehouse for BI, Photon where it pays. Autoscaling bounds + spot + **auto-termination**. Give an order-of-magnitude DBU estimate and name the top cost drivers. Mark all pricing **verify-at-use + dated**.
7. **State the seams and flip conditions.** dbt gold modeling → `analytics-engineering`; external orchestration → `data-orchestration`; org privacy policy → `data-governance-privacy`; ML lifecycle → `ml-engineering`; **Fabric/OneLake → `microsoft-fabric`**. Name the 1-2 facts that would flip each call.

## Worked example

> User: "We get order events from Kafka and want a dashboard of daily revenue by region, plus the raw data kept for audits. Build it on Databricks."

- **Reader & SLO:** BI dashboard, refreshed **daily** is fine; audit needs raw retained. No sub-hour requirement.
- **Batch-vs-streaming (Tree 1):** despite the Kafka source, the SLO is daily → a **scheduled batch read** (or `Trigger.AvailableNow` stream-once) is cheaper than an always-on stream. Don't reflex "streaming" from "Kafka."
- **Layering (Tree 2):** Bronze = raw Kafka payloads appended (the audit anchor). Silver = parsed, deduped, typed orders (MERGE on order_id). Gold = `daily_revenue_by_region` aggregate shaped for the dashboard.
- **Table design (Tree 3):** silver partitioned by `order_date` (low-cardinality, filters queries); **not** by `order_id` (high-cardinality → tiny files). `OPTIMIZE`/`Z-ORDER (region)` nightly; `VACUUM` at safe retention. Gold overwritten daily.
- **Unity Catalog:** `prod.orders` catalog/schema; grants to the analytics group; PII (customer id) tagged and masked in gold.
- **Compute/DBU:** a small jobs-compute cluster on a nightly schedule with auto-termination; a right-sized SQL warehouse (auto-stop) for the dashboard; Photon on for the SQL aggregate. Top cost risk: leaving the warehouse always-on. (DBU figures verify-at-use.)
- **Seams:** if analysts want to model the gold layer in dbt → `analytics-engineering`.

## Guardrails

- **Batch is the default** — streaming is earned by a real sub-hour SLO, not the word "real-time."
- **Never over-partition** — a high-cardinality partition column is the most common self-inflicted small-file wound.
- **Governance is designed in, not bolted on** — Unity Catalog layout + grants-to-groups + PII tagging from the start.
- **Auto-terminate all compute** — idle clusters/warehouses are the top DBU leak.
- **Every runtime/feature/pricing fact carries a retrieval date + verify-at-use** — DBR versions, liquid clustering/predictive-optimization GA, and DBU pricing move. See [`../../knowledge/databricks-patterns-2026.md`](../../knowledge/databricks-patterns-2026.md).
- **The design is the architect's; the code, dbt modeling, org policy, and ML lifecycle leave this skill** — route to `databricks-platform-engineer` / `analytics-engineering` / `data-governance-privacy` / `ml-engineering`.
