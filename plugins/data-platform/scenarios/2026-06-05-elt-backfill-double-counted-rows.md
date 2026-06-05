---
scenario_id: 2026-06-05-elt-backfill-double-counted-rows
contributed_at: 2026-06-05
plugin: data-platform
product: airbyte
product_version: "unknown"
scope: likely-general
tags: [elt, backfill, idempotency, merge, watermark, double-count]
confidence: high
reviewed: false
---

## Problem

A nightly ELT pipeline (Stripe + an internal orders API → Postgres warehouse → Metabase) had to be re-run after a source outage left two days of data missing. The engineer triggered a "backfill from the last good date." The next morning the revenue dashboard showed **roughly 2× the real number** for the overlap window. The pipeline had not errored — it had successfully loaded the same rows twice.

## Context

- The landing tables were `INSERT`-only (append). The connector's "incremental" mode advanced a watermark on success but had **no unique constraint and no MERGE/upsert** on the warehouse side — so a re-run over an already-loaded window appended duplicates instead of replacing them.
- The backfill window was picked by hand ("re-run from Tuesday"), overlapping a range that had partially loaded before the outage.
- The dashboard summed `amount` with no dedup in the model, so every duplicated row inflated the total directly.
- Constraint: the source (Stripe) is itself append-mostly and re-emits events on replay, so "just trust the source" was never going to dedup for us.

## Attempts

- Tried: deleting the duplicated rows by hand with a one-off `DELETE` keyed on the overlap dates. Outcome: stopped the bleeding for that window but didn't fix the mechanism — the next backfill would do it again, and the manual delete is itself a foot-gun on a live table.
- Tried: making the load **idempotent and replayable** instead of append-only — a natural/surrogate key (`source`, `source_id`, `event_id`) with a `MERGE` (upsert) so re-loading a row is a no-op, plus a bounded backfill from the **last-good watermark** rather than a hand-picked date. Outcome: re-running any window became safe; the double-count couldn't recur. This is the `ingest-idempotent-and-replayable` + `connector-incremental-with-backfill` best-practices, applied.
- Tried: adding the dbt floor tests (`unique` on the grain key, `not_null` on the keys) so a future duplicate **fails the build and halts the mart** instead of silently publishing. Outcome: turned "wrong number ships to client" into "build halts, we get paged."

## Resolution

The root cause was an **append-only load with no idempotency**, not the backfill itself — a replay is a normal operation, and a correct pipeline treats a re-run of an already-loaded window as a no-op. The fix was the standing house default: load with a MERGE on a stable grain key, drive backfills from the last-good watermark (not a hand-picked date), and guard the grain with a `unique` dbt test so a regression halts the build.

**Action for the next consultant hitting this pattern:** before you trigger *any* backfill, confirm the load path is idempotent — is there a unique key + MERGE/upsert, or is it `INSERT`-only? If it's append-only, **fix that first**; a backfill over an append-only table double-counts by construction. Then back-fill from the last-good watermark with a small overlap, never a hand-picked "from Tuesday." Map the failure with the `## Decision Tree: Pipeline failure` (the "transient outage → idempotent + cursor?" branch) and the `## Decision Tree: ELT load — append, merge/upsert, or full-refresh-and-swap?` tree in [`../knowledge/data-platform-decision-trees.md`](../knowledge/data-platform-decision-trees.md).

**Sources (retrieved 2026-06-05):** canonical rules this corroborates — [`../best-practices/ingest-idempotent-and-replayable.md`](../best-practices/ingest-idempotent-and-replayable.md), [`../best-practices/connector-incremental-with-backfill.md`](../best-practices/connector-incremental-with-backfill.md), [`../best-practices/dbt-test-the-floor-unique-not-null-relationships.md`](../best-practices/dbt-test-the-floor-unique-not-null-relationships.md). dbt incremental + `unique_key` upsert semantics: https://docs.getdbt.com/docs/build/incremental-models (treat version-specific behavior as `[verify-at-use]`).
