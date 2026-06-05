---
scenario_id: 2026-06-05-slow-dashboard-quick-filter-domain-queries
contributed_at: 2026-06-05
plugin: tableau
product: tableau-cloud
product_version: "Tableau Cloud 2025.2; extract (Hyper)"
scope: likely-general
tags: [performance, performance-recorder, quick-filters, query-fusion, marks]
confidence: high
reviewed: false
---

## Problem

An executive dashboard took ~40 seconds to load and stuttered on every filter change. The team
had spent a day "optimizing calculations" with no improvement, because they were guessing at
the cause instead of measuring it. The actual cost was **many small queries**, not one slow one
— a wall of high-cardinality "show all values" quick filters each firing its own domain query.

## Permissions context

- Explorer/author on a published, certified data source (extract). No RLS or governance limit
  in play — purely a performance-design problem.
- The data source was already an extract; the team assumed "extract = fast" and looked
  elsewhere.

## Attempts

- Tried: rewriting LOD calcs and simplifying table calcs (a full day) → near-zero improvement.
  The calcs weren't the bottleneck; this was effort spent without evidence.
- Tried: switching from extract to a bigger extract / adding RAM → no change (the problem wasn't
  data volume per se).
- **Worked — measure first:** turned on the **Performance Recorder**, reproduced the slow load,
  and **sorted events by duration**. The dominant category was **Executing Query** with *many*
  short queries — query fragmentation, not a single slow query. Root causes and fixes:
  1. Six "show all values in database" quick filters on high-cardinality dimensions → each
     issued its own domain query. Switched them to **"Only Relevant Values"** / wildcard
     type-in, eliminating most domain queries.
  2. Sheets pulled from the same source at different grains/filters, so the engine **couldn't
     fuse** their queries. Aligned source/grain/filters so query fusion kicked back in.
  3. One crosstab rendered ~120k marks. Capped detail + split it into a summary + drill,
     cutting render time too.

## Resolution

**Run the Performance Recorder and read the longest events before changing anything — the cause
is usually not the one you assumed.** Leaf in
[`../knowledge/data-performance-decision-trees.md`](../knowledge/data-performance-decision-trees.md)
(*Diagnosing a slow workbook* ladder) + the audit skill
[`../skills/workbook-performance-audit/SKILL.md`](../skills/workbook-performance-audit/SKILL.md).
Durable lessons:

- **"Slow" has categories — Executing Query (few vs many), Computing/Generating, Rendering,
  Connecting/Geocoding — and they have *different* fixes.** Optimizing calcs when the cost is in
  *many domain queries* is wasted effort. Always sort the recorder events by duration first.
- **High-cardinality "all values" quick filters are a top offender.** Each fires a domain query
  on load and on relevant changes. Prefer "Only Relevant Values" or a wildcard/type-in filter,
  or move the cut to the data source.
- **Restore query fusion.** Many small queries from one source often means the sheets diverged
  on grain/filters; aligning them lets the engine fuse. Then check **mark count** for the
  rendering half.

Cross-reference: the canonical mechanism is the *Diagnosing a slow workbook (Performance
Recorder ladder)* decision tree; this note is the field symptom (a day lost to the wrong layer)
that should send the next consultant to the recorder before the calc editor.
