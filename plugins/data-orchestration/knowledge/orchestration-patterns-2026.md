# Knowledge — Orchestration patterns (2026)

> **Last reviewed:** 2026-06-21 · **Confidence:** High on the concepts (idempotency, retries/backoff, partitioning, catchup, SLAs, lineage are stable cross-engine fundamentals); **Medium on engine-specific API names — re-verify against the installed version.**
> The patterns the `pipeline-orchestration-engineer` applies when building DAGs/assets, and the `orchestration-architect` checks a chosen engine against. Concepts are engine-agnostic; the per-engine mappings are a 2026-06 snapshot.

---

## 1. Thin orchestration, compute pushed down

The orchestrator's job is to **schedule and sequence**, not to compute. Push transform logic to dbt / warehouse SQL / Spark and keep tasks thin (a `dbt run`, a `spark-submit`, a SQL `MERGE`). A DAG full of business logic is brittle and untestable.

## 2. Partition by the data grain — not wall-clock run time

Partition outputs by the **natural logical grain** (event/logical date, region, tenant), keyed deterministically. This is the foundation for everything below: it lets backfills target exact slices and lets re-runs overwrite cleanly.

- Airflow: the run's **logical date** (`data_interval_start/end`), parameterizing the partition the task writes.
- Dagster: **partition definitions** (daily/static/dynamic) on assets.
- Anti-pattern: keying on `now()` / wall-clock — a re-run then writes a *different* partition than it should.

## 3. Idempotency is the price of admission for retries

A task is idempotent when re-running it produces the same result. Achieve it with:

- **deterministic partition keys** (rule #2),
- **overwrite-by-partition** — delete-then-insert, `INSERT OVERWRITE`, or `MERGE` the target partition; **never blind append** (append + retry = duplicates),
- **deduped/keyed external side effects** (don't fire an unconditional email/webhook mid-task).

**No idempotency proof → no retry policy.** This ordering is non-negotiable.

## 4. Retries with exponential backoff (+ jitter)

Once idempotent: bounded `retries` (3-5), `retry_delay` growing exponentially (e.g. 1m → 2m → 4m) with **jitter** to avoid a thundering herd of synchronized retries hammering a recovering upstream.

- **Split error classes:** retry **transient** (timeout, throttling, 5xx); **fail fast** on **deterministic** (schema mismatch, bad SQL).
- **On exhaustion:** alert with the partition + error, dead-letter/quarantine where applicable, surface in the SLA/lineage view — never fail silently.

## 5. Scheduling & triggering models

| Model | When | Engine mapping (2026-06 — verify) |
|---|---|---|
| **cron** | fixed cadence | all engines (`schedule`/`schedule_interval`, Dagster `@schedule`) |
| **event / sensor** | wait on external readiness | Airflow sensors — prefer **deferrable operators / async sensors** so you don't block a worker slot polling |
| **data-aware / asset-based** | "run when upstream data is fresh" | Airflow **Datasets**, Dagster **asset materialization** + asset sensors, Prefect **automations** |

Prefer deferrable/async sensors over a poke loop that holds a worker slot.

## 6. Catchup & backfill

- **`catchup`** (Airflow, historically default-on): on a new/changed schedule it will run every missed interval from `start_date` — an accidental `catchup=True` over a year of history is a classic incident. **Set it explicitly.**
- **Backfill** = deliberate reprocessing of a historical partition range. Treat it as a **production change**: scope exact partitions, confirm idempotency precondition, cap concurrency (pools / `max_active_runs` / backfill concurrency) so it doesn't starve live runs or overload the warehouse, monitor, and have a rollback. Dagster scopes backfills to partition ranges; Airflow via `airflow dags backfill` / a scoped catchup.

## 7. Dynamic task mapping / fan-out

When the number of parallel units is known only at runtime (N files, N partitions), use the engine's dynamic fan-out — Airflow **dynamic task mapping** (`.expand()`), Dagster dynamic outputs / dynamic partitions — instead of hand-unrolling tasks. Keep a **concurrency cap** so a large fan-out doesn't overwhelm downstream.

## 8. Executor / concurrency control

Match the executor to the workload (Local / Celery / Kubernetes / serverless — see the selection tree). Use **pools, priority weights, and `max_active_runs/tasks`** to protect shared resources (a warehouse, an API rate limit) from a burst.

## 9. Data-freshness SLAs & alerting

- Define a **freshness threshold per dataset** ("`sessions` must be ≤ 2h behind event time").
- Alert on **SLA miss / sensor timeout** — and every SLA names **who gets paged** and **the runbook to follow**. A missed-SLA alert with no owner is noise.
- Airflow SLA-miss callbacks, Dagster **freshness policies / asset checks**, or an external monitor (e.g. a freshness check in `data-platform`) are the surfaces.

## 10. Lineage & blast radius

Expose lineage across the asset/task graph so a failure's downstream blast radius is visible. Asset-centric engines (Dagster) give this natively; task-centric (Airflow) derive it from Datasets or an external catalog (OpenLineage / Marquez). Lineage is what turns "a task failed" into "these 6 dashboards are now stale."

---

## Anti-patterns the engineer flags

- Retries on a non-idempotent (append-style) task → duplicate data.
- Partitioning by wall-clock run time instead of logical/event date.
- A blocking poke-loop sensor hogging a worker slot (use deferrable operators).
- An accidental unbounded `catchup` on schedule change.
- A casual `--start-date` backfill with no concurrency cap / runbook / rollback.
- Heavy transform logic inside operators instead of pushed to dbt/SQL/Spark.
- A freshness SLA with no owner / no runbook.
- Hand-unrolled tasks where dynamic task mapping fits.

---

## Provenance

- Engine-agnostic fundamentals (idempotency, exponential backoff + jitter, partition-by-grain, catchup semantics, freshness SLAs, lineage) are stable across the data-engineering literature, reviewed 2026-06-21.
- Engine-specific API names (Airflow Datasets / deferrable operators / dynamic task mapping / `catchup`; Dagster software-defined assets / partitions / freshness policies / asset checks; Prefect automations) reflect 2026-06 docs — **re-verify against the installed version** before shipping, per the accuracy discipline.
