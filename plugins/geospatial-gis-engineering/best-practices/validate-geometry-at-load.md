# Validate geometry at load time, not after it breaks

**Status:** Absolute rule
**Domain:** Data quality
**Applies to:** `geospatial-gis-engineering`

---

## Why this exists

Invalid geometry (self-intersecting polygons, bad ring order) passes some functions silently and crashes others (`ST_Area`, `ST_Intersection`, `ST_Union`). If it lands in the table, the failure surfaces far from the cause. Validating/repairing at the ingest boundary keeps the table trustworthy.

## How to apply

```sql
-- Constraint: reject invalid geometry
ALTER TABLE parcels ADD CONSTRAINT parcels_geom_valid CHECK (ST_IsValid(geom));

-- Or repair on the way in
INSERT INTO parcels (geom)
SELECT ST_MakeValid(ST_SetSRID(raw_geom, 4326)) FROM staging;
```

**Do:**
- Run `ST_IsValid` / `ST_MakeValid` at load.
- Check the extent matches the CRS bounds (catches swapped lon/lat).
- Set the SRID on ingest.

**Don't:**
- Trust a file's declared CRS without an extent sanity check.
- Run area/union on un-validated polygons.

## Edge cases / when the rule does NOT apply

`ST_MakeValid` can change vertex counts/topology; for legally-authoritative boundaries, repair under review rather than blindly.

## See also

- [`./geojson-is-lon-lat.md`](./geojson-is-lon-lat.md)
- [`../skills/spatial-data-quality/SKILL.md`](../skills/spatial-data-quality/SKILL.md)

## Provenance

PostGIS validity functions (`ST_IsValid`/`ST_MakeValid`); OGC Simple Features. Codifies `spatial-data-engineer` discipline.

---

_Last reviewed: 2026-06-20 by `claude`_
