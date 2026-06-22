---
name: design-dag-and-dependencies
description: Design a correct, minimal DAG or software-defined-asset graph for a pipeline — derive the real upstream→downstream edges, pick the partition grain, choose the scheduling/triggering model (cron / sensor-deferrable / data-aware-asset), and decide catchup behavior — then capture it in the DAG design doc. Reach for this when the user says "design the DAG/assets for <pipeline>", "what should depend on what?", or "how should these jobs trigger?". Used by `pipeline-orchestration-engineer` (primary).
---

# Skill: design-dag-and-dependencies

> **Invoked by:** `pipeline-orchestration-engineer` (primary). Also consulted by `orchestration-architect` to confirm the chosen engine can express the required dependency shape.
>
> **When to invoke:** "design the DAG/assets for <pipeline>"; "what should depend on what?"; "how should these jobs trigger/schedule?"; any new or restructured pipeline graph.
>
> **Output:** a dependency graph (tasks or software-defined assets) + the partition grain + the scheduling/trigger choice (with catchup decision) + a filled-in [`../../templates/dag-design-doc.md`](../../templates/dag-design-doc.md).

## Procedure

1. **Identify the outputs and their partition grain first.** What datasets does this pipeline produce, and at what natural grain (logical/event date, region, tenant)? Partition by the data's grain, **not** wall-clock run time — this is what makes backfills target exact slices and re-runs overwrite cleanly.
2. **Derive the real dependency edges.** For each output, list the inputs it truly needs; draw upstream→downstream edges. Keep them **minimal** — a false edge serializes work that could run in parallel; a missing edge causes a race on stale data.
3. **Choose task-centric vs asset-centric expression.** Airflow tasks/operators (imperative steps) vs Dagster software-defined assets / Prefect flows (declare the data, let the engine derive the graph). Asset-centric gives lineage and data-aware scheduling for free; task-centric gives fine step control. Match to the chosen engine.
4. **Pick the scheduling/trigger per pipeline:**
   - **cron** for fixed cadence,
   - **event/sensor** for external readiness — prefer **deferrable operators / async sensors** so you don't hog a worker slot polling,
   - **data-aware / asset-based** (Airflow Datasets, Dagster asset materialization, Prefect automations) when the requirement is "run when upstream data is fresh."
5. **Decide catchup/backfill behavior explicitly.** Set Airflow `catchup` (default-on historically — an accidental `catchup=True` over a year of history is a classic incident), or Dagster partition backfill scope. Never leave it implicit.
6. **Apply the patterns reference** [`../../knowledge/orchestration-patterns-2026.md`](../../knowledge/orchestration-patterns-2026.md): keep the DAG thin (push compute to dbt/SQL/Spark), use **dynamic task mapping** for fan-out over a runtime-sized collection instead of hand-unrolled tasks, group related steps, and set sensible concurrency/pool limits.
7. **Capture the design** in [`../../templates/dag-design-doc.md`](../../templates/dag-design-doc.md) — graph, grain, schedule, catchup, idempotency/retry pointer, freshness SLA — before writing code.

## Worked example

> User: "Daily pipeline: load raw events → build a sessions table per day → run dbt marts. Design it."

- Outputs & grain: `sessions` and the marts are **partitioned by event date** (logical date, not run time).
- Edges (minimal): `raw_events[date]` → `sessions[date]` → `dbt_marts[date]`. The dbt step depends on `sessions`, not directly on `raw_events`.
- Expression: asset-centric (Dagster assets / Airflow Datasets) so "run sessions when today's raw_events landed" is data-aware, not a guessed 6am cron.
- Trigger: data-aware on `raw_events` freshness; dbt step triggers on `sessions` materialization. `catchup` decided explicitly = off (backfills run via the runbook, not auto-catchup).
- Thin DAG: the dbt marts are a single `dbt run` step, not reimplemented SQL inside operators.

## Guardrails

- Partition by the **data grain**, never wall-clock run time — see [`handle-backfills-and-retries`](../handle-backfills-and-retries/SKILL.md).
- Minimal edges only: no false dependency (kills parallelism), no missing dependency (race on stale data).
- Sensors **defer**, don't block a worker slot.
- Always set catchup/backfill behavior explicitly; never inherit the default by accident.
- Keep the DAG thin — orchestrate transforms (dbt/SQL/Spark), don't reimplement them in tasks.
