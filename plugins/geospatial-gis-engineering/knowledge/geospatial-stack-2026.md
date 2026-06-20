# Geospatial Stack — 2026 Capability Map

> Dated snapshot of the geospatial tooling the team recommends. **Versions and product capabilities are volatile — re-verify against the vendor/project before quoting to a client.** The durable reasoning lives in [`geospatial-decision-trees.md`](geospatial-decision-trees.md); this file is the freshness-anchored "what to reach for."
>
> _Last reviewed: 2026-06-20 by `claude`. Each row carries a confidence note; treat unmarked specifics as `[verify-at-use]`._

---

## Spatial databases & engines

| Tool | Use for | Note |
|---|---|---|
| **PostGIS** (on PostgreSQL) | Transactional spatial + relational; the default | Mature, GiST/SP-GiST indexes, `geography`+`geometry`, MVT (`ST_AsMVT`). `[verify-at-use]` current major version |
| **BigQuery GIS** | Analytics over very large point/feature sets | `GEOGRAPHY` type (spheroidal, WGS84); clustering, no manual index |
| **Snowflake geospatial** | Warehouse-native spatial analytics | `GEOGRAPHY`/`GEOMETRY` types |
| **DuckDB `spatial`** | Local/embedded analytics, GeoParquet | Lightweight; great for pipelines and notebooks |
| **GeoParquet** | Columnar spatial files on object storage | Open format; pairs with DuckDB/Spark/warehouse |

## Libraries & processing

| Tool | Use for |
|---|---|
| **GDAL/OGR** (`ogr2ogr`, `gdalwarp`) | The swiss-army knife: convert, reproject, load any format |
| **PROJ** | The reprojection engine under GDAL/PostGIS (EPSG transforms) |
| **Shapely / GeoPandas** (Python) | In-memory geometry ops + dataframes |
| **Turf.js** | Client/Node geometry ops in JS |

## Web map rendering

| Tool | Use for | Note |
|---|---|---|
| **MapLibre GL JS** | GL-rendered vector tiles, large data, styling | Open-source fork of Mapbox GL JS; the default for scale |
| **Leaflet** | Simple, lightweight raster/GeoJSON maps | Great for small layers; less suited to huge vector data |
| **deck.gl** | GPU-accelerated large-scale data viz layers | When you're rendering millions of points/arcs |
| **OpenLayers** | Feature-rich mapping incl. WMS/WMTS/projection variety | When you need non-Mercator projections in-browser |

## Tile serving

| Tool | Use for |
|---|---|
| **pg_tileserv / martin** | On-the-fly MVT from PostGIS |
| **tippecanoe → PMTiles/MBTiles** | Pre-render vector tile pyramids from GeoJSON |
| **PMTiles** | Single-file tile archive served from object storage/CDN (no tile server) |
| **TiTiler / rio-tiler** | Dynamic raster (COG) tiling |

## Formats

| Format | Use |
|---|---|
| **GeoJSON** (RFC 7946) | Interchange, small/dynamic web layers — `[lon, lat]`, WGS84 |
| **Vector tiles (MVT)** | Large styleable web layers |
| **Cloud-Optimized GeoTIFF (COG)** | Raster/imagery on object storage, range-read tiling |
| **GeoParquet** | Analytics-scale vector on object storage |
| **FlatGeobuf** | Streaming, indexed binary vector |

## Standards bodies / references

- **OGC** — Simple Features, GeoPackage, OGC API – Features/Tiles/Maps.
- **EPSG registry** (epsg.io) — authoritative CRS codes.
- **RFC 7946** — the GeoJSON specification (coordinate order, CRS, winding).

---

_Re-verify any version, pricing, or capability claim against the source before it reaches a client deliverable — these move quarterly._
