---
name: spatial-data-quality
description: "Keep spatial data trustworthy: geometry validity (ST_IsValid / ST_MakeValid, self-intersections, ring order), topology, declared-vs-actual SRID checks, coordinate-order (lon/lat) sanity, and validating geometry at load time so bad data never lands. Reach for this when loading a dataset, debugging a function that crashes on some rows, or hardening an ingest. Used by `geospatial-data-engineer` (primary)."
---

# Skill: spatial-data-quality

> **Invoked by:** `geospatial-data-engineer` (primary). Pairs with `design-postgis-schema` (the table the validated data lands in) and `write-spatial-query` (when a query crashes on invalid geometry).
>
> **When to invoke:** loading a Shapefile / GeoJSON / GeoPackage; "`ST_Area`/`ST_Union` crashes on some rows"; "my points show up in the ocean"; hardening an ingest so bad geometry never lands.
>
> **Output:** the validity / SRID / coordinate-order / topology checks + a validate-at-load constraint or repair-on-ingest query, run at the boundary.

Bad geometry fails silently in some functions and loudly in others — gate it at the boundary.

## The checks

1. **Validity:** `ST_IsValid(geom)` / repair with `ST_MakeValid(geom)`. Self-intersections and bad ring order break `ST_Area`, `ST_Intersection`, `ST_Union`.
2. **SRID present and correct:** `ST_SRID(geom)` is the declared SRID (not `0`); enforce with a typmod `geometry(Polygon, 4326)`.
3. **Coordinate order / extent sanity:** values plausibly within the CRS bounds (lon ∈ [-180,180], lat ∈ [-90,90] for 4326). A cluster off west Africa = swapped lon/lat.
4. **Topology** (where it matters): no gaps / overlaps between adjacent polygons (e.g. admin boundaries) — check with `ST_Relate` / topology rules.
5. **Empty / null geometry** handled explicitly (`ST_IsEmpty`).

## Validate at load, not after

```sql
-- Reject invalid geometry on insert
ALTER TABLE parcels
  ADD CONSTRAINT parcels_geom_valid CHECK (ST_IsValid(geom));

-- Or repair on the way in
INSERT INTO parcels (geom)
SELECT ST_MakeValid(ST_SetSRID(raw_geom, 4326)) FROM staging;
```

## Loading checklist (ogr2ogr)

- `-s_srs` set to the **source** CRS, `-t_srs` to the **table** CRS.
- `-nlt PROMOTE_TO_MULTI` where mixed single / multi geometry would otherwise fail.
- Validate (`ST_IsValid`) and reproject before the data is queryable.

## Guardrails

- Trusting a file's claimed CRS without checking the extent is how lon/lat swaps land — sanity-check the extent (the GeoJSON-is-lon-lat trap).
- Never run area / union on un-validated polygons.
- Never let SRID `0` (unknown) into a column — declare a typmod. See [`../../best-practices/validate-geometry-at-load.md`](../../best-practices/validate-geometry-at-load.md), [`../../best-practices/geojson-is-lon-lat.md`](../../best-practices/geojson-is-lon-lat.md), and [`../../best-practices/always-store-an-srid.md`](../../best-practices/always-store-an-srid.md).
