---
name: lod-expression-builder
description: "Step-by-step playbook for diagnosing the grain mismatch that causes wrong numbers, then selecting and constructing the right LOD expression (FIXED, INCLUDE, EXCLUDE) or table calculation. Includes the LOD-vs-table-calc decision, worked examples, and the common double-counting fixes. Owned by tableau-viz-engineer."
---

# LOD Expression Builder

## When to invoke

- A calculated field is returning wrong totals, double-counted numbers, or unexpected NULLs.
- Deciding between `FIXED`, `INCLUDE`, `EXCLUDE`, and a table calculation.
- Building a ratio-of-total, customer-first-order date, or cohort-entry metric.
- Aggregation at a different granularity than the view's level of detail.

## Step 1 — State the grain before writing a single calc

Answer these before opening the calculation editor:

1. **What is the view grain?** (e.g., one row per order line, per customer per month)
2. **What grain does the metric need?** (e.g., total revenue per customer, regardless of product)
3. **Are they the same?** If yes, a regular aggregate (`SUM`, `AVG`) is sufficient. If no, an LOD is needed.

Most "wrong number" bugs are grain bugs, not calculation bugs. Naming the mismatch first saves an hour of trial and error.

## Step 2 — Choose the expression type

| You need | Use | Example |
|---|---|---|
| A result locked to a specific dimension, regardless of view filters or granularity | `FIXED` | `{FIXED [Customer ID]: SUM([Revenue])}` — customer lifetime revenue |
| A result computed at a *finer* grain than the view | `INCLUDE` | `{INCLUDE [Order ID]: SUM([Qty])}` — average items per order, view is by month |
| A result computed at a *coarser* grain than the view (exclude a dimension) | `EXCLUDE` | `{EXCLUDE [Region]: SUM([Revenue])}` — national total on a region-level view |
| A ranking, running total, moving average, or percent-of-total that depends on the *current view layout* | Table calculation | `RANK(SUM([Revenue]))` with correct addressing/partitioning |

**FIXED does NOT respect dimension filters** (only context filters, data-source filters, and extract filters override it). If the metric must respect a user's filter, use `INCLUDE` or a table calculation — or promote the filter to a context filter explicitly.

## Step 3 — Construct the FIXED expression

```
{ FIXED [Dim1], [Dim2] : AGG([Measure]) }
```

- List every dimension needed to define the grain of the result.
- `AGG` must be a row-level expression wrapped in `SUM`/`MIN`/`MAX`/`AVG`/`COUNTD`.
- To use the result in another aggregate in the view, wrap it: `SUM({ FIXED ... })`.

**Worked example — customer first order date:**

```
{ FIXED [Customer ID] : MIN([Order Date]) }
```

Place this in a calculated field `[Customer First Order Date]`. The view can then be at any grain (order-level, month-level) and the field always returns the per-customer minimum.

## Step 4 — Construct the INCLUDE / EXCLUDE expression

```
{ INCLUDE [Extra Dim] : AGG([Measure]) }
{ EXCLUDE [Dim To Drop] : AGG([Measure]) }
```

INCLUDE adds a dimension to the computation; EXCLUDE removes one. Both respect dimension filters (unlike FIXED).

**Worked example — average order size at a monthly view:**

```
{ INCLUDE [Order ID] : SUM([Revenue]) }
```

This computes per-order revenue at the order-ID grain, then the view aggregates those results at the month level (the outer `AVG` in the view field becomes the average per-order revenue by month).

## Step 5 — Table calculation addressing and partitioning

Table calculations run on the query result already in the view, not on the underlying data. The two settings that matter:

| Setting | Meaning |
|---|---|
| **Addressing** (Compute Using) | The dimensions the calculation moves *across* (e.g., month-over-month: address = Date) |
| **Partitioning** | The dimensions that *reset* the calculation (e.g., each Region resets the running total) |

Never leave addressing on "Automatic" for a published workbook — it depends on field order in the view, which changes when users rearrange. Specify addressing explicitly.

## Double-counting diagnosis checklist

- [ ] Is there a JOIN that fans out rows (many-to-many)? → switch to a relationship or pre-aggregate.
- [ ] Is `SUM` applied to a pre-aggregated field? → use `ATTR` or rewrite the source.
- [ ] Is a FIXED LOD returning a value per row that gets `SUM`med again? → wrap in `MAX` or `MIN` if it's a row-level attribute, not a sum.
- [ ] Is a blend pulling in multiple matching rows from the secondary source? → blend should join on all granularity keys; consider converting to a relationship.

## Pitfalls

- Putting a FIXED LOD inside a `SUM` in the view when the FIXED already returns a total — you get total × row count.
- Using EXCLUDE when FIXED would be clearer — EXCLUDE is elegant when the dimension set is large; otherwise state the grain explicitly.
- Setting "Compute Using: Table (across)" on a multi-partition layout — the table calculation resets in unexpected places.
- Forgetting that FIXED ignores dimension filters: a FIXED customer revenue will ignore a Region quick-filter unless you promote that filter to a context filter.
