# data-orchestration

> The **orchestration layer** for Claude Code — the team that decides *what runs your data pipelines* and *builds the DAGs/assets that run them*. Two agents: the **orchestration-architect** (chooses the engine + scheduling model) and the **pipeline-orchestration-engineer** (builds correct, re-runnable, observable pipelines).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Airflow vs Dagster vs Prefect for our workload?" | A decision-tree-driven engine choice + scheduling model + executor + the conditions that would flip it |
| "Self-host or use MWAA / Cloud Composer / Azure Data Factory?" | A managed-vs-OSS verdict with the lock-in and ops trade-offs named |
| "Design the DAG / asset graph for this pipeline." | A minimal dependency graph + partition grain + scheduling/trigger choice, captured in a design doc |
| "Our pipeline isn't safe to re-run — fix it." | Idempotency rewrites (deterministic keys, overwrite-by-partition) + retries with exponential backoff |
| "We need to backfill last month — safely." | A backfill runbook: scope, idempotency precondition, concurrency cap, monitoring, rollback |
| "Alert us when a dataset goes stale or a DAG misses its SLA." | Freshness-SLA definitions + SLA-miss alerting + a lineage/blast-radius view |

**Two rules it never breaks:** *workload before brand* (the orchestrator is the conclusion, not the premise), and *no idempotency proof → no retry policy.*

## What's inside

- **2 agents** — `orchestration-architect` (chooses the engine/scheduling/executor) and `pipeline-orchestration-engineer` (builds DAGs/assets, idempotency, retries, backfills, SLAs, lineage).
- **3 skills** — `choose-orchestrator`, `design-dag-and-dependencies`, `handle-backfills-and-retries`.
- **2 knowledge files** — a Mermaid orchestrator-selection decision tree (+ trade-off table) and a 2026 orchestration-patterns reference (idempotency, retries/backoff, partitioning, catchup/backfill, scheduling models, freshness SLAs, lineage).
- **2 templates** — a DAG/asset design doc and a backfill runbook.

## Where it sits in the data stack

```
data-platform              →  ingest / connectors / warehouse / BI  ("get the data in & served")
analytics-engineering      →  dbt transforms                        ("model the data")
data-streaming-engineering →  real-time Kafka / Flink               ("sub-minute latency")
data-orchestration (HERE)  →  RUN & SCHEDULE all of the above       ("what runs it, when, and safely")
```

This plugin is the **scheduling/run layer** the others plug into. It runs the dbt models (analytics-engineering), loads from the connectors/warehouse (data-platform), and hands off anything sub-minute to streaming.

## Engine stance

Engine-agnostic on concepts (DAGs vs software-defined assets, sensors vs data-aware scheduling, catchup/backfill, idempotency, retries+backoff, partitioning, freshness SLAs, lineage), fluent across **Apache Airflow, Dagster, and Prefect**, with cloud-native options (AWS MWAA / Step Functions, GCP Cloud Composer / Workflows, Azure Data Factory) and **Temporal-for-data** for durable workflows. Engine versions and managed-service parity carry retrieval dates — re-verify before pinning in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install data-orchestration@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
