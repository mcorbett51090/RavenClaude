---
name: workbook-performance-audit
description: A repeatable, evidence-first Tableau workbook performance audit — run the Performance Recorder, read the longest events, and apply the right lever per dominant event category (Executing Query / Computing / Rendering / Connecting). Use when a workbook or dashboard is slow and you need the cause, not a guess.
---

# Workbook Performance Audit

> **Owner:** `tableau-data-architect` (primary) + `tableau-viz-engineer` (rendering/marks side).
> **Grounded in:** [`../../knowledge/data-performance-decision-trees.md`](../../knowledge/data-performance-decision-trees.md)
> *Diagnosing a slow workbook (the Performance Recorder ladder)* tree.

A disciplined procedure so a "slow dashboard" ticket is diagnosed from **measured evidence**,
not from whichever lever the author reached for first. The #1 failure (see the scenario bank,
`2026-06-05-slow-dashboard-quick-filter-domain-queries.md`) is spending a day "optimizing calcs"
when the cost was in many domain queries — because nobody ran the recorder first.

## When to use

Any time a workbook is slow to load, slow on a filter/parameter change, or slow to render — and
**before** changing a single calc, filter, or extract. Also as a pre-publish gate for any
dashboard headed to a governed prod site.

## The procedure (evidence first)

1. **Reproduce + record.** Turn on the **Performance Recorder** (Help → Settings and Performance
   → Start Performance Recording in Desktop; or the recording workflow on Server/Cloud
   `[verify-at-build]`). Reproduce the *exact* slow action (load, this filter, that parameter).
   Stop the recording to generate the performance workbook.
2. **Sort events by duration — read the longest first.** Do not start fixing the first thing you
   notice. Identify the **dominant event category** by total time:
   - **Executing Query** — database/engine returning rows. Sub-split: **few slow queries** vs
     **many queries**.
   - **Computing / Generating** — an expensive calc / LOD / table calc computing per query.
   - **Rendering** — VizQL drawing marks (client/server).
   - **Connecting / Geocoding** — connection or geocoding overhead.
3. **Apply the lever for the dominant category** (traverse the decision-tree leaf):
   - *Executing Query — few slow* → filter at source, fix the relationship/join, aggregate the
     extract, index upstream. (`../../best-practices/perf-filter-at-the-source.md`)
   - *Executing Query — many* → restore **query fusion** (same source / grain / filters) and kill
     high-cardinality "show all values" quick-filter domain queries → "Only Relevant Values" /
     wildcard. (`../../best-practices/perf-context-filters-and-query-fusion.md`)
   - *Computing / Generating* → push the calc into Prep or materialize it in the extract; fix LOD
     addressing/partitioning. (`../../best-practices/prep-incremental-and-idempotent-flows.md`)
   - *Rendering* → reduce **mark count** (aggregate, cap detail, split a giant crosstab into
     summary + drill). (`../../best-practices/perf-minimize-marks-and-quick-filters.md`)
   - *Connecting / Geocoding* → prefer an extract; cache geocoding / use a spatial join.
     (`../../best-practices/data-extract-vs-live-by-freshness.md`)
4. **Change ONE thing, re-record, compare.** Performance work is iterative; re-run the recorder
   after each change so the improvement is *measured*, not assumed. Stop when the dominant
   category is under the SLA.
5. **Check the structural defaults** (cheap wins, even before the recorder confirms):
   - Extract vs live carries a stated freshness reason; filters pushed to the lowest layer; no
     high-cardinality "all values" quick filters; mark count is bounded; LOD/table-calc
     addressing is explicit; dashboard sheets share source/grain so the engine can fuse.

## Anti-patterns this audit catches

- Optimizing calculations when the cost is in **Executing Query** (the recorder shows it).
- High-cardinality "show all values in database" quick filters firing per-load domain queries.
- A 100k+-mark crosstab rendered on a summary dashboard.
- Sheets diverging on grain/filters so query fusion never engages.
- A live connection with no stated freshness need paying per-interaction latency.

## Output

A short audit report:

```
Slow action: <the exact reproduced action>
Recorder evidence: <dominant event category + total ms + the longest events>
Diagnosis: <decision-tree leaf reached + why>
Levers applied: <one per change, with before/after recorder numbers>
Result: <new load/interaction time vs the SLA>
Residual / escalations: <upstream source/index work → data-platform; security filters → security-reviewer>
```

Follow the team **Output Contract** + the cross-plugin **Structured Output Protocol**. Don't
report "I optimized it" — report the measured before/after and the category that drove the win.

## See also

- [`../../knowledge/data-performance-decision-trees.md`](../../knowledge/data-performance-decision-trees.md) — the Performance Recorder ladder
- [`../../scenarios/2026-06-05-slow-dashboard-quick-filter-domain-queries.md`](../../scenarios/2026-06-05-slow-dashboard-quick-filter-domain-queries.md) — the field symptom
- [`../../best-practices/viz-dashboard-performance-by-design.md`](../../best-practices/viz-dashboard-performance-by-design.md) — designing perf in rather than tuning it later
- [`../../templates/workbook-performance-audit.md`](../../templates/workbook-performance-audit.md) — the fill-in report template
