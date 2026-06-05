# In Tableau Prep, choose join vs union based on whether rows or columns are being combined

**Status:** Absolute rule
**Domain:** Data / Tableau Prep
**Applies to:** `tableau`

---

## Why this exists

Tableau Prep exposes both join and union steps, and teams routinely confuse them.
A join combines tables horizontally — it adds columns from a second table to
matching rows in the first. A union combines tables vertically — it stacks rows
from two tables that share the same schema. Using a join when a union is needed
produces cross-joined Cartesian products or many-to-many matches. Using a union
when a join is needed produces NULL columns because the schemas differ. The
failure is often silent: the row count looks plausible but the data is wrong.

## How to apply

| Goal | Correct Prep step | Mental test |
|---|---|---|
| Combine tables with the same schema (monthly files, regional tables) | Union | "Do they have the same columns?" → Union |
| Add attributes from a second table via a shared key | Join | "Do they share a key column?" → Join |
| Combine different-grain tables for enrichment | Join (specific join type) | "One row per key in each table?" → Join |

**Union checklist before applying:**
- Both inputs have the same column names and types (Prep will warn on mismatches).
- The union will not introduce NULL columns for schema differences.
- You are not relying on union to deduplicate — it stacks rows, it does not dedup.

**Join checklist before applying:**
- The join key is the same grain in both tables (a many-to-many join fans out rows).
- You have chosen the correct join type (inner, left, full outer) explicitly.
- You have inspected the join clause count — a Prep join clause with an
  accidental extra condition silently filters rows.

**Do:**
- State the goal ("I'm adding columns" vs "I'm stacking rows") before choosing
  the step.
- Inspect row counts after any join or union step to catch fan-out or loss.
- Use the Prep join configuration panel to verify the join clause and the
  join type explicitly.

**Don't:**
- Use a join to combine two tables that have the same schema — this creates a
  Cartesian product.
- Use a union to combine two tables with different columns — the NULL columns
  will propagate downstream.
- Leave the join type on the default without verifying it matches your intent.

## Edge cases / when the rule does NOT apply

- Combining a slowly-changing dimension with a fact table where the SCD
  adds multiple rows per key: this is a many-to-many risk; design the SCD
  handling upstream in the warehouse, not in Prep.

## See also

- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — owns Prep flow design
- [`./prep-incremental-and-idempotent-flows.md`](./prep-incremental-and-idempotent-flows.md) — the idempotency rule for the Prep flow that contains this join or union
- [`./data-relationships-before-joins.md`](./data-relationships-before-joins.md) — prefer Tableau's logical layer for workbook-level combination

## Provenance

Codifies the join vs union distinction from Tableau Prep Builder documentation
`[verify-at-build]`. The row-count inspection discipline is standard ETL
validation practice applied to Prep flows.

---

_Last reviewed: 2026-06-05 by `claude`_
