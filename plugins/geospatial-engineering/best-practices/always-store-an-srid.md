# Always store an explicit SRID on every geometry/geography column

**Status:** Absolute rule
**Domain:** Spatial data modeling / coordinate-system hygiene
**Applies to:** `geospatial-engineering`

---

## Why this exists

A column declared `geometry` or `geometry(Point)` with **no SRID** is unconstrained: PostGIS will accept coordinates from *any* coordinate system into the same column and report `ST_SRID = 0` ("unknown"). Two rows that look identical may be lon/lat and metres-in-a-projection — and a join, a distance, or a reprojection across them silently produces nonsense, with no error. The SRID is **part of the data, not metadata you bolt on later**: it tells every function what the numbers *mean*. Declare it on the column (`geometry(Point, 4326)`), and a mismatched insert is rejected at write time instead of corrupting an analysis weeks later.

A second, equally common failure rides on this rule: measuring distance in `geometry(…, 4326)`, whose units are **degrees**, not metres — a number that is meaningless on the ground. Storing the SRID is what lets you *see* that you are in 4326 and cast to `geography` or reproject before measuring.

## How to apply

Pick the SRID from the projection decision tree, then declare it explicitly and validate it landed:

```sql
-- DO: explicit SRID on the column
geom geometry(Point, 4326) NOT NULL        -- or geography(Point, 4326) for true metres

-- validate after load
SELECT DISTINCT ST_SRID(geom) FROM my_table;   -- must be your SRID, never 0
```

**Do:**
- Declare the SRID in the column type for every geometry/geography column.
- Validate `ST_SRID` is your intended SRID (never 0) after any load.
- Cast to `geography` or `ST_Transform` to a metric CRS before reporting a distance — `geometry(…, 4326)` distances are degrees.

**Don't:**
- Declare a bare `geometry` / `geometry(Point)` and "add the SRID later."
- Compare or join two geometries with different SRIDs without `ST_Transform`.
- Quote a distance from `geometry(…, 4326)` as if it were metres.

## Edge cases / when the rule does NOT apply

- **Intentionally CRS-agnostic local coordinates** (e.g. a game/floorplan grid with no Earth datum) legitimately use SRID 0 — but document *why*, so SRID 0 is a decision, not an accident.
- **Mixed-SRID staging tables** during a migration may briefly hold raw input — but the target table always carries an explicit SRID, and the transform happens on the way in.

## See also

- [`../knowledge/projection-decision-tree.md`](../knowledge/projection-decision-tree.md) — pick the SRID + geometry-vs-geography type by use-case.
- [`./index-geometry-with-gist.md`](./index-geometry-with-gist.md) — the companion rule that makes the SRID-correct table fast.
- [`../skills/design-postgis-schema/SKILL.md`](../skills/design-postgis-schema/SKILL.md) — the schema-design procedure that applies this rule.

## Provenance

Codifies the `geospatial-data-engineer` house opinion "the SRID is part of the data, not metadata you add later" ([`../CLAUDE.md`](../CLAUDE.md)). The advisory hook [`../hooks/flag-geo-smells.sh`](../hooks/flag-geo-smells.sh) flags a geometry column created with no SRID and degree-distance smells. Grounded in PostGIS documentation (geometry SRID constraints; geometry vs geography), retrieved 2026-06-17.

---

_Last reviewed: 2026-06-17 by `claude`_
