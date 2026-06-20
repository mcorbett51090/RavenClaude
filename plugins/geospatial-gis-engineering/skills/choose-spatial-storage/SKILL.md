---
name: choose-spatial-storage
description: "Decide where spatial data lives: PostGIS (transactional map apps, mixed read/write) vs a geospatial warehouse (BigQuery GIS / Snowflake / GeoParquet for analytics at scale) vs a tile/feature service (mostly-read basemaps and large static layers)."
---

# Choose Spatial Storage

Match the store to the **workload**, not the buzzword.

## The split

| Workload | Default store | Why |
|---|---|---|
| Transactional map app (CRUD + "near me", moderate volume) | **PostGIS** | One engine for relational + spatial; GiST indexes; full spatial SQL |
| Analytics over 10⁸–10⁹+ features / points | **Geospatial warehouse** (BigQuery GIS, Snowflake geospatial, GeoParquet on object storage + DuckDB/Spark) | Columnar scale, clustering; not for low-latency single-feature CRUD |
| Mostly-read large/static layers, basemaps | **Tile / feature service** (pre-rendered MVT/raster pyramid, OGC API – Features) | Cheap fan-out reads; no per-request spatial compute |

## Decisions that follow the store
- **CRS:** store canonical SRID (4326 default; projected when accuracy/tiles demand) — see [`../design-coordinate-reference-system/SKILL.md`](../design-coordinate-reference-system/SKILL.md).
- **Index:** GiST in PostGIS; clustering/partitioning in the warehouse; tile pyramid for the service.
- **Geometry vs geography:** a per-column call (see [`../write-spatial-queries/SKILL.md`](../write-spatial-queries/SKILL.md)).

## Anti-patterns
- A geospatial warehouse used as a transactional map backend (latency, cost per query).
- PostGIS asked to scan billions of points per dashboard load (move it to the warehouse or pre-tile).
- Duplicating geometry columns per CRS instead of reprojecting on read.

Traverse the storage tree in [`../../knowledge/geospatial-decision-trees.md`](../../knowledge/geospatial-decision-trees.md) before committing.
