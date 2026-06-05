# Isolate data sources on a multi-source dashboard to prevent query fan-out

**Status:** Pattern
**Domain:** Performance / dashboard design
**Applies to:** `tableau`

---

## Why this exists

A dashboard that mixes sheets from two or more data sources triggers separate
query batches for each source. If a filter action spans multiple data sources,
Tableau must execute the filter against each source independently — multiplying
the query count with each cross-source interaction. On a live connection, a
five-sheet cross-source dashboard can fire 20+ queries on a single filter click.
Teams that don't consider source isolation during dashboard design discover the
latency only after the dashboard is published and being used.

## How to apply

**Design principle:** minimise the number of distinct data sources on a
dashboard and isolate sources by purpose.

| Anti-pattern | Better approach |
|---|---|
| 6 sheets from 4 different sources on one dashboard | Consolidate upstream into a single, well-modeled data source or a Prep flow that joins the needed tables |
| Cross-source filter action (filter sheet from source A using a click on source B) | Use a URL action, parameter action, or blend selectively — avoid cross-source filter actions |
| KPI tiles from operational DB + charts from the warehouse | Materialise the KPI data into the warehouse; query from one source |

**When multiple sources are genuinely required:**
1. Ensure sheets from different sources do not share filter actions that fan
   out to all sources.
2. Use parameter actions (not filter actions) to pass values across sources —
   a parameter update does not trigger a query on sources that aren't using
   the parameter.
3. Implement source-specific context filters to reduce the dataset each source
   queries before the cross-source join (if using blends).

**Do:**
- Profile the dashboard with the Performance Recorder after adding each new source.
- Favour a single well-modeled extract or a Prep flow join over on-the-fly
  cross-source dashboards.
- Document the source topology in the workbook's description field.

**Don't:**
- Use filter actions across data sources on a live-connection dashboard without
  profiling the query count.
- Treat a data blend as a substitute for proper upstream data modeling when
  the query volume is high.
- Add a sheet from a new source without checking what the cross-source filter
  impact will be.

## Edge cases / when the rule does NOT apply

- Extract-based dashboards: all queries hit the local `.hyper` files; cross-
  source query fan-out is low-latency; the rule is less critical but the
  design discipline still applies.

## See also

- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — owns data source design and query architecture
- [`./viz-dashboard-performance-by-design.md`](./viz-dashboard-performance-by-design.md) — the upstream rule on dashboard performance as a design constraint
- [`./data-blend-is-a-last-resort.md`](./data-blend-is-a-last-resort.md) — cross-source blends are the fallback when proper joins are impossible

## Provenance

Standard Tableau dashboard performance best practice. Cross-source query
fan-out is documented in Tableau's performance best practices guide
`[verify-at-build]`. House opinion #5 from `CLAUDE.md` §3 ("performance is
designed, not tuned later").

---

_Last reviewed: 2026-06-05 by `claude`_
