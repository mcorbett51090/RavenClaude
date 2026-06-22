# Tile large layers — don't ship a giant GeoJSON or N DOM markers

**Status:** Pattern (strong default; deviate only with a written reason)
**Domain:** Web mapping / performance
**Applies to:** `geospatial-engineering`

---

## Why this exists

A multi-megabyte GeoJSON blocks the main thread on parse and bloats memory; rendering tens of thousands of individual DOM markers freezes the browser. Vector tiles (MVT) deliver only the features in the current viewport and zoom, GL-rendered, so the map stays smooth as the dataset grows. This is the *serving-tree* leaf of the same decision the `vector-tiles-over-geojson-at-scale` rule frames — kept as its own rule because the failure mode (N DOM markers, world-fetch) is distinct from the format choice.

## How to apply

- **Small + dynamic** (≲ a few thousand features) → GeoJSON straight to the client.
- **Large + styleable** → vector tiles: pre-render with `tippecanoe` → PMTiles / MBTiles, or serve on-the-fly from PostGIS (`ST_AsMVT`, pg_tileserv / Martin).
- **Many points** → clustering or a GL symbol layer, never N DOM markers.
- Fetch the **viewport**, not the world.

**Do:**
- Tile anything large; render with MapLibre GL / deck.gl for scale.

**Don't:**
- Ship a 30 MB GeoJSON; create 50k Leaflet markers; re-fetch to filter when you can filter on the loaded layer.

## Edge cases / when the rule does NOT apply

A frequently-changing small layer (live vehicle positions, a few hundred) is fine as GeoJSON pushed over a socket — tiling adds latency you don't want.

## See also

- [`./vector-tiles-over-geojson-at-scale.md`](./vector-tiles-over-geojson-at-scale.md) — the format-by-feature-count decision this enforces.
- [`./simplify-per-zoom.md`](./simplify-per-zoom.md) — keeping each tile small once you tile.
- [`../knowledge/storage-and-serving-decision-trees.md`](../knowledge/storage-and-serving-decision-trees.md) — the serving-format decision tree.

## Provenance

Codifies the `geospatial-engineering` anti-pattern "shipping a multi-megabyte GeoJSON to the browser where vector tiles belong" ([`../CLAUDE.md`](../CLAUDE.md) §4). Grounded in the MVT specification and MapLibre GL / tippecanoe / PMTiles documentation, retrieved 2026-06-22.

---

_Last reviewed: 2026-06-22 by `claude`_
