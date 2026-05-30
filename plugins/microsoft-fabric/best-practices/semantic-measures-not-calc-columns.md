# Aggregate with measures, not calculated columns — push the math to gold or to DAX measures

**Status:** Pattern — explicit DAX measures (and gold-side precomputation) are the strong default; calculated columns for aggregatable values are an anti-pattern that bloats the model and, on Direct Lake, isn't even available.

**Domain:** Semantic modeling / DAX surface

**Applies to:** `microsoft-fabric`

---

## Why this exists

A **calculated column** is materialized into VertiPaq and stored for every row — it inflates model memory, can't respond to filter context, and recomputes on refresh. A **measure** is evaluated at query time in the current filter context and stores nothing. For aggregatable business logic (sums, ratios, running totals) the measure is almost always right. On **Direct Lake on OneLake specifically**, this isn't just a preference: Direct Lake reads columns straight from Delta, so the durable home for *derived columns* is the **gold Delta table** (computed in Spark/T-SQL), not a model-side calculated column — pushing row-level derivation into gold keeps the model lean and keeps Direct Lake able to load it. The division of labor: row-level derivations → gold; aggregations and context-dependent logic → DAX measures; calculated columns → rare exception.

## How to apply

Route each kind of logic to its right home.

```text
Row-level derived value (e.g. line_total = qty * price)   → compute in GOLD (Spark/T-SQL), store the column.
Aggregation / ratio / time intelligence                   → DAX MEASURE (no storage, filter-context aware).
A true low-cardinality grouping key you must materialize   → calculated column ONLY if it can't live in gold.
```

```dax
-- Measure: evaluated in filter context, stores nothing.
Total Sales = SUMX ( fact_sales, fact_sales[qty] * RELATED ( dim_product[price] ) )
-- Better still: precompute line_total in gold, then:  Total Sales = SUM ( fact_sales[line_total] )
```

**Do:**
- Write **measures** for anything aggregatable or filter-context dependent.
- Precompute **row-level derived columns in gold** so Direct Lake just reads them.
- Keep the model's column count and cardinality disciplined — it's a guardrail input.

**Don't:**
- Add calculated columns for values a measure or a gold column should produce — they bloat memory and refresh.
- Assume calculated columns behave the same on Direct Lake as Import; prefer gold-side derivation for Direct Lake models.

## Edge cases / when the rule does NOT apply

- **A grouping/binning key** that must exist as a physical column for slicing and genuinely can't be precomputed in gold may justify a calculated column — keep it low-cardinality.
- **DAX measure *authoring* depth** (complex measure libraries, calculation groups) escalates to **`power-platform/power-bi-engineer`** — this rule is about *where the math lives*, not advanced DAX craft.
- **Import models** tolerate calculated columns better than Direct Lake — but the memory/refresh cost argument still favors measures.

## See also

- [`semantic-star-schema-over-flat.md`](./semantic-star-schema-over-flat.md) — the star the measures sit on
- [`shape-gold-for-direct-lake.md`](./shape-gold-for-direct-lake.md) — gold is where row-level derivations belong for Direct Lake
- [`../knowledge/direct-lake-and-semantic-models.md`](../knowledge/direct-lake-and-semantic-models.md) — "data prep moves to OneLake, not to a model refresh"
- [`../agents/fabric-semantic-model-engineer.md`](../agents/fabric-semantic-model-engineer.md) — DAX measure authoring escalates to `power-platform/power-bi-engineer`

## Provenance

Grounded in [Direct Lake overview](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview) ("Direct Lake moves data preparation to OneLake … using the full breadth of Fabric technologies for data prep, including Spark jobs, T-SQL DML, dataflows, pipelines") and [Understand Direct Lake query performance](https://learn.microsoft.com/fabric/fundamentals/direct-lake-understand-storage) (disciplined cardinality / column count) — Microsoft Learn, retrieved 2026-05-30. The DAX-measure-authoring seam routes to `power-platform/power-bi-engineer` per [`../CLAUDE.md`](../CLAUDE.md) §10.

---

_Last reviewed: 2026-05-30 by `claude`_
