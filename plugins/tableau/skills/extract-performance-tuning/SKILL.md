---
name: extract-performance-tuning
description: "Playbook for diagnosing and fixing slow Tableau workbooks: the measurement-first approach, the six extract optimisation levers, query performance recording interpretation, and the view-level and data-source-level fixes that address 90% of performance complaints. Owned by tableau-data-architect."
---

# Extract Performance Tuning

## When to invoke

- A workbook loads slowly or times out on Tableau Server/Cloud.
- An extract refresh is running longer than expected.
- Users report a dashboard that worked fine on 1 M rows is slow at 10 M rows.
- Choosing between a live connection and an extract for a new workbook.

## Step 1 — Measure before tuning

Always start with Tableau's built-in instrumentation. Guessing the bottleneck wastes time.

1. **Performance Recording** — Help → Settings and Performance → Start Performance Recording. Interact with the slow view, then Stop. The recording workbook shows query time, rendering time, and layout time. The query bar is where most gains live.
2. **Stats for Viz Rendering** — Server: Admin → Stats for Viz Rendering (shows query time per viz load). Useful for identifying the worst-offending workbooks fleet-wide.
3. **Explain Data** (optional) — right-click a mark to see the contributing fields and whether an index is being used on the Hyper extract.

**Target thresholds:**

| Operation | Acceptable | Investigate |
|---|---|---|
| Initial viz load | < 3 s | > 5 s |
| Filter action | < 1 s | > 2 s |
| Extract refresh (full) | < 10 min | > 30 min |

## Step 2 — Extract optimisation levers (apply in order)

### 2a. Filter the extract at the source

Apply an extract filter to materialise only the rows the workbook needs. A 10 M row table filtered to 2 M rows reduces Hyper I/O by 80 %.

1. In the Data Source tab: Extract → Edit → Filters → Add.
2. Date-range filters (`Last N months`) are the highest-leverage; apply them first.
3. Never use `OR` conditions in extract filters — Hyper cannot push them to source databases efficiently.

### 2b. Aggregate the extract

For summary dashboards that never drill to row level: aggregate the extract to the view's grain in the Extract editor. Reduces row count by orders of magnitude.

Only do this if no workbook sheet needs row-level data — aggregated extracts cannot be disaggregated.

### 2c. Add a Hyper materialised calculation

Tableau Hyper (Tableau 2022.4+) supports materialised calculations: pre-compute expensive fields in the extract rather than at query time. Right-click a calculated field in the Data Source tab → Materialise in Extract.

Best candidates: string parsing, nested LODs, date truncations on high-cardinality fields.

### 2d. Incremental refresh

For append-only sources (event logs, transaction tables): configure incremental refresh on a date or integer key column. Full refreshes on unchanged historical data are pure waste.

Incremental refresh requirements:
- Source must have a reliable, monotonically increasing column (`created_at`, `event_id`).
- Avoid incremental refresh on tables with updates to historical rows — missed updates cause silent data drift.

### 2e. Reduce high-cardinality quick filters

A quick filter with "Show all values" executes a separate query per load to populate the filter list. On a 10 M row extract, a `Customer Name` quick filter with 500 K distinct values can add 5 s to every page load.

Fixes: use "Relevant values" (context filter), a typed search filter, or a parameter instead of a quick filter for high-cardinality dimensions.

### 2f. Minimise marks and marks-per-view

Each rendered mark is a query row that Tableau VizQL must process. Views with > 5 000 marks become slow to render regardless of data volume.

- Replace a scatter plot of 100 K points with a hexbin or aggregated heat map.
- Use `Reference Lines` or `Trend Lines` instead of a mark for summary statistics.
- Replace row-level text tables with aggregated summaries; use drill-through actions to the detail view.

## Step 3 — Relationship and join fixes

If the performance recording shows join time (not query time) as the bottleneck:

| Symptom | Fix |
|---|---|
| Slow cross-database join | Move to a physical table join inside a single data source, or pre-join in Prep |
| Relationship fan-out on many-to-many | Add a level-of-detail aggregate to one side before the relationship |
| Blend re-querying the secondary source per filter | Replace with a relationship if the data model allows |

## Pitfalls

- Tuning without a performance recording — anecdotal "it feels slow" cannot identify which query is the problem.
- Applying materialised calculations to low-cardinality fields — the overhead of materialising outweighs the gain for simple lookups.
- Incremental refresh on a table that has late-arriving or corrected rows — silent data errors are worse than slow refreshes.
- Using a "Full Extract" with no filters on a table with 50 M+ rows and then wondering why the extract is 8 GB.
