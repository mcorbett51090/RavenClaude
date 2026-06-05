---
name: dashboard-layout-review
description: "Checklist-driven review for Tableau dashboard layout, chart-type selection, formatting, and accessibility — covering the question-first design principle, attention hierarchy, filter placement, colour and font conventions, and the five layout anti-patterns that confuse users. Owned by tableau-viz-engineer."
---

# Dashboard Layout Review

## When to invoke

- Before publishing a new dashboard to Tableau Server/Cloud.
- A stakeholder says the dashboard is "confusing" or "hard to use."
- Standardising dashboard design across a team.
- Reviewing a dashboard built by someone else for quality.

## Gate 1 — Question-first audit

Every sheet in the dashboard should answer a specific business question. For each sheet ask:

1. What is the question this chart answers? (Write it in one sentence.)
2. Does the chart type match the question type?
3. Can a user read the answer in < 5 seconds without explanation?

| Question type | Correct chart types | Common wrong choice |
|---|---|---|
| Trend over time | Line, area | Bar (for time-ordered data > 6 periods) |
| Comparison across categories | Bar (horizontal for long labels), dot plot | Pie / donut (> 5 categories) |
| Part-to-whole | Bar (stacked, 100%) for ≤ 5 categories; treemap for hierarchical | Pie chart with > 6 slices |
| Distribution | Box-whisker, histogram, violin | Average line only (hides spread) |
| Correlation | Scatter plot, heatmap | Dual-axis line (implies causality) |
| Geographic | Filled map, symbol map | Table of values with no spatial context |

Remove any sheet that cannot be assigned a question — it's decoration, not information.

## Gate 2 — Attention hierarchy

Users read dashboards in a Z or F pattern. Place the most important KPI or insight in the top-left. Review the hierarchy:

1. **Primary insight** — one number or chart that answers "so what?" Largest, most prominent.
2. **Supporting context** — 2–3 charts that explain the primary insight's drivers.
3. **Detail** — filters, secondary views, drill-down targets. Smaller, lower, or on a second sheet.

Anti-pattern: treating all charts as equal size and importance — the dashboard looks like a grid of tiles with no focal point.

## Gate 3 — Filter placement and performance review

| Filter type | Use when | Avoid when |
|---|---|---|
| Quick filter (Relevant Values) | Low-cardinality (≤ 50 values); user must see all options | High-cardinality (names, IDs) — use typed search |
| Context filter (Make Context Filter) | Drives FIXED LODs; needs to constrain other filter lists | Every filter — only promote when the dependency requires it |
| Action filter (filter action on click) | Guided drill-through; interactive exploration | Replace-all-values filter across every sheet — too aggressive |
| Parameter | Single-select, user-controlled inputs (date range, metric toggle) | Multi-select — use a set or quick filter |

Flag any quick filter set to "Show All Values" on a field with > 1 000 distinct values — it fires an expensive query on every dashboard load.

## Gate 4 — Formatting checklist

- [ ] **Font**: one font family; 3 sizes maximum (title / label / axis tick). No WordArt.
- [ ] **Colour**: one primary colour palette (3–5 colours); diverging palette for negative/positive; sequential palette for continuous measures. Remove all default blue-on-blue.
- [ ] **Gridlines**: light grey or off — never dark. Remove horizontal gridlines from bar charts (the bars encode the value).
- [ ] **Axis titles**: describe the measure and unit (`Revenue (USD)`); not the field name (`sum of Revenue`). Truncate long axis labels at 45°.
- [ ] **Tooltips**: answer a micro-question, not a data dump. Include the context dimension (date, segment) + the measure + the unit.
- [ ] **Null handling**: decide and document — hide nulls, show 0, or show "N/A" consistently across all sheets.

## Gate 5 — Accessibility checklist

- [ ] Colour is not the only encoding (also use shape, size, or label for colour-blind users).
- [ ] Contrast ratio ≥ 4.5:1 for text on background (WCAG AA).
- [ ] Chart titles are descriptive, not the field name (`Monthly Revenue by Region`, not `Region / Month`).
- [ ] Mark labels are on by default for key metrics — do not make users hover to see the value.
- [ ] Dashboard is navigable via keyboard (Tableau Cloud/Server supports keyboard focus mode).

## Five layout anti-patterns

1. **The "everything on one screen" trap** — 12 charts crammed into 1 200 × 800 px. Rule: ≤ 5 main charts per dashboard view; use navigation or drill-through for detail.
2. **Floating objects over tiled layouts** — z-fighting and alignment drift on different screen sizes. Use tiled layout; float only images/logos.
3. **Unsynchronised dual-axis** — two measures on different scales look correlated when they're not. Always right-click → Synchronise Axis on dual-axis charts, or explain why not.
4. **Truncated zero baseline** — bar charts with a non-zero baseline inflate visual differences. Lock to zero unless the question is explicitly about relative change within a range.
5. **Auto-fit text that breaks on smaller screens** — test at 1 280 × 800 px (laptop) and 1 920 × 1 080 px (desktop) before publish.

## Pitfalls

- Publishing without a mobile layout when > 30 % of users access via Tableau Mobile — Tableau auto-generates a mobile layout but it's rarely usable without manual adjustment.
- Using colour saturation as a continuous encoding on a filled map with outliers — one extreme value washes out everything else; use a diverging or stepped colour palette with a fixed range.
- Omitting sheet titles — users navigating via tab order or screen readers lose context.
