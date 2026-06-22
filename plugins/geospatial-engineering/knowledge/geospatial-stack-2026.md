# Knowledge — The geospatial engineering stack (2026)

> **Last reviewed:** 2026-06-17 · **Confidence:** Medium-High (mature, widely-deployed open-source tooling; **versions are volatile — re-verify before pinning in a client deliverable**).
> Tiered reference for the tools the two agents recommend. Tier 1 = the default spine; Tier 2 = reach for it with a reason. **Every version/recency claim below carries the 2026-06-17 retrieval date and must be re-checked** (house opinion: volatile tooling claims carry retrieval dates).

---

## Storage & spatial SQL

| Tool | Tier | What it is | Notes (retrieved 2026-06-17) |
|---|---|---|---|
| **PostGIS** (on PostgreSQL) | 1 | The reference spatial database — `geometry`/`geography` types, `ST_` functions, GiST/SP-GiST indexing, raster, topology. | The default for *any* spatial storage + analysis. `geography` for global true-metre work; projected `geometry` for fast local work. Pair with a GiST index always. |
| **SpatiaLite** | 2 | SQLite + spatial extension. | Embedded / single-file / offline use; not for concurrent server workloads. |
| **DuckDB spatial** | 2 | DuckDB extension for analytical spatial queries. | Fast columnar spatial analytics / ad-hoc; complements, doesn't replace, PostGIS for OLTP+serving. |
| **BigQuery GIS** | 2 | Warehouse-native spatial analytics over very large feature sets. | `GEOGRAPHY` type (spheroidal, WGS84); clustering, no manual index. For analytics at scale, not a map backend (see the storage decision tree). `[verify-at-use]` current capabilities. |
| **Snowflake geospatial** | 2 | Warehouse-native spatial analytics. | `GEOGRAPHY` / `GEOMETRY` types. Same role as BigQuery GIS — analytics scale, not transactional serving. `[verify-at-use]`. |
| **GeoParquet** | 2 | Columnar spatial files on object storage. | Open format; pairs with DuckDB / Spark / warehouse for analytics-scale vector. Not a query engine — a storage format the engines read. |

## Pipelines & data movement

| Tool | Tier | What it is | Notes (retrieved 2026-06-17) |
|---|---|---|---|
| **GDAL / OGR** (`ogr2ogr`, `gdalwarp`, `gdal_translate`) | 1 | The universal translator for vector (OGR) and raster (GDAL) formats + reprojection. | Load shapefile/GeoJSON/GeoPackage → PostGIS, reproject (`-t_srs`), convert formats. Always assert source SRID + set target SRID. |
| **GeoPackage / FlatGeobuf** | 1 | Modern open container formats (vs legacy shapefile). | Prefer over shapefile (no 2GB / field-name limits); FlatGeobuf streams well. |
| **PROJ** | 1 | The reprojection engine under GDAL / PostGIS (EPSG transforms). | You rarely call it directly — it's what `ST_Transform` / `ogr2ogr -t_srs` use; pin its grid/version for authoritative transforms. |
| **Shapely / GeoPandas** (Python) | 2 | In-memory geometry ops + spatial dataframes. | Notebook / pipeline geometry work; reads GeoParquet / GeoPackage. Not a serving layer. |
| **Turf.js** | 2 | Client / Node geometry ops in JavaScript. | Lightweight in-browser/Node spatial ops (buffer, within, distance) without a round-trip. |
| **PDAL** | 2 | Point-cloud (LiDAR) pipeline. | Only when the data is point clouds. |

## Geocoding & routing

| Tool | Tier | What it is | Notes (retrieved 2026-06-17) |
|---|---|---|---|
| **Nominatim** | 1 | OSM-based geocoder (address ↔ coordinate). | Self-host for volume / privacy; respect usage policy on the public instance. |
| **OSRM** | 1 | Fast OSM routing engine (contraction hierarchies). | Fastest for fixed-profile shortest-path at scale; less flexible per-request costing. |
| **Valhalla** | 1 | Tiled OSM routing engine. | More flexible (multi-modal, dynamic costing, time-distance matrices); heavier setup. |
| **pgRouting** | 2 | Routing inside PostGIS. | When the network already lives in PostGIS and volumes are modest. |

## Serving (tiles)

| Tool | Tier | What it is | Notes (retrieved 2026-06-17) |
|---|---|---|---|
| **pg_tileserv** | 1 | Zero-config dynamic MVT vector tiles straight from PostGIS tables/functions. | Easiest path from an indexed PostGIS table to vector tiles. Tiles served in 3857. |
| **Martin** | 1 | Fast Rust vector-tile server (PostGIS + MBTiles + PMTiles sources). | High-throughput; config-driven; broad source support. |
| **Tegola** | 1 | Go vector-tile server with caching. | Good when pre-generation / caching matters. |
| **MBTiles / PMTiles** | 1 | Single-file tile archives (PMTiles = cloud-native, range-request friendly). | Pre-generated static tiles; PMTiles serves from object storage with no tile server. |
| **tippecanoe** | 1 | Pre-renders vector-tile pyramids from GeoJSON (per-zoom simplification built in). | The standard "build a static MVT pyramid → PMTiles/MBTiles" tool; applies per-zoom generalization. |
| **TiTiler / rio-tiler** | 2 | Dynamic raster (COG) tiling. | Serve Cloud-Optimized GeoTIFF imagery as raster tiles on-the-fly. Raster path, not vector. |

## Visualization (client)

| Tool | Tier | What it is | Notes (retrieved 2026-06-17) |
|---|---|---|---|
| **MapLibre GL JS** | 1 | Open-source GL vector/raster map renderer (community fork of Mapbox GL JS v1). | The default open web map client — no token gate; style spec drives data-driven, zoom-dependent styling. |
| **Mapbox GL JS** | 2 | Proprietary GL renderer + basemaps. | Reach for when the vendor basemap/ecosystem is genuinely easier and the token/licensing is acceptable. |
| **deck.gl** | 2 | WebGL data-visualization layers (large-scale points/arcs/hexbins). | Heavy analytical overlays; pairs with MapLibre as a base. |
| **Leaflet** | 2 | Lightweight raster/vector map library. | Simple raster maps / small feature counts; not GL vector-tile native. |
| **OpenLayers** | 2 | Feature-rich mapping incl. WMS/WMTS/projection variety. | When you need non-Mercator projections in-browser, or OGC WMS/WMTS support MapLibre doesn't give. |

---

## Formats

| Format | Tier | Use |
|---|---|---|
| **GeoJSON** (RFC 7946) | 1 | Interchange + small / dynamic web layers — `[lon, lat]`, WGS84. |
| **Vector tiles (MVT)** | 1 | Large styleable web layers (the serving default at scale). |
| **Cloud-Optimized GeoTIFF (COG)** | 1 | Raster / imagery on object storage, range-read tiling (pairs with TiTiler). |
| **GeoParquet** | 2 | Analytics-scale vector on object storage (pairs with DuckDB / warehouse). |
| **FlatGeobuf** | 2 | Streaming, indexed binary vector. |

## Standards bodies / references

- **OGC** — Simple Features, GeoPackage, OGC API – Features / Tiles / Maps.
- **EPSG registry** (epsg.io) — authoritative CRS codes (4326, 3857, UTM, state-plane, national grids).
- **RFC 7946** — the GeoJSON specification (coordinate order, CRS, polygon winding).

---

## How the agents pick from this

- **geospatial-data-engineer** lives in the *Storage / spatial SQL / Pipelines / Geocoding & routing* rows — PostGIS + GDAL Tier 1, with the CRS decision from [`projection-decision-tree.md`](projection-decision-tree.md).
- **mapping-visualization-engineer** lives in the *Serving / Visualization* rows — vector tiles via pg_tileserv/Martin/Tegola Tier 1, MapLibre Tier 1.

## Provenance

- PostGIS, GDAL/OGR, OSRM, Valhalla, Nominatim, pg_tileserv, Martin, Tegola, MapLibre official project documentation (retrieved 2026-06-17). **Versions and project status move — re-verify with `ravenclaude-core/deep-researcher` before quoting in a client deliverable.**

---

_Last reviewed: 2026-06-17 by `claude`_
