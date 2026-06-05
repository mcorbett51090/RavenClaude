# Compose nested LOD expressions from the inside out

**Status:** Pattern
**Domain:** Calculations / LOD expressions
**Applies to:** `tableau`

---

## Why this exists

A nested LOD expression (an LOD inside another LOD) is the correct tool when a
calculation needs to be evaluated at two different levels of detail sequentially
— for example, "the average of customer-level totals" requires computing each
customer's total at `FIXED [Customer ID]` granularity and then averaging those
totals at the view level. Teams that try to do this in a single expression, or
that nest the LODs in the wrong order, get double-counting or an incorrect
aggregation level. The mental model is always inside-out: resolve the inner LOD
first, then apply the outer aggregation to those results.

## How to apply

**Step 1 — identify the two grains:**
- The *inner grain* is the granularity at which you need an intermediate value.
- The *outer aggregation* is the summary applied across the inner-grain values.

**Step 2 — write the inner LOD:**
```
// Inner: total revenue per customer
{ FIXED [Customer ID] : SUM([Revenue]) }
```

**Step 3 — wrap with the outer aggregation:**
```
// Outer: average of customer totals (average customer LTV)
AVG( { FIXED [Customer ID] : SUM([Revenue]) } )
```

**The outer aggregation runs at the view's grain** (whatever dimensions are on
the shelf), not at the inner LOD's grain.

**A three-level example (inner → mid → outer):**
```
// Mid: average daily revenue per customer
{ FIXED [Customer ID] : AVG( { FIXED [Customer ID], [Order Date] : SUM([Revenue]) } ) }
// Outer: average across all customers
AVG( { FIXED [Customer ID] : AVG( { FIXED [Customer ID], [Order Date] : SUM([Revenue]) } ) } )
```

**Do:**
- Build and test each LOD level independently before nesting.
- Verify the grain at each level by adding the relevant dimension to the viz
  and checking that the inner value is correct.
- Use a table calculation (running total, window average) for the outer
  aggregation only when the inner grain is already the view grain.

**Don't:**
- Nest more than two levels without a written explanation of what each level
  computes — three-level LODs become unreadable and unmaintainable.
- Use a nested LOD when a table calculation over the inner LOD would be simpler
  and correct.
- Leave the inner LOD as an ad-hoc calculated field embedded in the outer
  expression without naming it separately first.

## Edge cases / when the rule does NOT apply

- When both grains match the view level: use a regular aggregate, not an LOD.
- When the inner grain is the dimension already on the view: a `FIXED` LOD is
  redundant; use `SUM()` directly.

## See also

- [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) — owns LOD expression design
- [`./calc-lod-for-grain-mismatch.md`](./calc-lod-for-grain-mismatch.md) — the upstream rule on when to use an LOD at all
- [`./calc-aggregate-vs-row-level.md`](./calc-aggregate-vs-row-level.md) — grain awareness required before writing any LOD

## Provenance

Codifies the nested LOD pattern from Tableau's official LOD expression reference
documentation `[verify-at-build]` and the house opinion "model granularity before
you calculate" from `CLAUDE.md` §3. Standard Tableau calculation engineering
practice for multi-grain summaries.

---

_Last reviewed: 2026-06-05 by `claude`_
