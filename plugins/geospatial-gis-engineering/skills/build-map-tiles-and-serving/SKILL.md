---
name: build-map-tiles-and-serving
description: "Serve and render spatial data on the web: vector tiles (MVT) vs GeoJSON vs raster, tile pyramids and per-zoom generalization, MapLibre GL / Leaflet rendering, clustering and viewport-bound fetching for large feature sets, and basemap/attribution choices."
---

# Build Map Tiles & Serving

The goal: a map that stays smooth as data grows, with correct coordinates.

## Format by feature count + cadence
| Layer | Format |
|---|---|
| Small (≲ a few thousand), changes often | **GeoJSON** straight to the client |
| Large, styleable, zoomable | **Vector tiles (MVT)** — pre-rendered pyramid or a tile server (e.g. from PostGIS `ST_AsMVT`) |
| Imagery, heavy cartography | **Raster tiles** (XYZ/WMTS pyramid) |

## Rendering strategy (large N)
- Never create N DOM markers for large N — use GL symbol layers, vector tiles, or **clustering**.
- **Fetch the viewport**, not the world; **simplify per zoom** (`ST_Simplify` / tile generalization).
- Style and interact **on the loaded tile** (data-driven expressions, feature-state for hover/select) — avoid re-fetching to filter.

## Coordinate correctness
- GeoJSON is **`[longitude, latitude]`** (RFC 7946), WGS84 (4326), right-hand-rule winding. Swapped lon/lat is the "data in the ocean" bug.
- Web maps render in **EPSG:3857**; the tile server reprojects from your canonical SRID.

## Serving
- **Pre-rendered pyramid** when data updates rarely (cheap CDN reads).
- **On-the-fly tile server** (`ST_AsMVT`, pg_tileserv, or martin) when data updates often.
- Surface **attribution + licensing** for every basemap/tile source.

## Anti-patterns
- A 30MB GeoJSON shipped to the browser (tile it).
- Heavy spatial work in the client (push to server/tiles).
- Computing area client-side in Web Mercator.

See [`../../knowledge/geospatial-stack-2026.md`](../../knowledge/geospatial-stack-2026.md) for current libraries (dated; re-verify).
