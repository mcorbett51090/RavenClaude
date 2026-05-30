# Know whether a calc is row-level or aggregate before you write it

**Status:** Absolute rule — mixing a row-level expression with an aggregate one in the same calc is a build error, and aggregating the wrong layer is a silent wrong-number bug.

**Domain:** Calculations / level of detail

**Applies to:** `tableau`

---

## Why this exists

Tableau evaluates every calculation at one of two layers: **row-level** (computed per row of the underlying data, before any grouping) or **aggregate** (computed across the rows that fall under a mark, after grouping). Get the layer wrong and the number is quietly wrong — `SUM([Price]) / SUM([Qty])` (a weighted average) is not the same as `AVG([Price]/[Qty])` (an average of per-row ratios), and the two diverge whenever quantities differ. Tableau also forbids mixing the layers in one expression (`[Price] - SUM([Cost])` errors with "Cannot mix aggregate and non-aggregate arguments"), which is the platform forcing you to decide on purpose. This is the foundation under house opinion #1 — model granularity before you calculate.

## How to apply

Decide what the math needs *per row* versus *per mark*, then keep each calc on one layer.

```
// Row-level: a per-transaction margin ratio, computed before grouping.
// Lives at the data's grain; can be aggregated later.
[Line Margin %]  =  ([Sales] - [Cost]) / [Sales]

// Aggregate: the blended margin across all rows under the mark.
// This is the one that is correct for a total or subtotal.
[Margin %]       =  (SUM([Sales]) - SUM([Cost])) / SUM([Sales])

// WRONG for a total: AVG of a row-level ratio ignores transaction size,
// so a $1 sale and a $1M sale count equally.
[Avg Line Margin]=  AVG(([Sales] - [Cost]) / [Sales])   // rarely what you want
```

**Do:**
- Name the grain of the source table and the level of detail of the mark before choosing the layer.
- Use **aggregate-of-aggregates** (`SUM(...)/SUM(...)`) for any ratio that must be correct at a subtotal/total.
- Keep a calc entirely row-level *or* entirely aggregate; wrap the row-level part in an explicit aggregation if you need to combine.

**Don't:**
- Average a ratio (`AVG([a]/[b])`) when you mean a weighted ratio (`SUM([a])/SUM([b])`).
- Mix layers in one expression and "fix" the error by sprinkling `ATTR()` / `MIN()` without understanding why.
- Assume a row-level calc and its aggregate give the same total — they only agree when the denominator is constant.

## Edge cases / when the rule does NOT apply

When the data is already at the grain of the viz (one row per mark), row-level and aggregate forms coincide — but write the aggregate form anyway so the calc stays correct if the grain later changes. A genuinely per-row metric that you *want* averaged unweighted (e.g., "mean satisfaction score per response") is a correct use of `AVG` of a row-level value — the rule is to choose it deliberately, not by accident.

## See also

- [`./calc-lod-for-grain-mismatch.md`](./calc-lod-for-grain-mismatch.md) — when the right grain differs from the viz grain, reach for an LOD
- [`../knowledge/viz-calc-decision-trees.md`](../knowledge/viz-calc-decision-trees.md) — the LOD-vs-table-calc-vs-aggregate tree
- [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) — owns calc-layer discipline
- Tableau Help: "Understanding Calculation Types" / "Aggregate Functions" `[verify-at-build]`

## Provenance

Codifies house opinion #1 from [`../CLAUDE.md`](../CLAUDE.md) and the first anti-pattern (a calculated field where a fixed grain was needed). The aggregate/row-level distinction is documented Tableau calculation behavior; the "Cannot mix aggregate and non-aggregate arguments" error is the platform enforcing it.

---

_Last reviewed: 2026-05-30 by `claude`_
