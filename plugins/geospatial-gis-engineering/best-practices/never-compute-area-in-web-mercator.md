# Never compute area (or true distance) in Web Mercator

**Status:** Absolute rule
**Domain:** CRS / spatial SQL
**Applies to:** `geospatial-gis-engineering`

---

## Why this exists

EPSG:3857 (Web Mercator) is a conformal projection tuned for tiling: it preserves shape locally but grossly distorts area and distance away from the equator (Greenland looks larger than Africa). Computing `ST_Area`/`ST_Length` in 3857 yields numbers that can be wrong by a factor of several. Web Mercator is for *rendering tiles*, not for measurement.

## How to apply

```sql
-- Wrong: area in Web Mercator (badly distorted)
SELECT ST_Area(ST_Transform(geom, 3857)) FROM lakes;          -- DO NOT

-- Right: area via geography (m²) or a local projected CRS
SELECT ST_Area(geom::geography) FROM lakes;                    -- m², correct
SELECT ST_Area(ST_Transform(geom, 32630)) FROM lakes;         -- UTM zone, m²
```

**Do:**
- Measure in `geography` (m²/m) or an appropriate projected CRS (UTM/national grid).
- Reserve 3857 for tile generation/display.

**Don't:**
- Report any area/length computed in 3857.

## Edge cases / when the rule does NOT apply

Relative comparisons at a single latitude over a tiny extent can tolerate Mercator distortion, but it's never worth the footgun — use the correct CRS.

## See also

- [`./geography-for-lonlat-distance.md`](./geography-for-lonlat-distance.md)
- [`../skills/design-coordinate-reference-system/SKILL.md`](../skills/design-coordinate-reference-system/SKILL.md)

## Provenance

Projection theory (Mercator area distortion); PostGIS CRS docs. Codifies `gis-architect` house opinion.

---

_Last reviewed: 2026-06-20 by `claude`_
