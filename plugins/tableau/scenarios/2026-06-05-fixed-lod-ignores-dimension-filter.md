---
scenario_id: 2026-06-05-fixed-lod-ignores-dimension-filter
contributed_at: 2026-06-05
plugin: tableau
product: tableau-desktop
product_version: "2025.2"
scope: likely-general
tags: [lod, fixed, order-of-operations, context-filter, wrong-totals]
confidence: high
reviewed: false
---

## Problem

A "% of category total" KPI on a sales dashboard was **right at the workbook level but wrong
the moment a user picked a region in a quick filter.** The denominator (a `FIXED [Category]`
LOD computing category sales) didn't shrink when the region filter was applied — so each
region's bars summed to far less than 100%, and the client thought the data was broken. The
calc itself was textbook; the bug was *when* it computed relative to the filter.

## Permissions context

- Tableau Desktop author, Explorer on the published data source — full authoring rights, no
  governance constraint. This was a calculation-semantics bug, not an access one.
- Single published data source (relationships, extract). No RLS in play.

## Attempts

- Tried: rewriting the LOD as `INCLUDE`/`EXCLUDE` → changed the number but still wrong; the
  author was guessing at the LOD type instead of reasoning about order of operations.
- Tried: a table calc `% of Total` → worked for the simple view but broke when a second
  dimension was added to the view (addressing/partitioning silently wrong — a different trap,
  see `2026-06-05-slow-dashboard-quick-filter-domain-queries.md`'s cousin in the calc bank).
- Tried: moving the region filter to a data-source filter → fixed the number but removed the
  user's ability to switch regions at runtime (wrong tradeoff — the filter had to stay
  interactive).
- **Worked:** kept the `FIXED [Category]` LOD and added the **region dimension filter to
  context** (right-click → Add to Context). `FIXED` LODs are computed **before** dimension
  filters in Tableau's order of operations, but **after** context filters — so promoting the
  region filter to context makes the `FIXED` denominator see the filtered subset.

## Resolution

**Reason from Tableau's order of operations, not by swapping LOD keywords.** The leaf to apply
is in [`../knowledge/viz-calc-decision-trees.md`](../knowledge/viz-calc-decision-trees.md)
(LOD-vs-table-calc tree) and the filter tree in
[`../knowledge/data-performance-decision-trees.md`](../knowledge/data-performance-decision-trees.md)
(*Where to filter* → "Must a FIXED LOD or top-N see the reduced set first?" → **context
filter**). Two durable lessons for the next consultant:

- **A `FIXED` LOD that ignores a dimension filter is working as designed, not broken.** `FIXED`
  runs before dimension filters; `INCLUDE`/`EXCLUDE` run after. If the user's interactive filter
  must shrink a `FIXED` result, promote that filter to **context** — don't reach for a different
  LOD type hoping the number changes the right way.
- **Don't fix an order-of-operations bug by moving the filter out of the user's hands.** A
  data-source/extract filter "fixes" the math by deleting the rows, but it also deletes the
  interactivity. Context preserves the runtime filter *and* the math.

Cross-reference: this is the symptom-level field note; the canonical mechanism is the
order-of-operations sequence (extract → data-source → context → dimension → **FIXED** runs
between context and dimension) documented in the calc + filter decision trees. `[verify-at-build]`
the exact order-of-operations diagram against current Tableau Help before quoting it precisely.
