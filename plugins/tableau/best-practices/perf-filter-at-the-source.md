# Filter at the cheapest layer — the fastest query is the row that never enters the workbook

**Status:** Pattern — push every filter as close to the source as the requirement allows; a workbook-level dimension filter is the *last* place to remove rows, not the first.

**Domain:** Performance

**Applies to:** `tableau`

---

## Why this exists

Filtering is layered, and each layer is cheaper than the one above it. A **data-source filter** (or **extract filter**) removes rows *before they are ever stored in or read from the extract* — the workbook never sees them, so no query they would have appeared in pays for them. A **context filter** materializes a temporary subset that downstream filters and `FIXED` LODs see, cutting the working set early. An ordinary **dimension filter** runs inside every viz query against the full domain. Most "slow workbook" tickets are really "we dragged 200M rows into the workbook and then filtered to one region in the view" — the region filter runs *after* the engine already moved the rows. Removing data at the lowest possible layer is the single highest-leverage performance move, because the cheapest query is the one that has fewer rows to begin with.

## How to apply

Push each filter down to the lowest layer its requirement permits.

```
LAYER (cheapest → most expensive):
  1. SOURCE / EXTRACT filter   rows excluded before the extract stores them   ← push here first
  2. DATA-SOURCE filter        applied to every query from this source        ← global cuts
  3. CONTEXT filter            temp subset; FIXED LODs + downstream see it     ← expensive dim cut
  4. DIMENSION filter          per-viz, against the full domain                ← last resort
```

```
EXAMPLE — "dashboard only ever covers the last 2 fiscal years, EMEA region"
  WRONG: live/extract on all 8 years × all regions, then a [Region]=EMEA + [Year]>=2024
         dimension filter in each sheet → every query scans the full table.
  RIGHT: DATA-SOURCE filter [Region]=EMEA and [Order Date] >= dateadd('year',-2, today())
         (or bake it into the EXTRACT filter) → the workbook holds only the rows it can ever show.
  Result: smaller extract, faster refresh, every viz query starts from the reduced set.
```

**Do:**
- Put global, always-true constraints (region scope, date window, active-records-only) in a **data-source / extract filter**.
- Use a **context filter** when an expensive dimension filter must apply *before* a `FIXED` LOD or a top-N.
- Reserve plain **dimension filters** for the interactive choices a user actually changes per session.

**Don't:**
- Load the whole table and filter to a sliver in the view — move that sliver-defining filter to the source.
- Stack many context filters "for speed" — each one recomputes the temp table; context is for the *one* expensive early cut, not every filter (see the context-filter doc).
- Put a user-facing interactive filter in the data source — they can't change it at runtime.

## Edge cases / when the rule does NOT apply

- **User must be able to widen the scope at runtime** — that filter can't live in the data source; keep it a dimension/parameter filter.
- **Small data already** — pushing filters down adds little; don't pre-optimize a thousand-row extract.
- **Context filter overhead** — on a *small* result a context filter can be net-slower (it builds a temp table); only contextualize an expensive early cut (see `perf-context-filters-and-query-fusion.md`).
- **Security filtering** — RLS / user filters are a *security control*, not a perf lever; design them as such and escalate the security verdict.

## See also

- [`./perf-context-filters-and-query-fusion.md`](./perf-context-filters-and-query-fusion.md) — when and why to promote a filter to context
- [`./perf-minimize-marks-and-quick-filters.md`](./perf-minimize-marks-and-quick-filters.md) — the rendering/quick-filter side
- [`./data-extract-optimization.md`](./data-extract-optimization.md) — extract filters as a shaping lever
- [`../knowledge/data-performance-decision-trees.md`](../knowledge/data-performance-decision-trees.md) — `## Decision Tree: Where to filter — source vs data-source vs context vs dimension`
- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — the agent that owns this rule
- Tableau Help, "Filter your data" and the "order of operations" reference `[verify-at-build]`

## Provenance

Codifies the agent's discipline step 5 ("Filter at the cheapest layer") and constitution house opinion #5. The filter order-of-operations (extract → data-source → context → dimension → measure → table-calc) is core Tableau query semantics; verify the current order-of-operations diagram against Tableau Help before quoting it precisely — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
