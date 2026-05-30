# Reach for an LOD when the answer's grain differs from the viz's grain

**Status:** Pattern — when a number must be computed at a level of detail other than the viz, use an LOD expression; deviate only with a written reason.

**Domain:** Calculations / level of detail

**Applies to:** `tableau`

---

## Why this exists

A view has a level of detail set by the dimensions on Rows/Columns/marks. Most aggregates compute *at* that level — but a whole class of questions needs a number at a **different** grain: "customer's first order date" (per-customer, regardless of the month on the axis), "each order's share of its region's total," "average sales *per customer*" shown by region. Building these by hand — duplicating rows, blending, or faking it with a table calc — is fragile and double-counts. Level-of-detail (LOD) expressions compute a value at a grain you name explicitly, independent of the viz, which is why "wrong total" and "double-counting" bugs so often resolve to "should have been a FIXED LOD." This is house opinion #1 in action.

## How to apply

Pick the keyword by how the calc's grain relates to the viz's:

- **`FIXED`** — compute at the named dimensions only, **ignoring** the viz level of detail.
- **`INCLUDE`** — compute at the viz dimensions **plus** the named ones (finer), then re-aggregate up.
- **`EXCLUDE`** — compute at the viz dimensions **minus** the named ones (coarser).

```
// Per-customer total, fixed regardless of what's on the view.
// Use it to bucket customers, or to get "first order date" stably.
[Customer Lifetime Sales]  =  { FIXED [Customer ID] : SUM([Sales]) }
[First Order Date]         =  { FIXED [Customer ID] : MIN([Order Date]) }

// Average order size PER CUSTOMER, even though the view is by Region.
// INCLUDE pushes detail down to customer, then AVG re-aggregates to Region.
[Avg Sales per Customer]   =  AVG({ INCLUDE [Customer ID] : SUM([Sales]) })

// Each row's share of its category total (EXCLUDE removes the sub-dimension).
[% of Category]            =  SUM([Sales]) / SUM({ EXCLUDE [Sub-Category] : SUM([Sales]) })
```

**Order of operations matters:** FIXED is computed **before** dimension (quick) filters but **after** context filters; INCLUDE/EXCLUDE are computed **after** dimension filters. Promote a filter to a **context filter** when you need FIXED to respect it.

**Do:**
- Use `FIXED` when the grain is absolute (per-customer, per-order) and must not move with the view.
- Use `INCLUDE`/`EXCLUDE` when the grain is *relative* to whatever dimensions are currently on the view.
- Promote filters to context filters when a FIXED LOD must honor them.

**Don't:**
- Fake an LOD with a self-blend or a table calc when a one-line `FIXED` is correct and faster.
- Forget that FIXED ignores dimension filters — a "why didn't my filter change the number" bug is almost always this.

## Edge cases / when the rule does NOT apply

If the answer *is* relative to other marks already drawn (running total, rank, % difference from prior), that's a **table calc**, not an LOD — see the addressing doc. If the number genuinely lives at the viz grain, a plain aggregate is simpler; don't reach for an LOD reflexively. LODs on extracts vs. live connections can differ in performance and (rarely) in null/blend behavior — seam to `tableau-data-architect` for the data-side implications.

## See also

- [`./calc-table-calc-addressing-explicit.md`](./calc-table-calc-addressing-explicit.md) — when the answer is relative to marks, not grain
- [`./calc-aggregate-vs-row-level.md`](./calc-aggregate-vs-row-level.md) — the layer underneath LODs
- [`../knowledge/viz-calc-decision-trees.md`](../knowledge/viz-calc-decision-trees.md) — the FIXED-vs-INCLUDE-vs-EXCLUDE tree and the order-of-operations note
- [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) — owns LOD selection
- Tableau Help: "Create Level of Detail Expressions" + "Order of Operations" `[verify-at-build]`

## Provenance

Codifies house opinion #1 and the first anti-pattern from [`../CLAUDE.md`](../CLAUDE.md). FIXED/INCLUDE/EXCLUDE semantics and the filter order-of-operations are documented Tableau behavior; exact ordering re-verify against current Tableau Help `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
