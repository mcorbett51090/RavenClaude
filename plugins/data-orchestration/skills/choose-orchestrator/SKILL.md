---
name: choose-orchestrator
description: Pick the right data-pipeline orchestrator for a described workload by traversing the orchestrator-selection decision tree (workload shape → latency → asset-centric vs task-centric → team/ops capacity → cloud lock-in → engine), then return the recommended engine, its scheduling model, its executor/runtime, the trade-offs, and the conditions that would flip the choice. Reach for this when the user asks "Airflow vs Dagster vs Prefect?", "self-host or managed (MWAA/Composer/ADF)?", or "what should run our pipelines?". Used by `orchestration-architect` (primary).
---

# Skill: choose-orchestrator

> **Invoked by:** `orchestration-architect` (primary). Also consulted by `pipeline-orchestration-engineer` when a build reveals the chosen engine can't express a required pattern.
>
> **When to invoke:** "Airflow vs Dagster vs Prefect?"; "should we self-host or use MWAA / Cloud Composer / Azure Data Factory?"; "Step Functions or a real orchestrator?"; any "what should run/schedule our pipelines?" question.
>
> **Output:** the recommended orchestrator + its scheduling model + its executor/runtime + the trade-offs + the 1-2 flip conditions that would change the answer.

## Procedure

1. **Restate the workload in the tree's terms.** Capture: data **volume & cadence**, the **latency target** (minutes/hours vs sub-minute), **dependency complexity** (linear vs cross-team DAG mesh), whether the mental model is **asset/data-centric or task-centric**, the **team size & ops capacity**, and the **existing cloud / lock-in tolerance**.
2. **Gate latency first.** If the real requirement is sub-minute/continuous, this is **not** an orchestration problem — route to `data-streaming-engineering` (Kafka/Flink) and stop. Orchestrators schedule batch/micro-batch work.
3. **Traverse the decision tree** in [`../../knowledge/orchestrator-selection-decision-tree.md`](../../knowledge/orchestrator-selection-decision-tree.md) against those inputs:
   - asset/lineage-first + typed I/O + local dev → **Dagster** (software-defined assets),
   - large cross-team DAG estate + mature scheduling/backfill + big ops team → **Apache Airflow**,
   - dynamic Python-native flows + light ops → **Prefect**,
   - notebook/low-code data team → **Mage**,
   - long-running, stateful, exactly-once *workflows* (not batch tables) → **Temporal-for-data**,
   - "we just want managed, minimal ops, already on a cloud" → **MWAA / Cloud Composer (managed Airflow)** or **Azure Data Factory**; simple state-machine glue → **AWS Step Functions / GCP Workflows**.
4. **Name the scheduling model**, per pipeline: cron (fixed cadence) / event-sensor (external readiness; deferrable operators) / data-aware-asset (run when upstream data is fresh — Airflow Datasets, Dagster asset materialization, Prefect automations).
5. **Choose the executor/runtime:** Local (small) / Celery (horizontal scale) / Kubernetes (isolation, bursty) / serverless (managed). State where the scheduler + metadata DB live.
6. **Decide managed vs OSS** explicitly: managed buys ops time and adds lock-in; self-host buys control/cost/portability and costs ops headcount.
7. **State the flip conditions** — the 1-2 facts that, if different, change the answer (e.g., "if the team had no Kubernetes capacity, drop the KubernetesExecutor recommendation").

## Worked example

> User: "We have ~40 nightly tables with strong cross-table dependencies, a 3-person data team already on GCP, and we care a lot about which upstream a failure breaks. Airflow or Dagster?"

- Asset/lineage-first ("which upstream broke") + small team + GCP → **Dagster software-defined assets** for the lineage/blast-radius model, **or managed Airflow (Cloud Composer)** if the team prefers the larger ecosystem and doesn't want to operate Dagster.
- Scheduling: **data-aware / asset materialization** (run a table when its upstreams are fresh), not blind 6am cron.
- Executor: small team on GCP → managed runtime; avoid self-managing a Celery cluster.
- **Flip condition:** if the estate grows to hundreds of cross-team DAGs with dedicated platform engineers, Airflow's ecosystem/ops maturity starts to win.

## Guardrails

- Never name an orchestrator before traversing the tree — workload before brand.
- Sub-minute latency → not orchestration; route to streaming and say so.
- Don't recommend Temporal for batch table builds, or Step Functions/ADF where heavy DAG scheduling/backfill is the core need.
- Volatile claims (versions, managed-service feature parity, pricing) carry a **retrieval date** and are re-verified before a client commitment. See [`../../knowledge/orchestration-patterns-2026.md`](../../knowledge/orchestration-patterns-2026.md).
