# Use context filters for one expensive early cut; let query fusion combine like-grained sheets

**Status:** Pattern — promote a filter to context only when something downstream must see the reduced set; design dashboard sheets so the engine can *fuse* their queries rather than fragment them.

**Domain:** Performance

**Applies to:** `tableau`

---

## Why this exists

Two engine behaviors are routinely misunderstood and so misused. **Context filters** create a temporary, materialized subset that is computed *before* normal dimension filters and `FIXED` LODs — useful when a `FIXED` calc or a top-N must operate on an already-narrowed population (e.g. "top 10 products *within the selected region*"). But every context filter builds a temp table, so making *every* filter a context filter (a myth that "context = faster") can be net-slower than no context at all. Separately, **query fusion** is the engine combining multiple worksheets that hit the *same data source at the same grain with compatible filters* into one query — so a dashboard of six KPI tiles off one extract can run *one* query instead of six. Mismatched filters, mismatched grain, or per-sheet data-source filters *break* fusion and multiply the query count. Knowing which behavior you want — and not breaking the one you don't — is what separates a 2-second dashboard from a 20-second one.

## How to apply

Promote to context deliberately; keep dashboard sheets fusion-compatible.

```
CONTEXT FILTER — use ONLY when something downstream must see the reduced set:
  ✓ a FIXED LOD must compute over the filtered population, not the whole table
  ✓ a top-N / "Show me the top 10 within the current filter" must rank inside the subset
  ✓ one genuinely expensive early cut that shrinks the working set for everything after it
  ✗ NOT every filter — each context filter materializes a temp table (overhead, not free speed)

QUERY FUSION — keep it intact across a dashboard:
  ✓ point all KPI tiles at the SAME data source at the SAME grain
  ✓ use the SAME filters (or dashboard-level filter actions) across the fused sheets
  ✗ per-sheet data-source filters, mismatched grain, or divergent quick filters → fusion breaks,
    query count multiplies (6 tiles → 6 queries instead of 1)
```

```
EXAMPLE — context done right:
  "Top 10 SKUs by sales in the region the user picks."
  [Region] as a CONTEXT filter → the Top-10 SKU filter (and any FIXED LOD) ranks within that
  region, not across all regions. Without context, the top-10 ranks globally, then the region
  filter trims survivors → wrong, sparse result.

EXAMPLE — fusion preserved:
  Six headline tiles (Sales, Orders, AOV, Margin, Returns, Customers) all off one Hyper extract
  at order grain, same date/region filter applied dashboard-wide → engine fuses to ~1 query.
  Give one tile its own data-source filter and you fork it back into a separate query.
```

**Do:**
- Reach for a context filter when a `FIXED` LOD or top-N must operate on the *filtered* population.
- Keep one expensive early cut as the context; let cheap filters stay ordinary dimension filters.
- Build dashboard tiles on one source at one grain with shared filters so the engine can fuse them.

**Don't:**
- Believe "make it a context filter" is a universal speed-up — it adds a temp-table build.
- Fragment a fused dashboard with per-sheet data-source filters or mismatched grain.
- Use context to *order* unrelated filters when no `FIXED`/top-N depends on the order.

## Edge cases / when the rule does NOT apply

- **No `FIXED` LOD and no top-N downstream** — you probably don't need a context filter at all; a plain dimension filter is fine.
- **Tiny data** — context's temp-table overhead can outweigh its benefit; measure.
- **Sheets that genuinely need different grains/sources** — they *can't* fuse; that's correct, not a bug — just don't expect single-query behavior.
- **Fusion behavior is version-dependent** — the exact rules for what fuses change across releases; verify against the current Performance Recorder output rather than assuming `[verify-at-build]`.

## See also

- [`./perf-filter-at-the-source.md`](./perf-filter-at-the-source.md) — the filter-layer ladder context sits inside
- [`./perf-minimize-marks-and-quick-filters.md`](./perf-minimize-marks-and-quick-filters.md) — the rendering/quick-filter side of perf
- [`./calc-lod-for-grain-mismatch.md`](./calc-lod-for-grain-mismatch.md) — the `FIXED` LODs that interact with context
- [`../knowledge/data-performance-decision-trees.md`](../knowledge/data-performance-decision-trees.md) — `## Decision Tree: Where to filter` and the perf-recorder ladder
- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — the agent that owns this rule
- Tableau Help, "Use context filters" and "How VizQL fuses queries" / order-of-operations `[verify-at-build]`

## Provenance

Codifies the agent's discipline steps 5–6 and constitution house opinion #5. Context-filter ordering (before dimension filters and `FIXED` LODs) is core order-of-operations; query fusion is an internal VizQL optimization whose exact match rules are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
