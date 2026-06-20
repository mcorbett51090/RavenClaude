# Reproject on read, store geometry once

**Status:** Absolute rule
**Domain:** CRS / data modeling
**Applies to:** `geospatial-gis-engineering`

---

## Why this exists

Keeping a separate geometry column for every CRS you display in (one for 4326, one for 3857, …) means every write has to update them all in lockstep — and the moment one update is missed, the columns disagree and the bug is invisible until a map renders wrong. Storing a single canonical SRID and reprojecting at read time (`ST_Transform`) keeps one source of truth.

## How to apply

```sql
-- Store canonical 4326; reproject for the web map at read time
SELECT id, ST_AsMVTGeom(ST_Transform(geom, 3857), :bbox) AS geom
FROM roads
WHERE ST_Intersects(geom, ST_Transform(:bbox, 4326));
```

**Do:**
- Store one canonical SRID (4326 default).
- `ST_Transform` on read for display/analysis CRSs.
- Cache/pre-render tiles if reprojection cost on read is hot.

**Don't:**
- Maintain duplicate geometry columns per CRS in application tables.

## Edge cases / when the rule does NOT apply

A read-heavy analytics table where one projected CRS dominates every query may store *in* that projected CRS — still one canonical SRID, just not 4326. The rule is "one canonical column," not "always 4326."

## See also

- [`./store-one-canonical-srid-per-column.md`](./store-one-canonical-srid-per-column.md)
- [`./never-compute-area-in-web-mercator.md`](./never-compute-area-in-web-mercator.md)

## Provenance

PostGIS `ST_Transform` / PROJ. Standard CRS-management practice. Codifies `gis-architect` / `spatial-data-engineer` discipline.

---

_Last reviewed: 2026-06-20 by `claude`_
