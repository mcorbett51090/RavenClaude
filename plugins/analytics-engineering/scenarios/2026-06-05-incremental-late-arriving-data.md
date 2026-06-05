---
scenario_id: 2026-06-05-incremental-late-arriving-data
contributed_at: 2026-06-05
plugin: analytics-engineering
product: bigquery
product_version: "dbt-core 1.8"
scope: likely-general
tags: [incremental, late-arriving, lookback, merge, watermark, append]
confidence: high
reviewed: false
---

## Problem

An incremental fact `fct_events` quietly under-counted. The daily total in the warehouse was consistently ~2–4% below the source system's daily total, and a full-refresh rebuild produced the *correct* number — so the incremental logic, not the source data, was dropping rows. The `is_incremental()` filter was `where event_timestamp > (select max(event_timestamp) from {{ this }})`. Events from mobile clients arrived hours-to-days late (buffered offline, then flushed), so an event with `event_timestamp = Monday 14:00` could land in the warehouse on Wednesday — after the watermark had already advanced past Monday. Those late rows were filtered out forever.

## Constraints context

- Warehouse: BigQuery; `incremental_strategy = 'merge'` with `unique_key = 'event_id'`. The merge was correct; the *predicate that selected new rows* was the bug.
- The full-refresh was correct but expensive (multi-TB scan) and ran weekly, so the drift accumulated for up to six days before a rebuild masked it.
- Late arrival was a real property of the source (offline mobile buffering), not a one-off — any watermark on the *event* timestamp would lose late rows.
- The source carried both an `event_timestamp` (when it happened) and a `_loaded_at` (when it landed in the warehouse). The model filtered on the wrong one.

## Attempts

- Tried: switching the predicate to `event_timestamp >= max(event_timestamp) - interval 3 day` (a fixed lookback). Recovered most late rows but (a) still lost anything later than 3 days, and (b) re-processed three days of data every run, which with `merge` is correct but more expensive. A lookback is a band-aid sized to the *observed* lateness, not the actual distribution.
- Tried: filtering on the **load timestamp** instead — `where _loaded_at > (select max(_loaded_at) from {{ this }})`. This is the real fix: the watermark advances on *ingestion* time, which is monotonic, so a late-arriving event is selected on the run *after it lands*, regardless of how old its `event_timestamp` is. The `merge` on `event_id` then inserts it (or updates it if it was a correction).
- Tried (belt-and-suspenders): keeping a *bounded* lookback on `_loaded_at` (`- interval 12 hour`) to cover the edge case where a row lands mid-run between the `max()` read and the merge write, so a row straddling the run boundary isn't skipped. Idempotent because the `merge` dedups on `event_id`.
- Tried (the detector): a scheduled reconciliation test comparing the incremental daily total against a `count(*)` from the source staging model for the trailing 3 days — it fails loudly if the incremental and full counts diverge, so the next occurrence is caught in CI, not by a weekly rebuild.

## Resolution

**Watermark on ingestion time, not event time; merge on the business key.** The durable rule:

1. **Filter `is_incremental()` on a monotonically-increasing load/ingestion column** (`_loaded_at`, `_fivetran_synced`, `_airbyte_emitted_at`), never on the business `event_timestamp`. Event time can arrive out of order; load time can't go backwards.
2. **Use `merge` (or `delete+insert`) keyed on a reliable business key** so a late or corrected row updates in place rather than duplicating. `append` is only safe for truly immutable, never-late event streams.
3. **Add a bounded lookback** on the load watermark to cover the run-boundary race, and rely on the merge key for idempotency so re-processing the overlap is harmless.
4. **Detect drift in CI**, not in a weekly full-refresh: a trailing-window reconciliation test against the source count turns "the number is quietly low" into a failing build.

The trap is that an event-time watermark *looks* obviously correct — "process rows newer than the newest one I have" — and works perfectly until the source's arrival order stops matching its event order, which for any client-side or batch-buffered source, it eventually does.

**Action for the next engineer:** before shipping an incremental model, ask "can a row arrive whose event timestamp is *older* than rows I've already loaded?" If yes (almost always, for event data), watermark on load time and merge on the key. Validate by diffing the incremental daily totals against a full-refresh once before trusting it.

Cross-reference: the field-note complement to [`../best-practices/key-incremental-models-correctly.md`](../best-practices/key-incremental-models-correctly.md) and [`../best-practices/make-transforms-idempotent-and-rerunnable.md`](../best-practices/make-transforms-idempotent-and-rerunnable.md). For the strategy-per-warehouse choice, see the "Incremental model — which strategy for this warehouse?" tree in [`../knowledge/analytics-engineering-decision-trees.md`](../knowledge/analytics-engineering-decision-trees.md).
