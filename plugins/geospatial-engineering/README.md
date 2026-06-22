# geospatial-engineering

> The **geospatial / GIS engineering** team for Claude Code — the engineering of *location data*. Two specialists: one makes spatial data correct and fast in the database; the other gets it onto a map. Answers the questions a generic data or frontend engineer can't safely answer: **which coordinate system?**, **geometry or geography?**, **why is this spatial query slow?**, **vector tiles or GeoJSON?**

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Model this in PostGIS — which SRID? geometry or geography?" | A CRS-first schema: explicit SRID + the right type + a GiST index + runnable `CREATE TABLE` |
| "Why is this spatial query slow / returning weird tiny numbers?" | Diagnosis (no index / degrees-not-metres / SRID mismatch) + an index-aware rewrite with correct units |
| "Load and reproject this shapefile/GeoTIFF" | A GDAL/OGR (`ogr2ogr`/`gdalwarp`) recipe with CRS hygiene + an SRID-tagged target table |
| "How do I serve 400k features without my map crawling?" | A GeoJSON-vs-vector-tile decision + a pg_tileserv/Martin/Tegola recipe + the MapLibre style |
| "My MapLibre map is slow / blank / mis-projected" | Diagnosis (megabyte GeoJSON / wrong tile SRID / over-dense geometry) + the fix + a corrected style |

**Three rules it never breaks:** *always store an SRID*, *index geometry with GiST*, and *vector tiles over GeoJSON at scale*.

## What's inside

- **2 agents** — `geospatial-data-engineer` (PostGIS, SRID/projections, spatial SQL, GDAL/OGR, geocoding, routing) and `mapping-visualization-engineer` (vector tiles/MVT, tile servers, MapLibre styling, raster vs vector).
- **3 skills** — `design-postgis-schema`, `write-spatial-query`, `serve-vector-tiles`.
- **2 knowledge files** — a projection/CRS Mermaid decision tree (pick the SRID + geometry-vs-geography by use-case) and a dated 2026 stack reference (PostGIS, GDAL, pg_tileserv/Martin/Tegola, MapLibre, OSRM/Valhalla).
- **2 templates** — spatial data model, tile-serving architecture.
- **3 best-practice rules** — always-store-an-SRID, index-geometry-with-GiST, vector-tiles-over-GeoJSON-at-scale.
- **1 advisory hook** — `flag-geo-smells.sh` (geometry-without-SRID, degree-distance, `ST_Distance(...) <` index-defeating filter).

## How it seams with adjacent plugins

```
geospatial-engineering   →  the engineering of location data (PostGIS, spatial SQL, tiles, maps)
data-platform            →  generic warehouse / ELT of non-spatial facts
database-engineering     →  the non-spatial OLTP schema (keys, normalization, migrations)
frontend-engineering     →  surrounding map UI chrome, layout, CSS
```

Precision-agriculture and fleet-logistics plugins are **consumers** of this engineering layer, not part of it.

## Tooling stance

PostGIS + GDAL are the Tier-1 spine; vector tiles (pg_tileserv / Martin / Tegola) + MapLibre GL are the Tier-1 serving/visualization layer. Versions carry retrieval dates — re-verify before pinning in a client deliverable. See [`knowledge/geospatial-stack-2026.md`](knowledge/geospatial-stack-2026.md).

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install geospatial-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
