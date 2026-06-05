# Use composite models and user-defined aggregations to blend Import speed with DirectQuery freshness

**Status:** Pattern
**Domain:** Power BI semantic modeling
**Applies to:** `power-platform`

---

## Why this exists

Import mode gives sub-second query response but requires scheduled refresh — data is never fully live. DirectQuery gives live data but every visual fires a query, and heavily-used reports can throttle the source. Composite models let the two coexist: high-traffic, stable dimensions sit in Import; fast-changing facts stay in DirectQuery. User-defined aggregation tables (pre-aggregated Import tables that Power BI promotes automatically) give DirectQuery reports Import-speed on common aggregations while hitting the live source only for granular drills. Without this pattern, authors default to "all Import" (stale data) or "all DirectQuery" (source hammering) and the business case for freshness vs. speed is never formally made.

## How to apply

1. **Identify storage mode by table role:**

| Table role | Recommended mode |
|---|---|
| Large fact / event table (>10M rows, refreshes frequently) | DirectQuery |
| Dimension / reference table (< 1M rows, changes rarely) | Import (dual mode for relationships) |
| Aggregated summary (pre-grouped facts) | Import, set as aggregation table |

2. **Set dimension tables to Dual mode** when they are shared between a DirectQuery fact and an Import aggregation — Dual tables behave as Import when queried with Import facts and as DirectQuery when queried with DQ facts.

3. **Register aggregation tables** in the Model view → Manage aggregations. Map each aggregation column to its fact-table counterpart (SummarizeColumns, GroupBy, Count).

4. **Test aggregation hits** using Performance Analyzer in Power BI Desktop: a query that hits the aggregation table shows `Direct query` = 0; a granular drill-through shows a non-zero DQ time.

**Do:**
- Use the `PBIP` format (TMDL) and source-control the storage mode assignments so they survive republish.
- Align the aggregation granularity to the most common slicer (e.g., date × region) — an aggregation at a granularity nobody slices by is wasted memory.

**Don't:**
- Put a relationship between a DirectQuery fact and a DirectQuery dimension without testing cross-source join behavior — cross-database DQ relationships have restrictions.
- Enable aggregations on a table that refreshes faster than the aggregation refresh schedule — stale aggregations are worse than no aggregations.
- Use composite models with the Publish to web / anonymous embed surface — composite model + row-level-security requires authenticated embed.

## Edge cases / when the rule does NOT apply

For a Fabric Direct Lake semantic model the storage-mode decision is made at the gold-table layer (TMDL framing, not Import/DQ mode). Composite model design is for Import/DQ Power BI models outside Fabric Direct Lake.

## See also

- [`../agents/power-bi-engineer.md`](../agents/power-bi-engineer.md) — owns semantic model design
- [`./bi-storage-mode-selection.md`](./bi-storage-mode-selection.md) — the primary diagnostic for storage mode choice

## Provenance

Codifies `power-bi-engineer`'s opinion from CLAUDE.md §8 skills/power-bi domain on storage-mode selection; Microsoft Learn composite models + aggregations documentation (standard domain practice).

---

_Last reviewed: 2026-06-05 by `claude`_
