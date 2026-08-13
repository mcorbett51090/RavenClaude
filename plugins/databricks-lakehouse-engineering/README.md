# databricks-lakehouse-engineering

> The **Databricks lakehouse engineering layer** for Claude Code — the team that answers _"how do we build this on Databricks correctly, governably, and affordably — without over-engineering it into an always-on stream or an over-partitioned small-file swamp?"_ Two agents: the **lakehouse-architect** (medallion layering, Delta table & partitioning strategy, batch-vs-streaming, Unity Catalog governance, and the DBU cost/sizing envelope) and the **databricks-platform-engineer** (PySpark/Spark SQL, Delta MERGE/CDC, DLT, Auto Loader/Structured Streaming, Jobs/Workflows, and evidence-driven diagnosis of the shuffle/skew/spill/OOM & small-file failures).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "How should we structure this on Databricks?" | A medallion (bronze/silver/gold) design tied to the reader and freshness SLO, with a per-layer Delta table & partitioning/clustering strategy |
| "We get events from Kafka — should this be streaming?" | A batch-vs-streaming call driven by the actual SLO (batch is the default; Auto Loader / Structured Streaming / DLT only when a real sub-hour SLO forces it), with the checkpoint/exactly-once implication named |
| "How do we lay out this Delta table?" | A partition/liquid-clustering choice matched to real query filters (never a high-cardinality column → small-file explosion), plus OPTIMIZE/Z-ORDER/VACUUM cadence and the MERGE/CDC vs append/overwrite write pattern |
| "How do we set up Unity Catalog?" | A catalog/schema layout, managed-vs-external decision, grants to **groups** (not users), lineage/audit, and PII tagging — designed in, not bolted on |
| "What cluster do we need and what will it cost?" | A compute recommendation (jobs vs all-purpose vs serverless, SQL warehouse sizing, Photon where it pays), an autoscaling + spot + auto-termination policy, and an order-of-magnitude DBU estimate with the top cost drivers named |
| "This Spark job is spilling to disk and takes hours." | An **evidence-grounded** root-cause diagnosis from the Spark UI (skew, shuffle spill, small files, missing broadcast, driver OOM) and the specific fix — not a guessed tuning knob |
| "Our Databricks bill is too high." | The DBU leak points (idle always-on compute, all-purpose for jobs, oversized warehouses, un-compacted small files, Photon-on-a-UDF-job) and the fixes, order-of-magnitude quantified |

**Two rules it never breaks:** _batch until a real SLO forces streaming_ (real-time is usually a wish, not a requirement), and _read the Spark UI before you tune_ (the skewed stage and the spilling task are right there — guessing wastes cluster hours).

## What's inside

- **2 agents** — `lakehouse-architect` (layering, table strategy, batch-vs-streaming, Unity Catalog governance, compute/DBU envelope) and `databricks-platform-engineer` (PySpark/Spark SQL, Delta MERGE/CDC, DLT, Auto Loader/Structured Streaming, Jobs/Workflows, and evidence-driven job diagnosis + cost reduction).
- **2 skills** — `design-medallion-lakehouse`, `tune-spark-and-costs`.
- **2 knowledge files** — a Mermaid decision-tree bank (batch-vs-streaming, medallion, Delta partitioning, slow-job symptom→fix, compute/DBU) and a dated 2026 patterns reference (Delta discipline, Spark performance without guesswork, Auto Loader/Streaming, DLT, Unity Catalog, Jobs, DBU cost wins, tooling map).
- **1 template** — a lakehouse design (readers/SLOs → layering → table strategy → governance → cost envelope → seams → verify-at-use list).

## Where it sits among the data plugins

```
microsoft-fabric            →  Microsoft Fabric / OneLake            (a DIFFERENT platform)
data-platform               →  generic, non-Databricks ETL scaffolding
data-orchestration          →  Airflow/Dagster & complex cross-system DAGs
analytics-engineering       →  dbt / semantic-layer modeling of the GOLD layer
ml-engineering              →  classical model training / serving lifecycle
databricks-lakehouse-engineering (HERE)  →  DESIGN & BUILD the lakehouse on Databricks
                                            ("medallion + Delta + Unity Catalog + Spark jobs, correct & cheap")
```

This plugin **designs and builds the Databricks lakehouse** and **feeds** those teams rather than replacing them: it hands the gold-layer modeling to `analytics-engineering`, complex orchestration to `data-orchestration`, org privacy policy to `data-governance-privacy`, and the ML lifecycle to `ml-engineering` — while owning the medallion design, Delta table craft, Spark performance, governance layout, and DBU cost discipline that make the lakehouse trustworthy and affordable.

## Domain stance

Cost-and-correctness-first: start from the reader and the freshness SLO, default to batch, size compute to the workload, and design governance in. Fluent across Delta Lake (MERGE/CDC, partitioning vs liquid clustering, OPTIMIZE/Z-ORDER/VACUUM), Spark/PySpark performance (AQE, skew, shuffle spill, broadcast, small files, driver OOM — diagnosed from the Spark UI, not guessed), ingestion (Auto Loader, Structured Streaming, DLT), Unity Catalog governance, and Jobs/Workflows orchestration — and militant about the DBU leak points (idle compute, all-purpose-for-jobs, over-partitioning, Photon-on-the-wrong-job). DBR versions, feature GA status, and DBU/list pricing carry retrieval dates — re-verify before a stakeholder commitment.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install databricks-lakehouse-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
