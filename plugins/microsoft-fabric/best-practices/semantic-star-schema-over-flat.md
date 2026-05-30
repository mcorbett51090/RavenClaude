# Model a star schema, not one wide flat table — VertiPaq and DAX both reward it

**Status:** Pattern — a star schema (conformed dimensions + fact tables) is the strong default for any Direct Lake / Import semantic model; a single wide flat gold table is an anti-pattern outside narrow exceptions.

**Domain:** Semantic modeling / dimensional design

**Applies to:** `microsoft-fabric`

---

## Why this exists

The instinct after building a clean gold layer is to flatten everything into one wide table "so the report is simple." It backfires on two fronts. **Compression:** VertiPaq compresses a star better — a denormalized wide table repeats high-cardinality dimension attributes on every fact row, inflating dictionaries and memory (which pushes you toward the per-SKU guardrails, see [`directlake-stay-under-guardrails.md`](./directlake-stay-under-guardrails.md)). **DAX:** filter context, `USERELATIONSHIP`, time intelligence, and slicers all assume a star; on a flat table you re-implement relationships in measure logic and lose the engine's join-index optimization. Direct Lake builds join indexes from declared relationships at query time — a star gives it something to optimize; a flat table gives it nothing. The star is the shape the whole stack is tuned for.

## How to apply

Shape gold as facts + conformed dimensions, declare the relationships, and keep dimensions narrow.

```text
gold.fact_sales        (grain = one row per order line; FK columns only + measures)
gold.dim_date          (conformed; marked as the date table)
gold.dim_customer      (one row per customer; SCD as needed)
gold.dim_product
   fact_sales[customer_key]  →  dim_customer[customer_key]   (single, bidirectional only if justified)
```

- **One fact per business process** at a declared grain; **conformed dimensions** shared across facts.
- **Single-direction relationships** by default; turn on bidirectional only for a specific, reasoned need (it costs perf and can create ambiguity).
- **Mark the date dimension** and build time intelligence on it rather than on a date column buried in the fact.
- **Push the shaping into gold** (the lakehouse-engineer seam) — the model declares relationships over already-conformed gold tables, it doesn't reshape at query time.

**Do:**
- Build facts + conformed dimensions; declare relationships so Direct Lake can build join indexes.
- Keep dimension tables narrow and de-duplicated; keep facts to keys + measures.
- Reserve denormalization for a deliberate, documented degenerate-dimension or report-specific case.

**Don't:**
- Ship one wide flat gold table as "the model" — you forfeit compression and DAX ergonomics.
- Default relationships to bidirectional; it's an exception, not a starting point.

## Edge cases / when the rule does NOT apply

- **A genuinely flat single-source feed** (e.g. a log/event extract with no dimensions to conform) can stay flat — there's no star to build.
- **A tiny prototype** on one table may skip dimensional modeling — say so, so the next engineer knows it was deliberate.
- **Aggregations / composite models** may add a denormalized agg table *alongside* the star for a specific perf win — that's additive, not a replacement for the star.

## See also

- [`semantic-measures-not-calc-columns.md`](./semantic-measures-not-calc-columns.md) — measures over calculated columns on the star
- [`shape-gold-for-direct-lake.md`](./shape-gold-for-direct-lake.md) — the gold shaping the star is declared over
- [`directlake-stay-under-guardrails.md`](./directlake-stay-under-guardrails.md) — flat-table inflation pushes toward the memory guardrail
- [`../agents/fabric-semantic-model-engineer.md`](../agents/fabric-semantic-model-engineer.md) · [`../agents/warehouse-engineer.md`](../agents/warehouse-engineer.md)

## Provenance

Grounded in [Power BI semantic models in Fabric](https://learn.microsoft.com/fabric/data-warehouse/semantic-models) and [Understand Direct Lake query performance](https://learn.microsoft.com/fabric/fundamentals/direct-lake-understand-storage) (join indexes built from table relationships at query time; large segments / disciplined cardinality drive performance) — Microsoft Learn, retrieved 2026-05-30. Star-schema-for-VertiPaq is long-standing Power BI guidance; the DAX measure seam routes to `power-platform/power-bi-engineer` per [`../CLAUDE.md`](../CLAUDE.md) §10.

---

_Last reviewed: 2026-05-30 by `claude`_
