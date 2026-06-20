# Tile large layers — don't ship a giant GeoJSON or N DOM markers

**Status:** Pattern
**Domain:** Web mapping / performance
**Applies to:** `geospatial-gis-engineering`

---

## Why this exists

A multi-megabyte GeoJSON blocks the main thread on parse and bloats memory; rendering tens of thousands of individual DOM markers freezes the browser. Vector tiles (MVT) deliver only the features in the current viewport and zoom, GL-rendered, so the map stays smooth as the dataset grows.

## How to apply

- **Small + dynamic** (≲ a few thousand features) → GeoJSON straight to the client.
- **Large + styleable** → vector tiles: pre-render with `tippecanoe` → PMTiles/MBTiles, or serve on-the-fly from PostGIS (`ST_AsMVT`, pg_tileserv/martin).
- **Many points** → clustering or a GL symbol layer, never N DOM markers.
- Fetch the **viewport**, not the world.

**Do:**
- Tile anything large; render with MapLibre GL / deck.gl for scale.

**Don't:**
- Ship a 30MB GeoJSON; create 50k Leaflet markers; re-fetch to filter when you can filter on the loaded layer.

## Edge cases / when the rule does NOT apply

A frequently-changing small layer (live vehicle positions, a few hundred) is fine as GeoJSON pushed over a socket — tiling adds latency you don't want.

## See also

- [`./simplify-per-zoom.md`](./simplify-per-zoom.md)
- [`../knowledge/geospatial-stack-2026.md`](../knowledge/geospatial-stack-2026.md)

## Provenance

MVT specification; MapLibre GL / tippecanoe / PMTiles docs. Codifies `geospatial-app-engineer` house opinion.

---

_Last reviewed: 2026-06-20 by `claude`_
