# Shape the extract to the question — hide, aggregate, materialize, then refresh incrementally

**Status:** Pattern — an extract should carry only the columns, rows, and grain the viz needs; a full-fat mirror of the source is the deviation.

**Domain:** Performance / Data modeling

**Applies to:** `tableau`

---

## Why this exists

The default mistake is to extract the source table verbatim — every column, every row, at row-level grain — and then wonder why the `.hyper` is multi-gigabyte and the refresh takes an hour. An extract is an opportunity to **pre-pay the work the viz would otherwise repeat on every query**. Three levers do most of it: **hide unused fields before extracting** (hidden fields are excluded from the extract, shrinking it), **aggregate to visible dimensions** when no row-level detail is ever shown (an extract of 50M order lines rolled up to region/month/product can be thousands of rows), and **materialize calculated fields** so deterministic calcs compute once at refresh instead of on every query. On top of that, **incremental refresh** keyed on a monotonic column turns an hour-long full reload into a seconds-long append. Skipping these is how a workbook is slow *before the first filter is even applied*.

## How to apply

Apply the four levers in order when creating/editing the extract.

```
1. HIDE first        Hide every field the workbook never uses, THEN create the extract.
                     (Hidden-at-extract-time fields are excluded; hiding after doesn't shrink it.)
2. AGGREGATE         "Aggregate data for visible dimensions" when no row-level detail is shown.
                     50M order lines → ~12k rows at [Region]×[Month]×[Category].
3. MATERIALIZE       "Compute calculations now" so deterministic calcs (not NOW()/TODAY()) bake in.
4. INCREMENTAL       Refresh incrementally on a monotonic key; schedule a periodic FULL refresh.
```

```
INCREMENTAL REFRESH setup:
  Identify a column that ONLY increases and is never edited:
    GOOD: surrogate id (BIGINT IDENTITY), created_at / loaded_at (immutable insert timestamp)
    BAD : updated_at (edits re-touch old rows → missed), business date (back-dated corrections),
          any column a user can change
  Incremental run appends rows where [key] > last-seen-max.
  → Schedule a periodic FULL refresh (e.g. weekly) to repair drift: late-arriving rows,
    hard-deleted rows, and back-dated corrections that an append can never catch.
```

**Do:**
- Hide unused fields *before* the extract exists; verify the size dropped.
- Aggregate to visible dimensions whenever the viz shows no row-level marks.
- Materialize deterministic calculations; leave volatile ones (`NOW()`, `TODAY()`, random) un-materialized.
- Key incremental refresh on a strictly-monotonic, never-edited column, and pair it with a periodic full refresh.

**Don't:**
- Incrementally refresh on `updated_at` or a back-datable business date — you will silently miss rows.
- Skip the periodic full refresh — incremental-only extracts drift (deletes, late arrivals, corrections accumulate).
- Aggregate away a dimension a tooltip, drill-down, or detail sheet actually needs.
- Materialize a calc that uses `NOW()`/`TODAY()` — it freezes to the refresh time and goes wrong.

## Edge cases / when the rule does NOT apply

- **Row-level detail required** (record-level audit sheet, "view underlying data") — do not aggregate; that grain is the deliverable.
- **No reliable monotonic key** — incremental refresh is unsafe; use full refresh on a schedule the SLA allows.
- **Volatile calculations** — leave un-materialized so they recompute per query.
- **Source small enough that refresh is already fast** — full refresh is simpler and avoids incremental drift entirely; don't add incremental machinery you don't need.
- **Heavy reshaping (pivot/union/dedup)** — that belongs in a Prep flow that outputs the extract, not in extract settings.

## See also

- [`./data-extract-vs-live-by-freshness.md`](./data-extract-vs-live-by-freshness.md) — choose extract before you optimize it
- [`./prep-incremental-and-idempotent-flows.md`](./prep-incremental-and-idempotent-flows.md) — where heavy reshaping lives
- [`./perf-filter-at-the-source.md`](./perf-filter-at-the-source.md) — extract/data-source filters remove rows before the workbook sees them
- [`../knowledge/data-performance-decision-trees.md`](../knowledge/data-performance-decision-trees.md) — `## Decision Tree: Where to filter` and the perf-recorder ladder
- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — the agent that owns this rule
- Tableau Help, "Aggregate data in extracts" and "Configure an incremental extract refresh" `[verify-at-build]`

## Provenance

Codifies the agent's discipline step 4 ("Shape the extract to the question") and constitution house opinion #5. The "hide-before-extract excludes the field," "aggregate for visible dimensions," and incremental-refresh-on-monotonic-key behaviors are long-standing Hyper/extract mechanics; exact option labels move across versions — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
