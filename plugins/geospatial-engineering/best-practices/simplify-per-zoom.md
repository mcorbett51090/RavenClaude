# Simplify (generalize) geometry per zoom, deliberately

**Status:** Pattern (strong default; deviate only with a written reason)
**Domain:** Web mapping / tiling
**Applies to:** `geospatial-engineering`

---

## Why this exists

Street-level vertex density is wasted at a country-level view: it bloats tiles and slows rendering with detail no one can see. Per-zoom generalization (dropping / merging vertices as you zoom out) keeps tiles small and the map fast — but it **changes the geometry**, so the tolerance is a deliberate choice, not a silent default. Shipping full-resolution z18 geometry at z3 is the per-zoom companion to shipping a giant GeoJSON: the right data, in the wrong amount, for the view.

## How to apply

```sql
-- Generalize for a low zoom (tolerance in the layer's units)
SELECT ST_AsMVTGeom(ST_Simplify(ST_Transform(geom, 3857), :tolerance), :bbox)
FROM admin_boundaries;
```

- Tools like `tippecanoe` apply per-zoom simplification when building the pyramid.
- Name the tolerance per layer / zoom; preserve topology where adjacency matters (`ST_SimplifyPreserveTopology` or topology-aware tooling).

**Do:**
- Generalize as a designed step; document the tolerance.
- Preserve shared boundaries between adjacent polygons.

**Don't:**
- Ship full-resolution geometry to every zoom.
- Over-simplify so shapes self-intersect or boundaries gap.

## Edge cases / when the rule does NOT apply

Analytical / measurement layers should use full-resolution source geometry — simplification is a *display* optimization, not a data transform you analyze on.

## See also

- [`./tile-large-layers-dont-ship-giant-geojson.md`](./tile-large-layers-dont-ship-giant-geojson.md) — the companion serving rule.
- [`./vector-tiles-over-geojson-at-scale.md`](./vector-tiles-over-geojson-at-scale.md) — the format decision per-zoom simplification lives inside.
- [`../skills/serve-vector-tiles/SKILL.md`](../skills/serve-vector-tiles/SKILL.md) — `ST_AsMVTGeom` / `ST_SimplifyPreserveTopology` in the serving recipe.

## Provenance

Codifies the `geospatial-engineering` anti-pattern "full-resolution geometry at low zoom — no per-zoom simplification" ([`../CLAUDE.md`](../CLAUDE.md) §4). Grounded in PostGIS `ST_Simplify` / `ST_SimplifyPreserveTopology` and tippecanoe zoom handling, retrieved 2026-06-22.

---

_Last reviewed: 2026-06-22 by `claude`_
