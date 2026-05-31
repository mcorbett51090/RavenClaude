---
description: Scaffold a Fabric data-ingestion pipeline — pick the movement method from the decision tree (mirror / copy job / pipeline), make the load incremental and idempotent with a watermark control table and MERGE-on-key, and reframe Direct Lake as the final step.
argument-hint: "[the source, e.g. 'incremental load from an on-prem SQL Server']"
---

# Scaffold an ingestion pipeline

You are running `/microsoft-fabric:scaffold-ingestion-pipeline`. Build the ingestion for what the user described (`$ARGUMENTS`), following this plugin's `data-factory-engineer` discipline — move only what changed, and make re-runs safe.

## When to use this

You own the data movement (past Mirroring/auto-mirror) and need an incremental, repeatable load. If the source already lives in OneLake/ADLS/S3/GCS and you only need to read it, **stop and use a shortcut** instead of building a pipeline (`one-copy-shortcut-before-copying.md`). If the source is operational and already in Fabric, auto-mirror handles it.

## Steps

1. **Pick the movement method from the decision tree** — Mirroring/auto-mirror (replica, no scaffolding), Copy job (native incremental + CDC, 50+ connectors, no pipeline to build), or Pipeline (when you need orchestration/control flow). Prefer the lower-ceremony leaf (`pipeline-orchestrate-idempotent-watermarks.md`).
2. **Make the load incremental** — Lookup the last successful high-water value from a control table, copy only rows `> watermark`, and advance the watermark **only after** the load commits so a failed run re-pulls the same delta (same file).
3. **Write idempotently with MERGE-on-key**, never a blind `INSERT` — re-runs and double-fires must not duplicate rows (same file).
4. **Use Fast Copy then Spark** where the method supports it — stage with the high-throughput copy, transform in Spark (`pipeline-fast-copy-then-spark.md`).
5. **Schedule with smoothing in mind** — heavy loads are background CU consumers; ride the 24-h smoothing window off-peak, don't fire them into the interactive peak (`pipeline-orchestrate-idempotent-watermarks.md`, `capacity-isolate-noisy-workloads.md`).
6. **Reframe the Direct Lake model as the final step** if the load feeds one (`pipeline-orchestrate-idempotent-watermarks.md`). Use the `templates/fabric-ingestion-design.md` shape.

## Guardrails

- Never truncate-and-reload a large source every run (initial backfill aside) — it wastes CUs and widens the load window.
- Never advance the watermark before the load commits — a mid-load failure then silently skips data.
- This plugin is advisory: emit the pipeline JSON / Copy-job config / `fab` snippets the consultant runs in their own tenant. Connection-string/service-principal handling routes to `ravenclaude-core/security-reviewer`.
