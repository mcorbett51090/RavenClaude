# Set table-calc addressing and partitioning explicitly — never ship the default

**Status:** Absolute rule — a table calculation left on default "Table (across)" addressing is a latent wrong-number bug that surfaces the day someone reorders pills or adds a dimension.

**Domain:** Calculations / table calculations

**Applies to:** `tableau`

---

## Why this exists

A table calculation (running total, % difference, rank, moving average, percent-of-total) computes **relative to the other marks already in the view**. Two settings control it: **partitioning** — the group the calc *resets* within — and **addressing** — the direction it *computes along*. Tableau's default ("Table (across)", "Table (down)", "Cell", "Pane…") is positional: it follows the visual layout, not your fields. So a running total that looks right today silently recomputes the wrong way the moment a colleague drags a new dimension onto Rows, reorders the pills, or pivots the view. Because the number still *renders* — it just renders wrong — these bugs ship to production unnoticed. Defining addressing/partitioning by **named field** ("Compute Using → specific dimensions") pins the behavior to your intent instead of to the pixel layout.

## How to apply

After creating any table calc, open **Compute Using** (or **Edit Table Calculation**) and choose **Specific Dimensions**, then check exactly the fields that form the *addressing*; everything unchecked becomes the *partition*.

```
// Running total of Sales BY MONTH, restarting each Year.
// Calc: RUNNING_SUM(SUM([Sales]))
// Addressing (compute along): [Month of Order Date]   <- the calc walks across months
// Partitioning (reset within): [Year of Order Date]    <- restarts every year

// Rank of Sub-Category WITHIN each Region (not across the whole table).
// Calc: RANK(SUM([Sales]))
// Addressing: [Sub-Category]      Partition: [Region]

// Percent of total within each Category column.
// Calc: SUM([Sales]) / TOTAL(SUM([Sales]))
// Addressing: [Sub-Category]      Partition: [Category]
```

**Do:**
- Always set **Compute Using → Specific Dimensions** and name the addressing fields; never leave a shipped calc on Table/Pane/Cell.
- State the partition and addressing in plain language before you build ("resets each Region, walks across Sub-Category").
- Use `LOOKUP`, `WINDOW_SUM`, `INDEX`, `FIRST`/`LAST` knowing they all honor the *same* addressing you set.

**Don't:**
- Trust "Table (across)" because it happens to look right in the current layout.
- Mix a table calc and an LOD to fake addressing when one explicit table calc is clearer.
- Forget that **sorting by a table calc**, filtering, and nested table calcs all depend on the addressing being pinned.

## Edge cases / when the rule does NOT apply

A single-row or single-column view where only one addressing is even possible is technically unambiguous — but set it explicitly anyway, because the view rarely stays single-axis. When the answer is *absolute* to a grain (per-customer total) rather than *relative to marks*, that's an **LOD**, not a table calc — see the LOD doc. Quick table calcs (the right-click shortcuts) are fine for exploration but should be opened and pinned to specific dimensions before the workbook is shared.

## See also

- [`./calc-lod-for-grain-mismatch.md`](./calc-lod-for-grain-mismatch.md) — when the answer is grain-absolute, use an LOD, not a table calc
- [`./calc-aggregate-vs-row-level.md`](./calc-aggregate-vs-row-level.md) — the aggregation a table calc sits on top of
- [`../knowledge/viz-calc-decision-trees.md`](../knowledge/viz-calc-decision-trees.md) — the LOD-vs-table-calc-vs-aggregate tree
- [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) — owns table-calc addressing discipline
- Tableau Help: "Transform Values with Table Calculations" / "The Basics of Addressing and Partitioning" `[verify-at-build]`

## Provenance

Codifies house opinion #4 reasoning and the second anti-pattern from [`../CLAUDE.md`](../CLAUDE.md) ("a table calc whose addressing/partitioning is left to default and silently wrong"). Addressing/partitioning semantics are documented Tableau behavior; exact menu wording re-verify against current Tableau Help `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
