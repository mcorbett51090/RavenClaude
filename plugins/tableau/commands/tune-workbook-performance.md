---
description: "Diagnose and fix an already-slow Tableau workbook — read the performance recording to find the cost driver, push filters down a layer, cut marks and quick filters, restore query fusion, and fix the calc layer (LOD/table-calc/aggregation)."
argument-hint: "[the slow workbook, e.g. 'the exec dashboard takes 25s to load']"
---

# Tune workbook performance

You are running `/tableau:tune-workbook-performance`. Diagnose why the workbook the user named (`$ARGUMENTS`) is slow and fix the actual cost driver, the way the `tableau-viz-engineer` (and `tableau-data-architect` for the data-layer seam) would — measuring before changing, not guessing.

## When to use this

A finished workbook is slow and you need to find and remove the bottleneck. NOT for designing a new dashboard from scratch (that is `/tableau:build-performant-dashboard`) — though the same levers apply preventively there.

## Steps

1. **Find the cost driver before changing anything**: a performance recording localizes whether time is in query execution, rendering, or layout — the two dominant drivers are mark count and query count/shape (`viz-dashboard-performance-by-design.md`).
2. **Push filters down a layer** (`perf-filter-at-the-source.md`): the classic slow-workbook ticket is "200M rows dragged in, then filtered to one region in the view" — move that filter to a source/extract or data-source filter so the rows never enter the workbook.
3. **Cut marks and high-cardinality quick filters** (`perf-minimize-marks-and-quick-filters.md`): reduce the mark count on dense crosstabs and replace "show all values" quick filters on high-cardinality fields, which fire a query each.
4. **Restore query fusion** (`perf-context-filters-and-query-fusion.md`): align sheets to the same source/grain with compatible filters so six KPI tiles run one query instead of six; remove per-sheet data-source filters that fragment it. Audit whether every context filter is actually needed — each builds a temp table.
5. **Fix the calc layer** (`calc-aggregate-vs-row-level.md`, `calc-lod-for-grain-mismatch.md`, `calc-table-calc-addressing-explicit.md`): move string/regex work out of the row path, use a LOD for a genuine grain mismatch rather than forcing it elsewhere, and make table-calc addressing explicit so it computes over the intended partition.
6. **Reconsider the data layer if the model is the bottleneck**: a verbatim full-fat extract or a fan-out join may be the root cause — hand back to `/tableau:design-data-source-and-extract` for extract shaping (`data-extract-optimization.md`) or relationships-over-joins (`data-relationships-before-joins.md`).

## Guardrails

- Don't guess at the fix — read the performance recording first; the felt bottleneck is often not the real one.
- "Context = faster" is a myth: a pile of context filters can be net-slower because each materializes a temp table.
- A data blend is a last resort (`data-blend-is-a-last-resort.md`) — if a slow workbook leans on a blend, the fix is usually a relationship or a published source, not blend tuning.
