# A data blend is a last resort — relate or join first, blend only across unrelatable sources

**Status:** Pattern — blending is the connection method of last resort; a relationship or join is almost always the correct first choice.

**Domain:** Data modeling

**Applies to:** `tableau`

---

## Why this exists

A **data blend** is not a join — it is a *left-aggregate-then-merge* performed at the level of the linking dimension, after each source is queried separately. That mechanism is the source of three recurring surprises: (1) the **secondary source is aggregated to the primary's grain**, so its measures arrive pre-aggregated and you lose row-level detail; (2) only the **primary's dimensions filter freely** — filtering on a secondary dimension is awkward or impossible; and (3) `ATTR()` returns `*` whenever the secondary has multiple values per link, silently signalling a grain mismatch many users misread as a bug. Since relationships (Tableau 2020.2) let tables of *different grain* in the *same source* coexist correctly, a blend is only justified when the data genuinely **cannot be related or joined** — typically two different published data sources or two different databases with no federated path. Reaching for a blend when a relationship would work trades correctness and speed for a fragile, hard-to-filter model.

## How to apply

Walk the ladder; blend only when both rungs above it are impossible.

```
1. RELATIONSHIP   — same data source, tables of any grain, shared key      ← default
2. PHYSICAL JOIN  — same database, same grain, want one fused table        ← with a reason
3. DATA BLEND     — different sources/databases, no federated path,        ← last resort
                    a shared linking dimension exists, secondary only
                    needs to contribute an aggregated measure
```

```
LEGITIMATE BLEND example:
  Primary   = Sales extract (Snowflake)          grain: one row per order line
  Secondary = Targets workbook (Excel upload)    grain: one row per region per month
  Link on [Region] + [Month]; show SUM(Sales) vs AVG(Target).
  Why a blend: the two live in different sources with no federation; Targets only needs to
  contribute an aggregated measure at the region/month grain the viz already uses.

BLEND THAT SHOULD HAVE BEEN A RELATIONSHIP:
  Primary = Orders, Secondary = Customers, both in the same warehouse, joined on Customer ID.
  → relate them in one data source instead; the blend just makes Customer dimensions un-filterable.
```

**Do:**
- Confirm the two datasets truly cannot be related/joined (different sources, no federation) before blending.
- Make the source whose **grain and dimensions you must filter** the *primary*.
- Keep the secondary contributing only an **aggregated measure** at the primary's grain.
- Verify the link dimension is present and identically valued on both sides.

**Don't:**
- Blend two tables that live in the same source — relate them.
- Expect to filter on a secondary dimension, drill into secondary row detail, or get a non-`*` `ATTR()` when the secondary is finer-grained than the link.
- Use a blend to "join" — a blend cannot widen the primary to the secondary's grain.

## Edge cases / when the rule does NOT apply

- **Cross-database federation available** — if your environment supports a cross-database join/relationship, prefer it; the blend's filtering and grain limitations disappear.
- **Secondary genuinely is at (or coarser than) the link grain** — e.g. one target per region/month — is the *ideal* blend case; this is where blends shine.
- **Scaffold / date-spine blends** — blending a continuous date scaffold against sparse data to densify is a recognized legitimate technique.
- **Quick throwaway comparison** during exploration — a blend is fine to eyeball a number; productionize it as a related model.

## See also

- [`./data-relationships-before-joins.md`](./data-relationships-before-joins.md) — rung 1 and 2 of the ladder
- [`./data-extract-vs-live-by-freshness.md`](./data-extract-vs-live-by-freshness.md) — the connection mode under each source
- [`../knowledge/data-performance-decision-trees.md`](../knowledge/data-performance-decision-trees.md) — `## Decision Tree: Connection model — relationship vs join vs blend`
- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — the agent that owns this rule
- Tableau Help, "Blend your data" and "Troubleshoot data blending" `[verify-at-build]`

## Provenance

Codifies constitution house opinion #2 and anti-pattern "A data blend used where a relationship would have been correct (and faster)." The left-aggregate merge semantics and `ATTR() → *` behavior are long-standing Tableau blend mechanics; federation availability is environment/version-specific — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
