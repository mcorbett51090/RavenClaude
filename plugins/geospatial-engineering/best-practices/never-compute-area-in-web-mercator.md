# Never compute area (or true distance) in Web Mercator

**Status:** Absolute rule
**Domain:** CRS / spatial SQL
**Applies to:** `geospatial-engineering`

---

## Why this exists

EPSG:3857 (Web Mercator) is a conformal projection tuned for tiling: it preserves shape locally but grossly distorts area and distance away from the equator (Greenland looks larger than Africa). Computing `ST_Area` / `ST_Length` in 3857 yields numbers that can be wrong by a factor of several. **Web Mercator is for rendering tiles, not for measurement** — it sits at the *display* leaf of the projection decision tree, never the *measurement* leaf. The companion trap to the degree-distance bug (`geometry(…, 4326)` distances are degrees): here the units are metres but the projection lies about how many.

## How to apply

```sql
-- Wrong: area in Web Mercator (badly distorted)
SELECT ST_Area(ST_Transform(geom, 3857)) FROM lakes;          -- DO NOT

-- Right: area via geography (m²) or a local projected CRS
SELECT ST_Area(geom::geography) FROM lakes;                    -- m², correct
SELECT ST_Area(ST_Transform(geom, 32630)) FROM lakes;         -- UTM zone, m²
```

**Do:**
- Measure in `geography` (m²/m) or an appropriate projected CRS (UTM / state-plane / national grid).
- Reserve 3857 for tile generation and display.

**Don't:**
- Report any area or length computed in 3857.

## Edge cases / when the rule does NOT apply

Relative comparisons at a single latitude over a tiny extent can tolerate Mercator distortion, but it's never worth the foot-gun — use the correct CRS.

## See also

- [`../knowledge/projection-decision-tree.md`](../knowledge/projection-decision-tree.md) — 3857 is the display leaf; measure in geography / a projected CRS.
- [`./always-store-an-srid.md`](./always-store-an-srid.md) — the companion units-correctness rule (degree distances).
- [`../skills/write-spatial-query/SKILL.md`](../skills/write-spatial-query/SKILL.md) — the units fix in query form.

## Provenance

Codifies the `geospatial-engineering` house opinions "never measure distance or area in 3857" and "distances in degrees are a bug" ([`../CLAUDE.md`](../CLAUDE.md) §3, §4). The advisory hook [`../hooks/flag-geo-smells.sh`](../hooks/flag-geo-smells.sh) flags an `ST_Area`/`ST_Length` computed in 3857. Grounded in projection theory (Mercator area distortion) and PostGIS CRS documentation, retrieved 2026-06-22.

---

_Last reviewed: 2026-06-22 by `claude`_
