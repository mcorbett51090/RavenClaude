# Model a star schema, not one flat wide table

**Status:** Absolute rule — a flat-table Power BI model is a defect, not a style choice.

**Domain:** Power BI / semantic modeling

**Applies to:** `power-platform`

---

## Why this exists

The VertiPaq engine that powers Import and Direct Lake storage is built to compress and join a **star schema** — narrow fact tables surrounded by dimension tables on single-column relationships. A single flat, wide table (the shape you get from a naive Excel/CSV import) defeats VertiPaq's columnar compression: high-cardinality descriptive columns repeat on every fact row, model size balloons, relationships you'd otherwise get for free become impossible, and time intelligence has no clean date dimension to anchor to. Microsoft's own guidance ([Understand star schema and the importance for Power BI](https://learn.microsoft.com/power-bi/guidance/star-schema)) makes star schema the foundational modeling pattern. The failure mode is silent: the report works on 10k rows and falls off a performance cliff at 10M.

## How to apply

Split the flat table into **facts** (the events/measures — sales, transactions, log entries) and **dimensions** (the descriptive context — product, customer, date, geography). One relationship per dimension into the fact, single-direction filter, single key column.

Build an explicit **Date** dimension and mark it as a date table so time intelligence works:

```dax
-- A dedicated, marked Date dimension table (DAX calculated table):
Date =
VAR _min = MIN ( Sales[OrderDate] )
VAR _max = MAX ( Sales[OrderDate] )
RETURN
ADDCOLUMNS (
    CALENDAR ( DATE ( YEAR ( _min ), 1, 1 ), DATE ( YEAR ( _max ), 12, 31 ) ),
    "Year",        YEAR ( [Date] ),
    "Month No",    MONTH ( [Date] ),
    "Month",       FORMAT ( [Date], "MMM" ),
    "Year-Month",  FORMAT ( [Date], "YYYY-MM" )
)
-- Then: Table tools → Mark as date table → Date column = [Date].
```

**Do:**
- One fact table per business process (Sales, Inventory, Web Sessions); conform shared dimensions across them.
- Put descriptive columns on the dimension, keep the fact narrow (keys + numeric measures + degenerate dims only).
- Single-direction relationships from dimension → fact. Reach for bidirectional only with a written reason.
- Mark the Date table so `TOTALYTD`, `SAMEPERIODLASTYEAR`, etc. resolve correctly.

**Don't:**
- Ship a single wide table with product name, customer address, and sales amount all on every row.
- Snowflake a dimension into five sub-tables when one denormalized dimension would compress better.
- Rely on the auto-generated date hierarchy in place of a real Date dimension — it bloats the model with one hidden date table per date column.

## Edge cases / when the rule does NOT apply

- **Tiny, single-purpose models** (a one-page personal report over a few hundred rows) don't pay the cliff cost — a flat table is fine and faster to build.
- **Aggregation tables** over a DirectQuery fact are intentionally denormalized summaries; they're a performance pattern, not a violation.
- **Snowflaking** is acceptable when a sub-dimension is genuinely reused across multiple dimensions and the cardinality is low.

## See also

- [`bi-measures-not-calculated-columns.md`](./bi-measures-not-calculated-columns.md) — the measure-side discipline that pairs with a clean star schema
- [`bi-storage-mode-selection.md`](./bi-storage-mode-selection.md) — storage mode interacts with how you split facts vs dimensions
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — `## Decision Tree: Power BI — Storage mode`
- [`../skills/power-bi/SKILL.md`](../skills/power-bi/SKILL.md) and [`resources/dax-patterns-and-performance.md`](../skills/power-bi/resources/dax-patterns-and-performance.md) — the deeper modeling playbook
- [`../agents/power-bi-engineer.md`](../agents/power-bi-engineer.md) — owner of semantic-model design

## Provenance

Grounded in [Understand star schema and the importance for Power BI](https://learn.microsoft.com/power-bi/guidance/star-schema) and [Semantic model modes](https://learn.microsoft.com/power-bi/connect-data/service-dataset-modes-understand) (retrieved 2026-05-30). Extends the `power-bi-engineer` opinion "suspicious of giant monolithic models" and CLAUDE.md §4 anti-pattern "giant single semantic model."

---

_Last reviewed: 2026-05-30 by `claude`_
