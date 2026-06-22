# Serve vector tiles, not GeoJSON, once feature count or zoom demands it

**Status:** Pattern (strong default; deviate only with a written reason)
**Domain:** Geospatial serving / web-map performance
**Applies to:** `geospatial-engineering`

---

## Why this exists

GeoJSON is a **transport format**, not a serving strategy. Handing a browser a single GeoJSON of every feature means: the whole dataset crosses the wire at once, the client holds it all in memory, and the renderer draws full-resolution geometry at every zoom — wonderful for a few hundred features, a foot-gun at a hundred thousand, where it produces a multi-megabyte download and a map that hangs. **Vector tiles (MVT)** invert all three costs: the server cuts the data into a pyramid of small, **zoom-simplified, bbox-clipped** tiles, the client fetches only the tiles in view at the current zoom, and styling moves to the client so one tile set serves infinite restyles with no re-export. The decision point is **feature count and zoom interactivity**, and it should be made explicitly — not defaulted to "just send a GeoJSON."

## How to apply

Decide the format by size and zoom *before* building the serving layer:

| Situation | Serve as |
|---|---|
| ≲ a few hundred static features, no per-zoom simplification | **GeoJSON** (simple, no server) |
| thousands → millions, or zoom-dependent, or restyleable | **vector tiles (MVT)** via pg_tileserv / Martin / Tegola / MBTiles-PMTiles |
| true imagery / heavy cartography | **raster tiles** (XYZ / WMTS) |

For vector tiles, the server reprojects to **EPSG:3857**, clips with `ST_AsMVTGeom`, and simplifies per zoom; the MapLibre `source-layer` name must match the server's layer.

**Do:**
- Count features and consider zoom before choosing; document the choice.
- Reach for vector tiles at the thousands-of-features / zoom-dependent threshold.
- Simplify per zoom (`ST_SimplifyPreserveTopology` / `ST_AsMVTGeom`) so tiles stay small.

**Don't:**
- Ship a multi-megabyte GeoJSON of every feature to the client (the #1 slow-map cause).
- Serve full z18 geometry detail at z3.
- Forget the source must be `ST_Transform`ed to 3857 — a mismatch yields a blank map.

## Edge cases / when the rule does NOT apply

- **Small, frequently-mutating overlays** (a handful of live features) are fine as GeoJSON updated in place — tiling overhead isn't worth it.
- **One-off analytical snapshots** a user downloads (not a live map) are legitimately GeoJSON/GeoPackage files, not a tile service.
- **True raster imagery** belongs in raster tiles, not vector tiles — vector tiles are for restyleable vector data.

## See also

- [`../knowledge/geospatial-stack-2026.md`](../knowledge/geospatial-stack-2026.md) — the tile-server + MapLibre tooling rows.
- [`../skills/serve-vector-tiles/SKILL.md`](../skills/serve-vector-tiles/SKILL.md) — the format-decision + serving + MapLibre-wiring procedure.
- [`../templates/tile-serving-architecture.md`](../templates/tile-serving-architecture.md) — the architecture worksheet that records this decision.

## Provenance

Codifies the `mapping-visualization-engineer` house opinion "GeoJSON is a transport format, not a serving strategy at scale" ([`../CLAUDE.md`](../CLAUDE.md)). Grounded in MapLibre, pg_tileserv, and Martin documentation (MVT serving, zoom-dependent simplification, 3857 tiles), retrieved 2026-06-17.

---

_Last reviewed: 2026-06-17 by `claude`_
