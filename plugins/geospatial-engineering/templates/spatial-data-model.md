# Spatial data model — <dataset / table name>

> Fill this in **before** writing the DDL. The CRS decision and the index are part of
> the model, not afterthoughts — a column without an explicit SRID or a GiST index is
> a model bug. Traverse the projection decision tree first.

**Author:** <name> · **Date:** <YYYY-MM-DD> · **Source data:** <shapefile / GeoJSON / API / sensor feed + its native SRID>

## 1. What the data is
- **Entity:** <delivery stop / parcel / road segment / sensor reading …>
- **Geometry type:** <Point / LineString / Polygon / Multi… >
- **Approximate feature count:** <N> · **Update cadence:** <static / batch / streaming>

## 2. CRS decision (from the projection decision tree)
- **Job the data does:** <web-map serving / global analysis / local metric accuracy>
- **Chosen SRID:** <4326 / 3857 / UTM zone / state-plane> · **Why:** <one line tied to the job>
- **Storage type:** <`geography` (true metres, global) | `geometry` (planar, fast, metric CRS)> · **Why:** <one line>
- **Native source SRID:** <…> → **reproject on load?** <yes via `ST_Transform`/`ogr2ogr -t_srs` / no>

## 3. Schema (DDL)
```sql
CREATE TABLE <table> (
    id    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    <attributes …>,
    geom  <geometry|geography>(<Type>, <SRID>) NOT NULL   -- explicit SRID, never bare
);

CREATE INDEX <table>_geom_gix ON <table> USING GIST (geom);   -- spatial index, not optional

-- validate
SELECT ST_SRID(geom<::geometry if geography>) FROM <table> LIMIT 1;   -- expect <SRID>
```

## 4. Query access patterns (drives the index choice)
- **Primary spatial query:** <proximity / nearest-neighbor / spatial join / overlay>
- **Index:** <GiST (default) / SP-GiST for clustered points> · **Confirmed Index Scan?** <EXPLAIN result>
- **Units required:** <metres / feet> · **How guaranteed:** <geography / projected CRS>

## 5. Pipeline hygiene (if loaded via GDAL/OGR)
- **Load command:** `ogr2ogr -f PostgreSQL … -s_srs <src> -t_srs <dst> …`
- **Post-load validation:** <SRID check, geometry validity `ST_IsValid`, extent in-range>

## 6. Seams
- **Served on a map?** → hand the SRID + table to `mapping-visualization-engineer`.
- **Non-spatial schema (keys, normalization)?** → `database-engineering`.
