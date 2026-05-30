# Pick the storage mode deliberately — Import by default, DirectQuery/Direct Lake/Composite with a reason

**Status:** Primary diagnostic — when a model is slow, over-budget on capacity, or stale, check storage mode first.

**Domain:** Power BI / semantic modeling

**Applies to:** `power-platform`

---

## Why this exists

Storage mode is the single decision that most determines a semantic model's performance, freshness, and capacity cost — and it is the hardest to change later because relationships, aggregations, and DAX assumptions get baked around it. Makers reflexively leave everything on **Import** (fast, but a point-in-time copy that must refresh) or reflexively switch a whole model to **DirectQuery** (live, but every visual fires SQL and the model inherits the source's latency). Both reflexes are wrong as blanket policies. **Direct Lake** (Fabric) gives Import-class speed over Delta tables in OneLake without a refresh copy, but only inside a Fabric capacity and with [documented fallback-to-DirectQuery rules](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview). **Composite** lets you mix per-table. Microsoft's [Semantic model modes](https://learn.microsoft.com/power-bi/connect-data/service-dataset-modes-understand) is the authoritative reference. The failure mode is silent until scale: a 10k-row report is fast on any mode; a 50M-row DirectQuery model with no aggregations falls off a cliff in production.

## How to apply

Default to **Import**. Deviate only when a named requirement forces it:

| Requirement | Mode |
|---|---|
| Sub-second interactivity, data can be hours stale, fits in memory | **Import** |
| Near-real-time data, source is the system of record, data too large to import | **DirectQuery** (set a per-table storage mode; add **aggregations**) |
| Data already lands in OneLake Delta tables, you have Fabric capacity | **Direct Lake** |
| Big fact needs live data + small dimensions need speed | **Composite** (DirectQuery fact + Import dims + aggregation table) |

In a **composite** model, set the fact to DirectQuery and dimensions to Dual so they serve both the Import-speed slicers and the DirectQuery joins:

```
-- Per-table storage mode (Model view → table → Properties → Storage mode):
--   Sales (fact)      → DirectQuery
--   Date, Product     → Dual          (acts as Import for slicers, DirectQuery for joins)
--   Sales_Agg (agg)   → Import         (pre-aggregated summary; Manage aggregations maps it to Sales)
```

**Do:**
- Start in Import; profile before switching anything to DirectQuery.
- When you must use DirectQuery, add an **aggregation table** so common queries hit a cached summary instead of the source.
- Set shared dimensions to **Dual** in composite models so they don't force a slow join.
- For Direct Lake, confirm a Fabric capacity exists and check what triggers **fallback to DirectQuery** (unsupported DAX, capacity guardrails) — fallback silently slows queries.

**Don't:**
- Flip an entire model to DirectQuery to "get live data" without measuring — every visual now round-trips to the source.
- Use DirectQuery without aggregations on a high-traffic report.
- Assume Direct Lake works outside Fabric — it requires OneLake Delta + Fabric capacity.

## Edge cases / when the rule does NOT apply

- **Real-time streaming** (push/streaming datasets) is a separate path, not one of these four modes.
- **Tiny live dashboards** over a fast SQL source may be fine on pure DirectQuery without aggregations — measure first.
- **Direct Lake fallback** behavior changes as Fabric evolves; re-verify the fallback triggers before quoting them. `[volatile — Fabric ships monthly]`

## See also

- [`bi-star-schema-not-flat-table.md`](./bi-star-schema-not-flat-table.md) — storage mode interacts with how facts vs dimensions are split
- [`bi-measures-not-calculated-columns.md`](./bi-measures-not-calculated-columns.md) — calculated columns are limited under Direct Lake
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — `## Decision Tree: Power BI — Storage mode`
- [`../skills/power-bi/SKILL.md`](../skills/power-bi/SKILL.md) — composite models, DirectQuery, Direct Lake reference
- [`../agents/power-bi-engineer.md`](../agents/power-bi-engineer.md) — owner of the storage-mode call

## Provenance

Grounded in [Semantic model modes](https://learn.microsoft.com/power-bi/connect-data/service-dataset-modes-understand), [Direct Lake overview](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview), and [composite models / aggregations guidance](https://learn.microsoft.com/power-bi/transform-model/desktop-aggregations) (retrieved 2026-05-30). Encodes the `power-bi-engineer` opinion "prefers composite models, DirectQuery where appropriate."

---

_Last reviewed: 2026-05-30 by `claude`_
