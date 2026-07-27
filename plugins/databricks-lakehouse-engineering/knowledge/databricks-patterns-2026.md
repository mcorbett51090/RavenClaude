# Databricks Lakehouse — Patterns & Practices (2026)

> Last reviewed: 2026-07-20. Confidence: **HIGH** for durable engineering practice; **VERIFY-AT-USE** for every version/feature/pricing specific. This file is inline priors; the decision trees in [`databricks-decision-tree.md`](databricks-decision-tree.md) are the callable source of truth. Re-verify volatile facts against current Databricks documentation before a stakeholder commitment.

## Delta Lake — the table discipline

- **Idempotent writes.** Use `MERGE` with stable keys for upserts; dedupe within the batch (window/`row_number`) before the merge so a source with duplicates doesn't corrupt silver. A retry must not double-count — design for at-least-once delivery producing exactly-once _effect_.
- **Change Data Feed (CDC).** Enable where downstream needs row-level change propagation instead of full recompute; it's cheaper than diffing snapshots at scale.
- **File sizing & compaction.** Aim for healthy target file sizes; run `OPTIMIZE` (and `Z-ORDER` on the common filter columns, or **liquid clustering** where it applies — _verify GA/behavior at use_). Un-compacted tables cost scan time on every read.
- **VACUUM safely.** Respect the retention window your time-travel and concurrent readers need; an aggressive `VACUUM` can break in-flight streams and time-travel queries.
- **Schema evolution** is a decision, not a default. Explicit `mergeSchema`/evolution modes on ingestion; a silent widening in silver hides upstream breakage.
- **Deletion vectors / predictive optimization** — powerful but version-gated; **verify-at-use** before you rely on them.

## Spark / PySpark — performance without guesswork

- **AQE (Adaptive Query Execution)** handles a lot (dynamic partition coalescing, skew-join handling, join-strategy switching) — leave it on and let it work before hand-tuning.
- **Broadcast** the small side of a join when it's under the broadcast threshold; a needless sort-merge join on a small dim table is a classic slow stage.
- **Skew** is the #1 wide-transformation killer. Symptom: one task in a stage runs far longer than its peers. Fix with AQE skew handling or key salting.
- **Partitions:** too few → spill and under-parallelism; too many → scheduling overhead and small files. Right-size shuffle partitions; `repartition` before a heavy write, `coalesce` to reduce output files without a shuffle.
- **Never `collect()`/`toPandas()` a large DataFrame to the driver** — it's a driver OOM. Write to a table or process as a stream.
- **UDFs:** prefer built-in/SQL functions and pandas UDFs (vectorized) over row-at-a-time Python UDFs, which break Catalyst optimization and Photon acceleration.

## Ingestion — Auto Loader & Structured Streaming

- **Auto Loader** for files landing incrementally: schema inference + evolution, a checkpoint, and it tracks processed files so you don't re-scan the bucket. Choose the file-notification vs directory-listing mode by scale (**verify-at-use**).
- **Structured Streaming** for continuous event sources: pick the trigger (continuous vs micro-batch vs `availableNow` for "stream once then stop"), set the checkpoint location, and design an **idempotent sink** (foreachBatch + MERGE is the common exactly-once pattern).
- **Dead-letter bad records** — don't let one malformed row kill the stream; route it to a quarantine table.
- **The batch escape hatch:** if the SLO is hourly+, `Trigger.AvailableNow` (stream-once-then-stop) or a plain scheduled batch read is cheaper and easier to operate than an always-on stream.

## Delta Live Tables (DLT)

- Declarative pipelines with built-in **expectations** (data-quality constraints that can warn, drop, or fail), lineage, and managed orchestration. Good when you want the platform to own retries/checkpoints/scaling and you can express the transform declaratively.
- Not a fit when you need imperative control flow, external-system side effects, or fine-grained custom orchestration — use notebooks + Jobs then, or escalate to `data-orchestration`.

## Unity Catalog — governance

- **Three-level namespace:** `catalog.schema.table`. Common layouts: catalog-per-environment (dev/stage/prod) or catalog-per-domain.
- **Grant to groups, never individual users.** Manage groups at the account/identity-provider level.
- **Managed vs external tables/volumes** — managed for lifecycle simplicity; external when another engine or a data-sharing contract needs the files. Volumes govern non-tabular files.
- **Lineage & audit** are built in — use them for impact analysis and compliance rather than bolting on a separate catalog.
- **PII tagging / row-column masking** — design the classification in; retrofitting after an audit is expensive. Org-wide policy is `data-governance-privacy`'s call.

## Jobs / Workflows orchestration

- Multi-task jobs with a **task dependency graph**, per-task retries/timeouts, **job-cluster reuse** across tasks (cheaper than a cluster per task), parameters, and failure alerting.
- Prefer **jobs compute** over all-purpose for scheduled work (materially cheaper DBUs).
- Escalate to `data-orchestration` (Airflow/Dagster) when the DAG spans many external systems, needs complex backfills, or must share scheduling with non-Databricks work.

## Cost (DBU) discipline — the recurring wins

1. **Auto-terminate everything** — clusters and SQL warehouses. Idle compute is the top leak.
2. **Jobs compute for jobs**, all-purpose only for interactive dev.
3. **Right-size SQL warehouses** and enable auto-stop; serverless for spiky BI (**verify availability/pricing at use**).
4. **Spot workers + on-demand driver** for fault-tolerant batch.
5. **Compact tables** — small files cost scan-DBUs on every read.
6. **Photon where it pays** (vectorizable SQL/DataFrame), not blanket-on for UDF-bound Python.

All DBU/list-price figures are **VERIFY-AT-USE + dated** — SKUs and pricing change.

## Tooling map (2026 — verify-at-use)

- **Databricks Runtime (DBR)** — LTS vs latest; feature availability differs by version. Pin and test on upgrade.
- **Databricks Asset Bundles (DABs)** — IaC-style deployment of jobs/pipelines/config as code; good for CI/CD.
- **Databricks Connect / notebooks / SQL editor / dbt-on-Databricks** — dev surfaces.
- **MLflow / Model Serving / Feature Store** — the ML lifecycle seam → `ml-engineering`.

Every version/feature/pricing claim above carries an implicit `[verify-at-use, retrieved 2026-07-20]` — re-check current docs.
