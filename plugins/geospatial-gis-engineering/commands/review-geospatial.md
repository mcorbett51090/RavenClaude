---
description: "Review a geospatial design or query for CRS mismatches, missing spatial indexes, geometry/geography misuse, invalid geometry, and tiling gaps."
argument-hint: "[schema / query / map setup to review]"
---

You are running `/geospatial-gis-engineering:review-geospatial`. Use `spatial-data-engineer` (+ `gis-architect` for architecture-level findings).

## Steps
1. Check SRIDs match on every spatial predicate; geometry vs geography is correct.
2. Confirm a GiST index exists and the predicate is sargable (ST_DWithin not ST_Distance); verify with EXPLAIN.
3. Check geometry validity and (for web) GeoJSON [lon, lat] + tiling for large layers.
4. Report findings by severity + fixes, with the Structured Output block.
