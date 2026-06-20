---
name: write-spatial-queries
description: "Write correct, index-using spatial SQL: geometry vs geography per column, GiST spatial indexes, ST_DWithin instead of ST_Distance for distance filters, KNN nearest-neighbour with the <-> operator, spatial joins (ST_Intersects/ST_Contains) with matched SRIDs, and EXPLAIN verification."
---

# Write Spatial Queries (PostGIS-leaning)

Correct first (SRID + geometry/geography), fast second (index + sargable predicate).

## The index-using patterns
```sql
-- Spatial index (do this before anything else)
CREATE INDEX idx_stores_geog ON stores USING GIST (geog);

-- Within distance: ST_DWithin uses the index; ST_Distance < d does NOT
SELECT * FROM stores
WHERE ST_DWithin(geog, ST_MakePoint(:lon, :lat)::geography, 5000);  -- 5 km

-- Nearest k (KNN): the <-> operator is index-assisted with ORDER BY ... LIMIT
SELECT id, geog <-> ST_MakePoint(:lon, :lat)::geography AS dist
FROM depots
ORDER BY geog <-> ST_MakePoint(:lon, :lat)::geography
LIMIT 3;

-- Point-in-polygon join (match SRID on both sides)
SELECT p.id, d.district
FROM pings p
JOIN districts d ON ST_Intersects(d.geom, p.geom)   -- both EPSG:4326
;
```

## Checklist
1. **SRID matched** on both sides (`ST_SRID`, `ST_Transform` the outlier).
2. **geography vs geometry:** `geography` for correct lon/lat distance over large extents; `geometry` (projected) for speed and area/length.
3. **Sargable predicate:** `ST_DWithin` / `ST_Intersects`, not a function-wrapped or `ST_Distance < d` filter.
4. **Index present and used:** `EXPLAIN (ANALYZE)` shows an index scan, not a seq scan.
5. **Validity:** geometries are `ST_IsValid` (see [`../spatial-data-quality/SKILL.md`](../spatial-data-quality/SKILL.md)).

## Anti-patterns
- `ST_Distance(a, b) < d` as a filter (full scan).
- Cross join + `ORDER BY ST_Distance` for nearest-neighbour (use `<->` + LIMIT).
- Computing `ST_Area` in EPSG:3857 (Web Mercator distorts area badly).
- A spatial join across mismatched SRIDs (silently wrong).
