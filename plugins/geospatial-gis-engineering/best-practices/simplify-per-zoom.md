# Simplify (generalize) geometry per zoom, deliberately

**Status:** Pattern
**Domain:** Web mapping / tiling
**Applies to:** `geospatial-gis-engineering`

---

## Why this exists

Street-level vertex density is wasted at a country-level view: it bloats tiles and slows rendering with detail no one can see. Per-zoom generalization (dropping/merging vertices as you zoom out) keeps tiles small and the map fast — but it changes the geometry, so the tolerance is a deliberate choice, not a silent default.

## How to apply

```sql
-- Generalize for a low zoom (tolerance in the layer's units)
SELECT ST_AsMVTGeom(ST_Simplify(ST_Transform(geom, 3857), :tolerance), :bbox)
FROM admin_boundaries;
```

- Tools like `tippecanoe` apply per-zoom simplification when building the pyramid.
- Name the tolerance per layer/zoom; preserve topology where adjacency matters (`ST_SimplifyPreserveTopology` or topology-aware tooling).

**Do:**
- Generalize as a designed step; document the tolerance.
- Preserve shared boundaries between adjacent polygons.

**Don't:**
- Ship full-resolution geometry to every zoom.
- Over-simplify so shapes self-intersect or boundaries gap.

## Edge cases / when the rule does NOT apply

Analytical/measurement layers should use full-resolution source geometry — simplification is a *display* optimization, not a data transform you analyze on.

## See also

- [`./tile-large-layers-dont-ship-giant-geojson.md`](./tile-large-layers-dont-ship-giant-geojson.md)
- [`../skills/build-map-tiles-and-serving/SKILL.md`](../skills/build-map-tiles-and-serving/SKILL.md)

## Provenance

PostGIS `ST_Simplify`/`ST_SimplifyPreserveTopology`; tippecanoe zoom handling. Codifies `gis-architect`/`geospatial-app-engineer` discipline.

---

_Last reviewed: 2026-06-20 by `claude`_
