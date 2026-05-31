---
description: Scaffold an idempotent, replay-safe ELT pipeline — raw-verbatim load on a deterministic key, dbt staging→intermediate→marts, the test floor, and a declared freshness SLA.
argument-hint: "[the source, e.g. 'QuickBooks into Supabase' or 'Stripe + Salesforce']"
---

# Scaffold an idempotent ELT pipeline

You are running `/data-platform:scaffold-idempotent-elt-pipeline`. Stand up the load + transform shape for the source the user named (`$ARGUMENTS`), following this plugin's `etl-pipeline-engineer` discipline — a pipeline you cannot safely re-run is one you cannot operate.

## When to use this

Starting a new ELT engagement, or rebuilding a pipeline that double-counts on retry or silently ships stale data. Not for a Snowflake/Delta Sharing engagement (no pipeline to build — use the share) or a one-off CSV import.

## Steps

1. **Land raw, transform in the warehouse — ELT not ETL** (`etl-elt-load-then-transform-in-warehouse`): the connector's only job is to land the source verbatim into a `*_raw` schema; never pre-shape or encode business logic in the ingestion layer. Raw stays immutable and retained — it is the replay substrate.
2. **Make the load idempotent** (`ingest-idempotent-and-replayable`): `MERGE`/upsert on the source's stable primary key with last-write-wins on an extracted-at watermark — never blind `INSERT`. Checkpoint the cursor *after* the batch commits so a crash resumes from the last durable point, not row 1. Running the pipeline twice must leave the warehouse identical to running it once.
3. **Layer dbt staging → intermediate → marts** (`dbt-stage-then-mart-never-skip-the-layer`): staging is the only layer that touches `{{ source() }}` (one model per source table, all casts/renames/dedup here); marts reference only `ref()`. A mart reading a raw source is a layering defect.
4. **Lay the test floor** (`dbt-test-the-floor-unique-not-null-relationships`): `unique` + `not_null` on every surrogate key, `relationships` on every foreign key, `accepted_values` on enums. CI runs `dbt build` (which runs tests), never `dbt run` (which skips them).
5. **Declare a freshness SLA and match cadence to it** (`dashboard-set-data-freshness-slas`): a per-source `dbt source freshness` check that alerts on breach, an as-of timestamp surfaced downstream, and a sync schedule set to *just meet* the SLA — no faster.
6. **Write the handoff plan now** (`connector-document-the-handoff-at-design-time`): name the post-engagement owner up front; it drives managed-vs-self-hosted; ship the runbook (credential rotation, re-auth cadence, failure triage) as you build.

## Guardrails

- Any change touching auth, JWT, RLS, or PII in transit routes through `ravenclaude-core/security-reviewer` — mandatory.
- Don't advance the cursor before the batch is durably committed, and don't treat a webhook event stream as a CRUD table — dedupe on event ID.
- State stack context (Case A/B/C/D) and carry retrieval dates on any pricing claim per the plugin Output Contract.
