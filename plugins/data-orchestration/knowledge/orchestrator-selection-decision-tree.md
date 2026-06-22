# Knowledge — Orchestrator selection decision tree

> **Last reviewed:** 2026-06-21 · **Confidence:** Medium-High (consensus on the OSS vs managed and asset-vs-task framing; **version/feature-parity claims are volatile — re-verify before a client commitment**).
> The most-asked orchestration question is "what should run our pipelines — Airflow, Dagster, Prefect, or a cloud-native service?". This is the decision tree the `orchestration-architect` traverses **before** naming an engine, plus the trade-off table and the seams to adjacent plugins.

The agent's discipline: **name the workload requirements first, name the engine second.** Sub-minute/continuous latency is not an orchestration problem — it leaves this layer for `data-streaming-engineering`.

---

## Decision Tree: choosing a data-pipeline orchestrator

Traverse top-to-bottom. Gate on **latency** first, then **mental model (asset vs task)**, then **ops capacity / managed-vs-OSS**, then **cloud lock-in**.

```mermaid
flowchart TD
  Start([What is the WORKLOAD?]) --> LAT{Latency target?}
  LAT -->|Sub-minute / continuous| STREAM[Not orchestration →<br/>data-streaming-engineering<br/>Kafka / Flink]
  LAT -->|Minutes / hours / daily batch| OPS{Ops capacity?}

  OPS -->|Small team, want managed,<br/>minimal ops| MANAGED{Existing cloud?}
  OPS -->|Have platform engineers,<br/>want control / portability| OSS{Mental model?}

  %% ---- Managed / cloud-native branch ----
  MANAGED -->|AWS| AWSP{Heavy DAG scheduling<br/>+ backfill?}
  MANAGED -->|GCP| GCPP{Heavy DAG scheduling<br/>+ backfill?}
  MANAGED -->|Azure| ADF[Azure Data Factory<br/>· managed ELT + orchestration<br/>· Synapse/Fabric pipelines adjacent]
  AWSP -->|Yes| MWAA[Amazon MWAA<br/>· managed Airflow]
  AWSP -->|No, simple state-machine glue| SFN[AWS Step Functions<br/>· serverless workflow glue]
  GCPP -->|Yes| COMP[Cloud Composer<br/>· managed Airflow]
  GCPP -->|No, simple glue| GWF[GCP Workflows<br/>· serverless workflow glue]

  %% ---- OSS branch ----
  OSS -->|Asset / data / lineage-first,<br/>typed I/O, strong local dev| DAG[Dagster<br/>· software-defined assets<br/>· partitions + asset checks]
  OSS -->|Task-centric, large cross-team<br/>DAG estate, mature scheduling/backfill| AF[Apache Airflow<br/>· tasks/operators, sensors,<br/>· Datasets, dynamic task mapping]
  OSS -->|Dynamic Python-native flows,<br/>light ops| PF[Prefect<br/>· flows/tasks + automations]
  OSS -->|Notebook / low-code data team| MAGE[Mage<br/>· notebook-style pipelines]
  OSS -->|Long-running, stateful,<br/>exactly-once WORKFLOWS<br/>not batch tables| TMP[Temporal-for-data<br/>· durable execution]

  DAG --> SCHED
  AF --> SCHED
  PF --> SCHED
  MAGE --> SCHED
  TMP --> SCHED
  MWAA --> SCHED
  COMP --> SCHED
  ADF --> SCHED
  SFN --> SCHED
  GWF --> SCHED

  SCHED{Scheduling model?} -->|Fixed cadence| CRON[cron schedule]
  SCHED -->|External readiness| SENS[event/sensor<br/>· deferrable operators]
  SCHED -->|Run when upstream data fresh| ASSET[data-aware / asset-based<br/>· Airflow Datasets · Dagster materialization · Prefect automations]
```

---

## Trade-off table

| Engine | Sweet spot | Watch out for |
|---|---|---|
| **Apache Airflow** | Large, cross-team DAG estates; mature scheduling, backfill, huge operator ecosystem | Heaviest ops if self-hosted; task-centric (lineage is bolt-on via Datasets); `catchup` default historically bites |
| **Dagster** | Asset/lineage-first work; typed I/O; local dev + asset checks; data-aware scheduling native | Newer ecosystem; asset mental model is a shift for task-centric teams |
| **Prefect** | Dynamic, Python-native flows; light ops; pythonic control flow | Less of a fixed "DAG estate" model; smaller operator library than Airflow |
| **Mage** | Notebook/low-code data teams wanting fast pipeline authoring | Smaller community; less suited to very large/complex estates |
| **Temporal-for-data** | Long-running, stateful, exactly-once *workflows* (durable execution) | Overkill / wrong tool for nightly batch table builds |
| **MWAA / Cloud Composer** | Want Airflow without operating it; already on AWS/GCP | Managed-version lag + cloud lock-in; still Airflow's task model |
| **Azure Data Factory** | Azure-native ELT + orchestration, low-code | Azure lock-in; less code-first than OSS engines |
| **Step Functions / GCP Workflows** | Serverless state-machine glue, light dependency needs | Not a full DAG scheduler; weak backfill/catchup story; cloud lock-in |

> **Volatile:** feature parity of managed Airflow (MWAA/Composer) vs upstream, pricing, and per-engine version capabilities change frequently. Treat the rows above as a 2026-06 snapshot and re-verify with `ravenclaude-core/deep-researcher` before a client commitment.

---

## Executor / runtime sub-choice (after the engine)

- **Local** — small workloads, dev.
- **Celery** — horizontal worker scale.
- **Kubernetes** (e.g. Airflow KubernetesExecutor / Dagster K8s) — per-task isolation, bursty/elastic.
- **Serverless / managed** — minimal ops; pay-per-run.

State where the **scheduler** and **metadata DB** live; they are the reliability core.

---

## Seams (the orchestrator runs work it does not own)

- **Ingestion / connectors / warehouse** → `data-platform`.
- **Transforms (dbt models/tests)** → `analytics-engineering`.
- **Real-time / streaming** → `data-streaming-engineering` (anything sub-minute leaves this layer).
- **Deploying the engine (Helm/Terraform, K8s, managed provisioning)** → `devops-cicd` / cloud plugins.

---

## Provenance

- OSS docs and consensus framing for Airflow (tasks/operators, sensors, deferrable operators, Datasets, dynamic task mapping, `catchup`), Dagster (software-defined assets, partitions, asset checks), and Prefect (flows/tasks, automations), reviewed 2026-06-21.
- Managed/cloud-native: AWS MWAA + Step Functions, GCP Cloud Composer + Workflows, Azure Data Factory — vendor positioning as of 2026-06; **feature parity and pricing are volatile, re-verify before quoting.**
