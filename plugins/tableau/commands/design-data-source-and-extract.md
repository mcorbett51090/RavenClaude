---
description: "Design a governed Tableau data source — model with relationships first, choose extract-vs-live against a named freshness requirement, shape and incrementally refresh the extract, and publish it certified and separated from workbooks."
argument-hint: "[the data source, e.g. 'a Sales source over Orders + OrderLines + Customers']"
---

# Design a data source and extract strategy

You are running `/tableau:design-data-source-and-extract`. Model the source the user described (`$ARGUMENTS`) at the right grain, pick the right connection mode, and publish it as a governed, certified, separated data source — the work the `tableau-data-architect` agent owns. Most "wrong total" bugs are grain bugs decided here, not calc bugs.

## When to use this

You are standing up (or fixing) the data layer behind one or more workbooks. NOT for tuning an already-built slow dashboard (that is `/tableau:tune-workbook-performance`) and NOT for the view/chart design (that is `/tableau:build-performant-dashboard`).

## Steps

1. **Model in the logical layer with relationships first** (`data-relationships-before-joins.md`): relate tables on their keys and keep each at its native grain — a physical inner/left join fans out the coarser side and makes `SUM([Order Total])` double-count. Drop to a physical join only with a written reason.
2. **Choose extract vs live against a named freshness requirement** (`data-extract-vs-live-by-freshness.md`): a Hyper extract is the default — go live only when you can state, in observable terms, why rows must be seconds-old (ops desk, fraud queue). "To be safe" is not a freshness requirement.
3. **Shape the extract to the question** (`data-extract-optimization.md`): hide unused fields *before* extracting (hidden-at-extract-time fields are excluded), aggregate to visible dimensions when no row-level detail is shown, and materialize deterministic calcs so they compute once at refresh.
4. **Set up incremental refresh on a monotonic key** (`data-extract-optimization.md`): turn an hour-long full reload into a seconds-long append keyed on a monotonically increasing column.
5. **Publish the data source separately and certify it** (`server-publish-with-separated-data-sources.md`, `gov-certified-data-sources-and-governance.md`): publish the modeled `.tdsx` on its own with its own refresh schedule, certify it so it carries the badge and sorts to the top, and build workbooks against the *published* source — not embedded per-workbook extracts.
6. Hand off RLS-on-the-source design to `/tableau:set-up-rls-and-governance` so entitlements live once on the certified source, not per workbook.

## Guardrails

- A physical join introduced "just to flatten the data" is how you inherit fan-out you then debug with `COUNTD`/`ATTR` workarounds — prefer relationships.
- An embedded per-workbook extract blocks centralized RLS and clean per-environment connection remapping — separate and certify instead.
- Hiding a field *after* the extract is built doesn't shrink it — hide first, then extract.
