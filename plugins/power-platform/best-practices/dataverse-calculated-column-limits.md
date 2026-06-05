# Cap calculated columns and formula columns before they bloat the schema

**Status:** Pattern
**Domain:** Dataverse data modeling
**Applies to:** `power-platform`

---

## Why this exists

Dataverse supports three "server-side derived value" column types — calculated columns (legacy), formula columns (Power Fx, GA 2023), and rollup columns — and each carries a different runtime cost model. Calculated columns run on every read and every save; formula columns run on demand but add a join-like dependency that can cascade recalculation; rollup columns are async but count against org-wide recalculation quota. Stacking more than a handful of these on a high-volume table creates an invisible performance and quota tax that surfaces as slow form loads, slow saves, and throttling — with no obvious culprit in the audit log.

## How to apply

Before adding a calculated/formula/rollup column, ask: does this value need to be stored, or can it be computed in the consuming app?

```
Decision order (escalate only if the lower tier fails):
1. Compute in the app layer (Power Fx, DAX, or a view) — zero server cost.
2. Formula column — if the value must travel in a query, be indexed, or be read by connectors.
3. Rollup column — only for aggregations across child rows; accept async staleness.
4. Calculated column — legacy only; prefer formula columns for new work.
5. Plug-in PostOperation — when the value has side effects or the formula language can't express it.
```

**Do:**
- Keep formula columns to fewer than 10 per table on any table with > 50,000 rows.
- Use `@Computed` Dataverse views (FetchXML aliased expressions) to push computation to query time, not save time.
- Document every calculated/rollup column with a `Description` explaining its computation source so future agents don't duplicate it.

**Don't:**
- Stack rollup columns on a parent table that has millions of children — async recalculation queue depth is a tenant-wide shared resource.
- Use a calculated column to replicate a parent-lookup field value onto the child ("denormalise") when Power Fx or a DAX relationship can express it at read time.
- Leave the `Recalculate` trigger on a rollup column set to the default if the business only needs daily freshness.

## Edge cases / when the rule does NOT apply

A formula column whose output must be indexed for a Dataverse search or filter is legitimate even on a high-volume table — storage cost is paid once; query performance pays back every time. Document the reason on the column.

## See also

- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owns the data model and column-type decisions
- [`./dataverse-rollup-vs-calculated-vs-plugin.md`](./dataverse-rollup-vs-calculated-vs-plugin.md) — the tier-selection tree

## Provenance

Codifies `dataverse-architect`'s opinion from CLAUDE.md §3 #7 ("lowest-tier mechanism that does the job") applied specifically to server-side derived columns; supported by Microsoft Learn Dataverse formula-column performance guidance.

---

_Last reviewed: 2026-06-05 by `claude`_
