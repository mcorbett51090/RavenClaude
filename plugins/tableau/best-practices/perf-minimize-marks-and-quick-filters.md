# Minimize marks and the things that issue queries — rendering scales with marks, latency with quick filters

**Status:** Primary diagnostic — when a view is slow *after* the query returns, suspect mark count and high-cardinality quick filters first.

**Domain:** Performance

**Applies to:** `tableau`

---

## Why this exists

Tableau's cost splits cleanly: **query time** is the database/engine returning rows, **rendering time** is the client/VizQL server drawing marks, and a **quick filter** adds its *own* domain query just to populate its list of values. A scatter of 250,000 points behind a single tooltip, a text table with tens of thousands of cells, or a map with a mark per address will be slow *no matter how fast the query is* — because the bottleneck is drawing, not fetching. Worse, a "Show All Values in Database" quick filter on a high-cardinality dimension (every Customer, every SKU) fires a `SELECT DISTINCT` against the full domain on load and refresh, often slower than the viz itself. Designers add these reflexively ("let them filter by customer") and inherit a dashboard that's sluggish before anyone interacts with it. The fix is to draw fewer marks and to stop high-cardinality filters from querying the whole domain.

## How to apply

Cut marks, then tame the filters that issue their own queries.

```
MARKS — draw fewer:
  • Aggregate instead of plotting raw rows (SUM by category, not 200k individual points).
  • Cap detail: don't put a high-cardinality field on Detail "just in case" — each value is a mark.
  • Split a giant crosstab into summary + drill, rather than one 50k-cell table.
  • A target of "marks in the low thousands" renders smoothly; tens of thousands starts to drag.

QUICK FILTERS — stop the domain query:
  • Prefer "Only Relevant Values" over "All Values in Database" (still a query, but a smaller one)
  • For a huge domain use a "Wildcard match" / type-in filter, NOT a multi-select checklist.
  • Don't show "(All)" multi-value lists on dimensions with thousands of members.
  • Consider a parameter (no domain query) where the choice list is fixed/small.
```

```
EXAMPLE — "customer drill dashboard, 1.2M customers, loads in 28s"
  Cause via Performance Recorder: two events dominate — (1) a quick filter "Customer Name:
  All Values in Database" issuing SELECT DISTINCT over 1.2M rows; (2) 1.2M-mark detail scatter.
  Fix: replace the customer quick filter with a wildcard type-in; aggregate the scatter to
  segment-level summary with drill-to-detail on click. Load 28s → ~3s.
```

**Do:**
- Aggregate to the visible grain; let detail be revealed by interaction, not pre-drawn.
- Use "Only Relevant Values" or a wildcard/type-in filter for high-cardinality dimensions.
- Use parameters for small fixed choice lists (they issue no domain query).

**Don't:**
- Put a high-cardinality field on Detail without a reason — every distinct value is a mark.
- Default quick filters to "All Values in Database" on large dimensions.
- Ship a single huge crosstab when a summary-plus-drill renders a fraction of the marks.

## Edge cases / when the rule does NOT apply

- **A genuinely point-level analysis** (a true scatter where every point matters, a precise map) needs its marks — optimize the *query* and *filters* around it instead, and accept the render cost.
- **Small domains** — a quick filter on 12 regions is fine at "All Values"; the rule targets high cardinality.
- **Density marks / hexbin** — built for "many points"; use them rather than raw circles when density is the message.
- **Print/export crosstabs** where the full table *is* the deliverable — pre-aggregate where possible, but the cells are the requirement.

## See also

- [`./perf-filter-at-the-source.md`](./perf-filter-at-the-source.md) — remove the rows before they become marks
- [`./perf-context-filters-and-query-fusion.md`](./perf-context-filters-and-query-fusion.md) — fewer, fused queries
- [`./data-extract-optimization.md`](./data-extract-optimization.md) — aggregate the extract so fewer rows arrive
- [`../knowledge/data-performance-decision-trees.md`](../knowledge/data-performance-decision-trees.md) — `## Decision Tree: Diagnosing a slow workbook (the Performance Recorder ladder)`
- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — the agent that owns this rule
- Tableau Help, "Optimize workbook performance" and "Quick filters" guidance `[verify-at-build]`

## Provenance

Codifies the agent's discipline step 6 ("Minimize marks and the things that issue queries") and constitution anti-pattern "High-cardinality quick filters / 'show all values' on a large extract." The marks-vs-query-vs-render cost split and the quick-filter domain-query behavior are core VizQL performance mechanics; render thresholds are heuristic and hardware-dependent — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
