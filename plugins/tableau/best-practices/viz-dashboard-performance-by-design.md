# Design dashboard performance in — don't tune it later

**Status:** Pattern — performance is a design constraint applied while building (filter at source, minimize marks, keep the hot path cheap), not a rescue operation after a dashboard is already slow.

**Domain:** Viz design / performance

**Applies to:** `tableau`

---

## Why this exists

A dashboard's load time is set mostly by decisions made while building it: how many marks render, how many queries fire, how much work each calc does, and how much data crosses the wire. By the time a finished dashboard is "slow," the cheap fixes are gone and you're retrofitting. Two cost drivers dominate. **Mark count** — every mark is a render unit, so a 50,000-mark crosstab is slow no matter the hardware. **Query count and shape** — each worksheet, each quick filter showing "all values" from a high-cardinality field, each string/regex calc in the row path adds round-trips and CPU. This is house opinion #5: *performance is designed, not tuned later.* The viz engineer owns the **view-side** levers; extract-vs-live, data-model, and query-plan depth seam to `tableau-data-architect`.

## How to apply

Apply the view-side levers as you build, in rough order of payoff:

```
1. FILTER EARLY, FILTER CHEAP
   - Data-source / extract filters trim rows before the viz ever queries.
   - Context filters narrow the set the rest of the view (and FIXED LODs) see.
   - Avoid "Only Relevant Values" on high-cardinality quick filters — it
     re-queries on every interaction. Prefer a wildcard/parameter input.

2. MINIMIZE MARKS
   - Aggregate to the grain the question needs; don't render row-level
     detail nobody reads. Thousands of marks, not hundreds of thousands.
   - Fewer worksheets per dashboard = fewer queries on load.

3. KEEP THE HOT PATH CHEAP
   - No heavy string/regex/nested calcs evaluated per row at render time;
     materialize them in the extract instead.
   - Prefer booleans/integers over strings in calcs on the critical path.

4. LET THE EXTRACT DO THE WORK
   - Aggregated extracts pre-roll the data to the dashboard's grain.
   - (Extract vs live + Hyper tuning -> seam to tableau-data-architect.)
```

**Do:**
- Set data-source / extract filters so the workbook never pulls rows it will discard.
- Budget marks: if a view needs >~10k marks `[verify-at-build]`, ask whether the question needs that detail.
- Use the **Workbook Performance Recorder** to confirm where time actually goes before optimizing.

**Don't:**
- Ship high-cardinality "show all values" quick filters on a large extract.
- Put string concatenation, `REGEXP_*`, or nested LOD/table-calc chains in the per-row hot path.
- Optimize by guess — measure with the Performance Recorder first.

## Edge cases / when the rule does NOT apply

A genuinely small data source (a few thousand rows on a live connection to a fast warehouse) may not need extract-side trimming — don't over-engineer. Operational dashboards that *require* row-level detail (e.g., a case-list table the user scrolls) legitimately carry more marks; the lever there is pagination/Top-N and lazy filtering, not aggregation. Root-cause query slowness (a bad join, a missing index upstream, extract refresh time) is **data-architect** territory, not a view-side fix.

## See also

- [`./calc-table-calc-addressing-explicit.md`](./calc-table-calc-addressing-explicit.md) — keep table calcs off the per-row hot path
- [`./viz-actions-and-interactivity.md`](./viz-actions-and-interactivity.md) — actions vs. high-cardinality quick filters
- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — extract/live, Hyper, query tuning (the data-side seam)
- [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) — owns the view-side levers
- Tableau Help: "Designing Efficient Workbooks" / "Workbook Optimizer" `[verify-at-build]`

## Provenance

Codifies house opinion #5 and the high-cardinality-quick-filter anti-pattern from [`../CLAUDE.md`](../CLAUDE.md). Mark-count and query-count as the dominant cost drivers are documented Tableau performance guidance; specific mark thresholds re-verify against current docs `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
