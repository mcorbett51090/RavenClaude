# Put business logic in measures, not calculated columns

**Status:** Pattern — strong default; deviate only with a written reason.

**Domain:** Power BI / DAX

**Applies to:** `power-platform`

---

## Why this exists

A **calculated column** is computed once at refresh, materialized into the model, and consumes VertiPaq memory on every row forever — and it cannot respond to the user's filter context. A **measure** is computed at query time in the current filter context, stores nothing, and is the only way to get an answer that changes as the user slices. Makers coming from Excel reflexively reach for columns because that's what a spreadsheet cell is; the result is a bloated model full of pre-aggregated numbers that give wrong answers when filtered. The cost compounds: a high-cardinality calculated column can dwarf the fact table it lives on. Microsoft's [DAX guidance — avoid converting measures to columns](https://learn.microsoft.com/power-bi/guidance/dax-avoid-converting-use-cases) frames this as a core modeling discipline.

## How to apply

If the value should **respond to slicers/filters** or is an **aggregation**, it is a measure. Only use a calculated column when you need a per-row value to **group by, filter on, or relate** that genuinely can't be done upstream in Power Query or the source.

```dax
-- DON'T: a calculated column that pre-aggregates — wrong under any filter, costs memory per row.
-- Sales[TotalMargin] = Sales[Amount] - Sales[Cost]   (per-row is fine to group on, but the *total* must be a measure)

-- DO: a measure that respects filter context and stores nothing.
Total Margin =
SUMX (
    Sales,
    Sales[Amount] - Sales[Cost]
)

Margin % =
VAR _margin  = [Total Margin]
VAR _revenue = SUM ( Sales[Amount] )
RETURN
DIVIDE ( _margin, _revenue )   -- DIVIDE, not "/", to handle divide-by-zero safely
```

**Do:**
- Default every "how much / how many / what %" to a measure.
- Use `VAR` to name intermediate results — readability and one-time evaluation.
- Use `DIVIDE()` over the `/` operator to avoid divide-by-zero errors.
- Push genuinely per-row derived columns **upstream** into Power Query or the source view where they compress better and refresh once.

**Don't:**
- Create a calculated column to hold a sum/average/count — those are filter-context-dependent and belong in a measure.
- Materialize a high-cardinality calculated column (e.g., a concatenated key with millions of distinct values) when a measure or a Power Query transform would do.
- Reference a calculated column inside a measure when the same logic could live in the measure's `SUMX`/`AVERAGEX` iterator.

## Edge cases / when the rule does NOT apply

- A **per-row classification you must slice or group by** (e.g., a price band "Low/Med/High" used as an axis) legitimately needs a calculated column or, better, a Power Query column.
- A **relationship key** that must be computed from multiple columns needs a calculated column if it can't be built upstream.
- **Calculation groups** (Tabular Editor) replace many near-duplicate measures (time-intelligence variants, currency conversion) — prefer them over both columns and copy-pasted measures.
- In **Direct Lake** storage, calculated columns are limited/preview (unmaterialized) — push derivations to the Delta source instead.

## See also

- [`bi-star-schema-not-flat-table.md`](./bi-star-schema-not-flat-table.md) — the modeling shape these measures sit on
- [`../skills/power-bi/resources/dax-patterns-and-performance.md`](../skills/power-bi/resources/dax-patterns-and-performance.md) — VAR, calculation groups, DAX Studio
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — `## Decision Tree: Power BI — Measure vs calculated column`
- [`../agents/power-platform-tester.md`](../agents/power-platform-tester.md) — owns DAX measure-correctness tests (the `EVALUATE` suite)

## Provenance

Grounded in [DAX guidance: avoid converting measures to calculated columns](https://learn.microsoft.com/power-bi/guidance/dax-avoid-converting-use-cases) and [Data reduction techniques for Import modeling](https://learn.microsoft.com/power-bi/guidance/import-modeling-data-reduction) (retrieved 2026-05-30). Encodes the `power-bi` skill's "put business logic in measures, not duplicated across visuals or calculated columns."

---

_Last reviewed: 2026-05-30 by `claude`_
