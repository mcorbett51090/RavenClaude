# Index every spatial column with GiST before optimizing anything else

**Status:** Absolute rule
**Domain:** Spatial query performance
**Applies to:** `geospatial-engineering`

---

## Why this exists

A spatial predicate — `ST_Intersects`, `ST_DWithin`, `ST_Contains`, a `<->` nearest-neighbor — over an **unindexed** geometry column forces PostgreSQL to compute the relationship against *every row*: a sequential scan that is fine on 1,000 rows and a tarpit on 1,000,000. The **GiST** (Generalized Search Tree) index stores each geometry's bounding box in an R-tree-like structure, so the planner can discard the vast majority of rows with a cheap bounding-box test (`&&`) before running the exact, expensive predicate on the survivors. The index is **not an optimization you reach for when things get slow — it is part of a correct spatial table**, because the difference is milliseconds vs minutes and shows up the moment real data lands.

The index only helps if the query lets it. Index-aware operators (`&&`, `ST_DWithin`, the `<->` KNN operator) use it; `ST_Distance(a, b) < d` does **not** — it computes a distance per row and scans. Writing the index-aware form is half the rule.

## How to apply

Create a GiST index on every geometry/geography column, and confirm the plan uses it:

```sql
CREATE INDEX my_table_geom_gix ON my_table USING GIST (geom);

-- DO: index-aware proximity (uses the index)
SELECT * FROM my_table WHERE ST_DWithin(geom, :pt, 1000);
-- DON'T: this scans — distance computed per row
-- SELECT * FROM my_table WHERE ST_Distance(geom, :pt) < 1000;

EXPLAIN (ANALYZE) SELECT ...;   -- confirm an Index Scan on …_geom_gix, not a Seq Scan
```

**Do:**
- Add `USING GIST (geom)` to every spatial column; consider SP-GiST for point-only clustered data.
- Use index-aware operators: `ST_DWithin` (not `ST_Distance < d`), `&&`, the `<->` KNN operator for nearest-neighbor.
- Verify with `EXPLAIN (ANALYZE)` that you get an Index Scan, then `ANALYZE` the table so stats are fresh.

**Don't:**
- Ship a spatial table with no spatial index.
- Filter proximity with `ST_Distance(...) < d` — it defeats the index.
- Assume the index exists because the column does — indexes are separate objects.

## Edge cases / when the rule does NOT apply

- **Tiny lookup tables** (a handful of rows) won't benefit and the planner may correctly ignore the index — harmless, still cheap to create.
- **Write-heavy, rarely-queried staging tables** may defer index creation until load completes (build the index *after* the bulk load for speed), but the finished table still carries it.

## See also

- [`../knowledge/projection-decision-tree.md`](../knowledge/projection-decision-tree.md) — the CRS the indexed geometry lives in.
- [`./always-store-an-srid.md`](./always-store-an-srid.md) — the companion correctness rule.
- [`../skills/write-spatial-query/SKILL.md`](../skills/write-spatial-query/SKILL.md) — index-aware query patterns (KNN, `ST_DWithin`, spatial joins).

## Provenance

Codifies the `geospatial-data-engineer` house opinion "an unindexed spatial table is a tarpit at scale; the GiST index is not optional" ([`../CLAUDE.md`](../CLAUDE.md)). The advisory hook [`../hooks/flag-geo-smells.sh`](../hooks/flag-geo-smells.sh) flags an `ST_Distance(...) <` proximity smell. Grounded in PostGIS documentation (spatial indexing with GiST; index-only operators), retrieved 2026-06-17.

---

_Last reviewed: 2026-06-17 by `claude`_
