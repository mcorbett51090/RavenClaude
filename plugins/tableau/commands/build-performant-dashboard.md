---
description: "Build a Tableau dashboard that is fast by design and answers the question — pick the chart from the question class, filter early and cheap, minimize marks and quick filters, keep sheets fusion-compatible, and respect axis and accessibility integrity."
argument-hint: "[the dashboard, e.g. 'a regional sales overview for sales leadership']"
---

# Build a performant dashboard

You are running `/tableau:build-performant-dashboard`. Build the dashboard the user described (`$ARGUMENTS`) so it is fast *by design* and answers its question — the work the `tableau-viz-engineer` agent owns. Load time is set mostly by decisions made while building, not by hardware.

## When to use this

You are designing or building a new dashboard/viz. NOT for rescuing an already-slow finished dashboard (that is `/tableau:tune-workbook-performance`) and NOT for the underlying data model (that is `/tableau:design-data-source-and-extract`).

## Steps

1. **Pick the chart from the question class, never the aesthetic** (`viz-chart-type-follows-the-question.md`): classify the question (comparison / trend / distribution / correlation / part-to-whole / geographic) and map to the mark — a sorted bar for "which is biggest," not a donut the reader must estimate angles from (Cleveland & McGill ranking).
2. **Filter early and cheap** (`perf-filter-at-the-source.md`): push each filter to the lowest layer its requirement allows — source/extract filter first (rows never enter the workbook), then data-source filter, then context, with the ordinary dimension filter last.
3. **Minimize marks and quick filters** (`perf-minimize-marks-and-quick-filters.md`): every mark is a render unit and every "show all values" quick filter on a high-cardinality field adds a query — keep the hot path cheap as you build.
4. **Keep dashboard sheets fusion-compatible** (`perf-context-filters-and-query-fusion.md`): sheets hitting the same source at the same grain with compatible filters fuse into one query — mismatched filters/grain or per-sheet data-source filters break fusion and multiply queries. Promote a filter to context only when a FIXED LOD or top-N must see the reduced set (every context filter builds a temp table).
5. **Get axis and dual-axis integrity right** (`viz-axis-and-dual-axis-integrity.md`): don't truncate a bar axis to exaggerate, and only dual-axis two genuinely related measures (synchronize when comparable).
6. **Build for formatting and accessibility** (`viz-formatting-and-accessibility.md`), wire interactivity with `viz-actions-and-interactivity.md`, and treat the whole performance posture as designed-in per `viz-dashboard-performance-by-design.md`.

## Guardrails

- A 50,000-mark crosstab is slow no matter the hardware — reduce marks before reaching for a bigger box.
- "Context = faster" is a myth: making every filter a context filter can be net-slower because each builds a temp table.
- Performance retrofitted after a dashboard is "slow" loses the cheap fixes — design it in, don't tune it later.
