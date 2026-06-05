# Use custom SQL in live connections only when the logical layer cannot express it

**Status:** Pattern
**Domain:** Performance / data modeling
**Applies to:** `tableau`

---

## Why this exists

A custom SQL connection in Tableau wraps the entire workbook's queries inside a
subquery: every filter, every calculated field, every LOD expression executes
against `SELECT * FROM (your custom sql) AS t WHERE ...`. The database cannot
push filters or optimizations through the subquery boundary in most cases, which
turns every Tableau query into a full custom-SQL scan followed by a filter step.
Teams that use custom SQL "for flexibility" on live connections turn a 2-second
dashboard into a 30-second one. The logical layer (relationships, joins, native
table connections) allows the database's query planner to see Tableau's actual
filter predicates and push them down.

## How to apply

**Use custom SQL only when the logical layer genuinely cannot express the need:**
- A query requiring `PIVOT`, `LATERAL`, `CROSS JOIN UNNEST`, or other
  non-standard SQL that Tableau's join/relationship interface can't model.
- A stored procedure or function call required by the source system.
- A CTEs-based query that semantically cannot be broken into separate tables.

**For everything else, use the logical layer:**
- Multi-table models → relationships.
- Row-level filtering → data source filters on native table connections.
- Derived columns → calculated fields in Tableau or upstream views.

**When custom SQL is unavoidable:**
1. Materialise it as a database view and connect Tableau to the view, not to
   raw custom SQL — the view gives the planner more optimisation surface.
2. Add the minimum necessary `WHERE` clause to limit the rows the custom SQL
   returns at all.
3. Switch to an extract if the query cannot be optimised further in live mode.

**Do:**
- Document why the logical layer cannot satisfy the requirement before adding
  custom SQL.
- Prefer a database view over raw custom SQL in the connection.
- Benchmark the query plan with and without the custom SQL wrapper to confirm
  the performance impact.

**Don't:**
- Default to custom SQL because it "feels more like SQL" or is familiar from
  another BI tool.
- Use custom SQL on a live connection to a transactional database without
  confirming the query plan is acceptable.
- Put business logic in custom SQL that should live in a calculated field
  (it hides it from other workbook consumers).

## Edge cases / when the rule does NOT apply

- Extracts: the extract is built once; the query plan impact of custom SQL
  at extract-build time is acceptable; the workbook queries run against the
  `.hyper` file, not the custom SQL.

## See also

- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — owns data modeling and query design
- [`./data-relationships-before-joins.md`](./data-relationships-before-joins.md) — the logical layer alternative to custom SQL
- [`./perf-filter-at-the-source.md`](./perf-filter-at-the-source.md) — filter pushdown is what custom SQL defeats

## Provenance

Codifies the custom SQL performance concern from Tableau performance
documentation and the house opinion "performance is designed, not tuned later"
from `CLAUDE.md` §3. Standard Tableau performance engineering practice.
`[verify-at-build]` for specific database query-plan behaviour.

---

_Last reviewed: 2026-06-05 by `claude`_
