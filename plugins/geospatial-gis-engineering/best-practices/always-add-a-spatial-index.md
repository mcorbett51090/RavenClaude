# Always add (and verify) a spatial index

**Status:** Absolute rule
**Domain:** Spatial SQL / performance
**Applies to:** `geospatial-gis-engineering`

---

## Why this exists

A spatial predicate without an index is a full table scan that evaluates an expensive geometry function on every row. A GiST index on the geometry/geography column lets PostGIS prune with a bounding-box pre-filter first. Most "PostGIS is slow" reports are a missing index or a predicate that defeats it.

## How to apply

```sql
CREATE INDEX idx_roads_geom ON roads USING GIST (geom);

-- Verify the index is actually used
EXPLAIN (ANALYZE) SELECT * FROM roads
WHERE ST_DWithin(geom, :pt, 1000);   -- expect an Index Scan, not Seq Scan
```

**Do:**
- GiST-index every column you filter or join spatially.
- Confirm with `EXPLAIN (ANALYZE)` that the plan uses it.
- `ANALYZE` after bulk loads so the planner has stats.

**Don't:**
- Wrap the indexed column in a function in the predicate (defeats the index).
- Assume the index exists — check.

## Edge cases / when the rule does NOT apply

Tiny lookup tables (a handful of rows) don't need an index; the planner will seq-scan them anyway.

## See also

- [`./use-st-dwithin-not-st-distance.md`](./use-st-dwithin-not-st-distance.md)
- [`../skills/write-spatial-queries/SKILL.md`](../skills/write-spatial-queries/SKILL.md)

## Provenance

PostGIS GiST index documentation. Codifies `spatial-data-engineer` house opinion ("the index is the query plan").

---

_Last reviewed: 2026-06-20 by `claude`_
