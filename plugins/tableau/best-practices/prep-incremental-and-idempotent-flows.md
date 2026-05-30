# Build Prep flows to be idempotent and incremental — re-running yields the same output, not duplicates

**Status:** Pattern — a Prep flow that is not idempotent is a data-quality incident waiting to happen; design for safe re-runs from the start.

**Domain:** Prep / Data engineering

**Applies to:** `tableau`

---

## Why this exists

A Tableau Prep flow is an ETL job, and ETL jobs get re-run — on a schedule, after a failure, during a backfill. A flow that **appends** without a deduplicating key produces duplicate rows on the second run; a flow that **full-refreshes** a target every time re-processes the entire history when only yesterday changed. **Idempotent** means re-running the flow on the same input yields the same output (no growth, no drift); **incremental** means a scheduled run processes only the new rows. Without both, you get the two classic Prep failures: silently doubled fact rows (a failed run retried, appending twice) and a nightly flow that grows from minutes to hours as history accumulates. Heavy reshaping — pivots, unions, joins-to-aggregate, dedup, data-quality cleanup — belongs in a Prep flow precisely *because* it should happen once, centrally, and feed a clean extract; that benefit evaporates if the flow can't be re-run safely.

## How to apply

Make the output a function of the input (idempotent) and process only new rows (incremental).

```
IDEMPOTENT — same input → same output:
  • Deduplicate on a stable business/natural key (Remove Duplicates, or aggregate to the key grain)
    so a retried run can't double rows.
  • Prefer "REPLACE the output" semantics for full runs over blind "APPEND".
  • Keep transforms deterministic — no row order dependence, no NOW()-stamped keys that differ per run.
  • Land into a target whose write is atomic (full table replace, or upsert on the key) — not append-only.

INCREMENTAL — process only new rows:
  • Configure incremental run on a monotonically increasing, never-edited column
    (insert id, immutable loaded_at) — NOT updated_at, NOT a back-datable business date.
  • Pair with a periodic FULL run to repair drift (deletes, late arrivals, back-dated corrections).
  • An incremental run that APPENDS must still dedup on the key, or a re-run double-appends.
```

```
EXAMPLE — nightly order-cleanup flow:
  Input: raw_orders (append-only landing), ~2M new rows/night, occasional late/corrected rows.
  Flow: clean → dedup on [order_id] (keep latest by loaded_at) → roll up to order grain →
        output clean_orders.hyper.
  Incremental: run on [loaded_at] > last-seen-max nightly (fast).
  Idempotent: dedup-on-order_id means a retried failed run can't create a second copy.
  Drift repair: weekly FULL run re-reads all history to catch corrections an append missed.
```

**Do:**
- Dedup on a stable key so any re-run is safe.
- Key incremental runs on a strictly-monotonic, never-edited column.
- Schedule a periodic full run alongside the incremental one to repair drift.
- Keep every transform deterministic and order-independent.

**Don't:**
- Append without a dedup key — a retried run silently doubles rows.
- Drive incremental on `updated_at` or a back-datable date — you'll miss edited/late rows.
- Rely on incremental-only forever — deletes and corrections accumulate as drift.
- Put one-off, workbook-specific cleanup in Prep — that belongs in the workbook; Prep is for shared, repeated reshaping.

## Edge cases / when the rule does NOT apply

- **Truly append-only immutable source** (event log that is never edited/deleted) — incremental append without dedup can be safe *if* the run is guaranteed exactly-once; most schedulers aren't, so dedup is cheap insurance.
- **Small inputs** — full refresh every run is simplest and inherently idempotent; skip incremental machinery you don't need.
- **No reliable monotonic key** — incremental is unsafe; use full runs on a schedule the SLA permits.
- **Exploratory / one-shot flow** — idempotency matters less for a flow that runs once by hand, but make it safe before you schedule it.

## See also

- [`./data-extract-optimization.md`](./data-extract-optimization.md) — the incremental-extract-refresh analogue and the monotonic-key rule
- [`./data-relationships-before-joins.md`](./data-relationships-before-joins.md) — model the output grain Prep should produce
- [`../knowledge/data-performance-decision-trees.md`](../knowledge/data-performance-decision-trees.md) — `## Decision Tree: Where to do the work — Prep vs calculated fields vs reshape at source`
- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — the agent that owns this rule
- Tableau Help, "Tableau Prep" and "Refresh flow output incrementally" `[verify-at-build]`

## Provenance

Codifies the agent's discipline steps 7–8 ("Reshape at the right place" / "Build Prep flows to be incremental and idempotent"). Idempotency and incremental-on-monotonic-key are general ETL principles applied to Prep; exact Prep incremental-run option labels are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
