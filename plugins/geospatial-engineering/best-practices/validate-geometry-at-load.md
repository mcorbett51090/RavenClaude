# Validate geometry at load time, not after it breaks

**Status:** Absolute rule
**Domain:** Spatial data quality
**Applies to:** `geospatial-engineering`

---

## Why this exists

Invalid geometry (self-intersecting polygons, bad ring order) passes some functions silently and crashes others (`ST_Area`, `ST_Intersection`, `ST_Union`). If it lands in the table, the failure surfaces far from the cause — weeks later, in an analysis that touches one bad row. Validating and repairing at the **ingest boundary** keeps the table trustworthy, the same way the explicit-SRID rule keeps the coordinate system trustworthy: catch the problem at write time, not at read time.

## How to apply

```sql
-- Constraint: reject invalid geometry on insert
ALTER TABLE parcels ADD CONSTRAINT parcels_geom_valid CHECK (ST_IsValid(geom));

-- Or repair on the way in
INSERT INTO parcels (geom)
SELECT ST_MakeValid(ST_SetSRID(raw_geom, 4326)) FROM staging;
```

**Do:**
- Run `ST_IsValid` / `ST_MakeValid` at load.
- Check the extent matches the CRS bounds (lon ∈ [-180,180], lat ∈ [-90,90] for 4326) — catches swapped lon/lat.
- Set the SRID on ingest (companion to always-store-an-srid).

**Don't:**
- Trust a file's declared CRS without an extent sanity check.
- Run area / union on un-validated polygons.

## Edge cases / when the rule does NOT apply

`ST_MakeValid` can change vertex counts / topology; for legally-authoritative boundaries, repair under review rather than blindly.

## See also

- [`./always-store-an-srid.md`](./always-store-an-srid.md) — the companion ingest-boundary rule (the SRID half).
- [`./geojson-is-lon-lat.md`](./geojson-is-lon-lat.md) — the coordinate-order check the extent sanity catches.
- [`../skills/spatial-data-quality/SKILL.md`](../skills/spatial-data-quality/SKILL.md) — the full validate-at-load procedure.

## Provenance

Codifies the `geospatial-engineering` discipline "assert source SRID, set target SRID, range-validate the result" through every pipeline hop ([`../CLAUDE.md`](../CLAUDE.md) §3). Grounded in PostGIS validity functions (`ST_IsValid` / `ST_MakeValid`) and OGC Simple Features, retrieved 2026-06-22.

---

_Last reviewed: 2026-06-22 by `claude`_
