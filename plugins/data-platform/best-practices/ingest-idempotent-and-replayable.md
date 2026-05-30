# Make ingestion idempotent and replayable — a re-run must never duplicate or lose rows

**Status:** Absolute rule — a pipeline you cannot safely re-run is a pipeline you cannot operate. Every load path is keyed and replay-safe.

**Domain:** ELT / pipeline reliability

**Applies to:** `data-platform`

---

## Why this exists

Pipelines fail mid-run: a connector OOMs at row 4M of 10M, a rate limit trips, a network blip drops a checkpoint. The only safe recovery is **re-run the load** — and that is only safe if loading the same source data twice produces the same warehouse state. The two breaks are (1) **non-idempotent appends** — a retried batch double-counts revenue — and (2) **lost state** — a restart resumes from row 1 and silently skips rows the cursor had already passed. The discipline is: land into raw on a deterministic key with `MERGE`/upsert semantics (never blind `INSERT`), checkpoint the cursor per stream, and keep raw immutable so a full reload is always available as the nuclear-option replay. This is the operational complement to ELT — raw retention only buys replayability if the *load* into raw is itself replay-safe.

## How to apply

Upsert on the source's natural key plus an extracted-at watermark; never append blindly. Checkpoint the replication cursor after each committed batch.

```sql
-- Idempotent load into raw: MERGE on the source primary key, not INSERT.
-- A re-run of the same batch is a no-op; a changed row updates in place.
merge into stripe_raw.charges          as tgt
using staged_batch                     as src
  on tgt.id = src.id
when matched and src._extracted_at > tgt._extracted_at then
  update set *                          -- last-write-wins by watermark
when not matched then
  insert *;
```

```yaml
# Airbyte: choose a sync mode that is replay-safe by construction.
# Incremental | Append + Dedup  → upsert on primary key (idempotent)
# Full Refresh | Overwrite      → idempotent by truncate-and-reload (small tables)
# Incremental | Append          → NOT idempotent on retry; only for true append-only event logs
sync_mode: incremental
destination_sync_mode: append_dedup
primary_key: [["id"]]
cursor_field: ["updated_at"]
```

**Do:**
- Load with `MERGE`/upsert keyed on the source's stable primary key; let last-write-wins resolve on an extracted-at/updated-at watermark.
- Checkpoint the cursor **after** the batch commits, so a crash resumes from the last durable point — not row 1, not past unprocessed rows.
- Keep raw immutable + retained so "reset cursor, full reload" is always a valid recovery (the replay substrate from the ELT rule).
- Make the whole run re-entrant: running it twice back-to-back must leave the warehouse identical to running it once.

**Don't:**
- Blind-`INSERT` source rows on every run (a retry double-counts) or `DELETE`-then-`INSERT` without a transaction (a crash mid-window leaves a hole).
- Advance the cursor before the batch is durably committed.
- Treat a webhook event stream as a CRUD table — dedupe events on their event ID, then reconstruct state in dbt.

## Edge cases / when the rule does NOT apply

- **True append-only event logs** (immutable facts, e.g. click events) where the event ID is the dedup key — `append` is fine *because* the event ID makes a replayed event a detectable duplicate downstream.
- **Snowflake / Delta Sharing** — no pipeline to make idempotent; the share is the source (house opinion #10).
- **Full-refresh small dimension tables** — truncate-and-reload is idempotent by construction; no MERGE needed.

## See also

- [`./etl-elt-load-then-transform-in-warehouse.md`](./etl-elt-load-then-transform-in-warehouse.md) — raw retention is what makes the full-reload replay possible
- [`./connector-incremental-with-backfill.md`](./connector-incremental-with-backfill.md) — cursor checkpointing + backfill on the connector side
- [`../skills/data-quality-tests/SKILL.md`](../skills/data-quality-tests/SKILL.md) — row-count drift bands catch a double-load before it reaches a dashboard
- [`../agents/etl-pipeline-engineer.md`](../agents/etl-pipeline-engineer.md) — owns the load path

## Provenance

Distilled from `etl-pipeline-engineer.md` ("Webhooks for events; batch for history") and `connector-developer.md` ("Pagination + state are the silent killers … cursor-based pagination + checkpointed state + resumable runs are non-negotiable"), plus the ELT raw-retention rule. Append-dedup / MERGE-on-key is standard Airbyte / dbt-snapshot practice. `[verify-at-build]` Airbyte sync-mode names (`append_dedup`) — confirm against current Airbyte destination docs, the labels shift between CDK versions.

---

_Last reviewed: 2026-05-30 by `claude`_
