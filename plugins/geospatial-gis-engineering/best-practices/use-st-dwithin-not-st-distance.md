# Filter with ST_DWithin, not ST_Distance < d

**Status:** Absolute rule
**Domain:** Spatial SQL / performance
**Applies to:** `geospatial-gis-engineering`

---

## Why this exists

`ST_Distance(a, b) < d` computes a distance for every row before comparing — the GiST index can't help, so it's a full scan. `ST_DWithin(a, b, d)` is written so the planner uses the spatial index's bounding-box pre-filter, turning the same logical question into an index scan. Same answer, orders of magnitude faster.

## How to apply

```sql
-- Slow: function result compared (no index)
SELECT * FROM stores WHERE ST_Distance(geog, :pt) < 5000;     -- avoid

-- Fast: index-using distance filter
SELECT * FROM stores WHERE ST_DWithin(geog, :pt, 5000);       -- prefer
```

**Do:**
- Use `ST_DWithin` for every "within distance" filter.
- Use `ST_Distance` only to *report* a distance in the SELECT list, not to filter.
- Use the `<->` KNN operator with `ORDER BY ... LIMIT k` for nearest-neighbour.

**Don't:**
- Filter with `ST_Distance < d` or a cross-join-then-sort for nearest neighbour.

## Edge cases / when the rule does NOT apply

When you genuinely need the distance value in the output (and the row set is already small after other filters), `ST_Distance` in the projection is fine.

## See also

- [`./always-add-a-spatial-index.md`](./always-add-a-spatial-index.md)
- [`./geography-for-lonlat-distance.md`](./geography-for-lonlat-distance.md)

## Provenance

PostGIS `ST_DWithin` / KNN (`<->`) documentation. Codifies `spatial-data-engineer` discipline.

---

_Last reviewed: 2026-06-20 by `claude`_
