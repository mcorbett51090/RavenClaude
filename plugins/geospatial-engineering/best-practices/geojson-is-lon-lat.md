# GeoJSON coordinates are [longitude, latitude]

**Status:** Absolute rule
**Domain:** Formats / web mapping
**Applies to:** `geospatial-engineering`

---

## Why this exists

RFC 7946 fixes GeoJSON coordinate order as `[longitude, latitude]` (X, Y) in WGS84 (EPSG:4326), with the right-hand rule for polygon winding. People who think "lat, long" (because we say it that way out loud) swap them — and the data renders in the wrong hemisphere. The classic symptom: points meant for a city show up in the ocean off west Africa, where `lon = lat ≈ 0` swaps land for sea. It is the single most common web-map "wrong place" bug.

## How to apply

```json
{ "type": "Point", "coordinates": [-0.1276, 51.5072] }   // London: [lon, lat]
```

**Do:**
- Emit and consume GeoJSON as `[lon, lat]`, WGS84.
- Follow the right-hand rule (exterior ring counter-clockwise) for polygons.
- Sanity-check the extent after loading.

**Don't:**
- Write `[lat, lon]` (the most common GeoJSON bug).
- Put a non-4326 CRS in GeoJSON — the spec is WGS84.

## Edge cases / when the rule does NOT apply

Some legacy tools emit a non-standard `crs` member or `[lat, lon]`; detect and normalize on ingest rather than propagating it. (Note: Leaflet's *own* JS `LatLng` API is `[lat, lng]` — that's the library object, not GeoJSON.)

## See also

- [`./validate-geometry-at-load.md`](./validate-geometry-at-load.md) — the extent sanity check that catches a swapped pair.
- [`../skills/serve-vector-tiles/SKILL.md`](../skills/serve-vector-tiles/SKILL.md) — GeoJSON as a serving format (and when to leave it for MVT).
- [`../knowledge/geospatial-stack-2026.md`](../knowledge/geospatial-stack-2026.md) — the GeoJSON / RFC 7946 row in the formats reference.

## Provenance

Codifies the `mapping-visualization-engineer` correctness opinion that a mis-placed map is usually a coordinate-order or projection bug ([`../CLAUDE.md`](../CLAUDE.md) §4). Grounded in RFC 7946 (The GeoJSON Format — coordinate order, CRS, winding), retrieved 2026-06-22.

---

_Last reviewed: 2026-06-22 by `claude`_
