# Model with relationships first; drop to a physical join only with a reason

**Status:** Pattern — relationships (the logical layer) are the strong default for any multi-table model; a physical join is the deviation you justify in writing.

**Domain:** Data modeling

**Applies to:** `tableau`

---

## Why this exists

Most "wrong total" bugs in Tableau are grain bugs introduced by a physical join, not calc bugs. A physical inner/left join fuses two tables into one flat table at the **finer** grain, which **fans out** the coarser side: join `Orders` (one row per order) to `OrderLines` (one row per line) and every order-level measure now repeats once per line, so `SUM([Order Total])` double-, triple-, n-counts. A **relationship** (the "noodle" in the logical layer, since Tableau 2020.2) does not pre-join — it keeps each table at its **native grain** and lets Tableau generate the correct join (type and direction) per viz from the fields actually in play. You get the right number for an order-level measure and a line-level measure in the *same* workbook without two data sources. Reaching for a physical join first is how you inherit the fan-out you then spend an afternoon debugging with `COUNTD` and `MIN`/`ATTR` workarounds.

## How to apply

Build the model in the logical layer; only double-click into a logical table to add a physical join when you have a named reason.

```
Logical layer (default — relationships):
  [Orders] •———• [Customers]      relate on Customer ID
  [Orders] •———• [OrderLines]     relate on Order ID
    → SUM([Order Total]) is correct (orders kept at order grain)
    → SUM([Line Quantity]) is correct (lines kept at line grain)
    → no fan-out, join chosen per-viz from fields used

Physical join (deviation — only with a reason):
  [Orders] INNER JOIN [OrderStatusLookup] ON Orders.StatusID = Lookup.StatusID
    → justified: same grain (one status per order), row-level enrichment,
      same database, you genuinely want one fused table
```

Set the relationship's **performance options** when you know them: cardinality (Many-to-one / One-to-one) and **referential integrity** ("All records match" / "Some records match"). Correct settings let Tableau drop unnecessary joins from the query (faster); wrong settings produce wrong results, so only assert "All records match" when it is truly enforced upstream.

**Do:**
- State each table's grain ("one row per …") before relating anything.
- Use relationships for tables of *different* grain that share a key.
- Use a physical join only for a same-grain, same-database, row-level enrichment.
- Set cardinality and referential integrity from what the source actually guarantees.

**Don't:**
- Physically join a header table to its line table — that is the canonical fan-out.
- Assert "All records match" to chase speed when the source allows orphans.
- Reach for `COUNTD`/`MIN`/LOD gymnastics to undo a fan-out you created — remove the join instead.

## Edge cases / when the rule does NOT apply

- **Same-grain row-level enrichment** — a one-to-one lookup (one status row per order) is a legitimate physical join; a relationship would also work but adds nothing.
- **A single flat table** (one CSV, one wide view) — there is nothing to relate; model it as one logical table.
- **Calculations that must reference fields across the join in a row-level expression** — a row-level calc spanning two physical tables needs them in one logical table (joined or related is fine as long as grain is preserved); a measure-level calc does not.
- **Pre-Tableau-2020.2 workbooks** — relationships did not exist; those use physical joins and data source filters by necessity `[verify-at-build]`.

## See also

- [`./data-blend-is-a-last-resort.md`](./data-blend-is-a-last-resort.md) — when you can't relate at all
- [`./data-extract-vs-live-by-freshness.md`](./data-extract-vs-live-by-freshness.md) — the connection mode under the model
- [`../knowledge/data-performance-decision-trees.md`](../knowledge/data-performance-decision-trees.md) — `## Decision Tree: Connection model — relationship vs join vs blend`
- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — the agent that owns this rule
- Tableau Help, "Relationships vs joins" and "Differences between relationships and joins" `[verify-at-build]`

## Provenance

Codifies the constitution house opinion #2 ("Relationships by default; joins/blends with a reason") and #1 ("Model granularity before you calculate"). The fan-out / double-counting mechanism is the canonical Tableau modeling failure mode (header-to-line join); relationships were introduced in Tableau 2020.2 as the logical-layer default — re-verify version-gated details against current Tableau Help before quoting to a client.

---

_Last reviewed: 2026-05-30 by `claude`_
