# Use the geography type for distance on lon/lat

**Status:** Pattern
**Domain:** Spatial SQL
**Applies to:** `geospatial-gis-engineering`

---

## Why this exists

`geometry` computes planar (flat) math. Run a distance over lon/lat (degrees) stored as `geometry` and you get a "distance" in degrees — meaningless, and increasingly wrong as you move from the equator. The `geography` type computes correct spheroidal distances in metres on WGS84, which is what "find everything within 5 km" actually needs.

## How to apply

```sql
-- geography: distance in metres, correct on the sphere
SELECT * FROM stores
WHERE ST_DWithin(geog, ST_MakePoint(:lon,:lat)::geography, 5000);  -- 5 km
```

**Do:**
- Use `geography` for "near me" / distance / buffer over lon/lat across large extents.
- Keep `ST_DWithin` (index-using) as the filter.

**Don't:**
- Compare `ST_Distance` on raw 4326 `geometry` and treat the result as metres.

## Edge cases / when the rule does NOT apply

For a small local extent where performance is hot, projecting to a UTM `geometry` is faster than `geography` and accurate enough — profile and decide per column.

## See also

- [`./use-st-dwithin-not-st-distance.md`](./use-st-dwithin-not-st-distance.md)
- [`./never-compute-area-in-web-mercator.md`](./never-compute-area-in-web-mercator.md)

## Provenance

PostGIS geography type documentation. Codifies `spatial-data-engineer` discipline.

---

_Last reviewed: 2026-06-20 by `claude`_
