---
name: design-postgis-schema
description: Design a PostGIS table for spatial data — pick the CRS (SRID) and geometry-vs-geography type by use-case, declare the column with an explicit SRID, add the right GiST/SP-GiST spatial index, and emit a runnable CREATE TABLE + index. Reach for this when the user wants to store points/lines/polygons in PostGIS and asks "which SRID?" or "geometry or geography?". Used by `geospatial-data-engineer` (primary).
---

# Skill: design-postgis-schema

> **Invoked by:** `geospatial-data-engineer` (primary). Also consulted by `write-spatial-query` when a query exposes a missing SRID or index.
>
> **When to invoke:** "model this in PostGIS"; "which SRID do I use?"; "geometry or geography?"; storing any points / lines / polygons.
>
> **Output:** an explicit SRID + a geometry-vs-geography decision + a GiST/SP-GiST index + a runnable `CREATE TABLE` and `CREATE INDEX`, with the projection rationale.

## Procedure

1. **Pick the CRS first.** Traverse [`../../knowledge/projection-decision-tree.md`](../../knowledge/projection-decision-tree.md) against the use-case:
   - serving a web map → **EPSG:3857** (Web Mercator);
   - global storage / long-distance true distances → **EPSG:4326 `geography`**;
   - local metric accuracy (a city, a county) → the local **UTM zone** or **state-plane** SRID.
2. **Decide geometry vs geography.** `geography` for true-metre distances over large extents (slower, spheroidal); projected `geometry` for fast planar work in a metric CRS. Name which and why.
3. **Declare the column with an explicit SRID** — `geometry(Point, 4326)`, never bare `geometry`. Pick the geometry subtype (Point / LineString / Polygon / Multi…) to match the data.
4. **Add the spatial index.** `CREATE INDEX … USING GIST (geom);` for general spatial data; consider SP-GiST for point-only clustered data. The index is not optional.
5. **Emit the runnable DDL** + a `SELECT Find_SRID(...)` or `ST_SRID(geom)` validation the user can run to confirm the SRID landed.

## Worked example

> User: "I'm storing delivery stops (lat/long points) and querying 'stops within 5 km'. How do I model it?"

- Use-case = true-metre proximity over possibly wide extents → store as **`geography`** in **EPSG:4326** so `ST_DWithin(geog, geog, 5000)` is metres directly.
- (If it were a single city and speed mattered, a projected UTM `geometry` would be exact and faster — note the tradeoff.)

```sql
CREATE TABLE delivery_stop (
    id        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    label     text NOT NULL,
    geog      geography(Point, 4326) NOT NULL   -- explicit SRID; geography = true metres
);

CREATE INDEX delivery_stop_geog_gix ON delivery_stop USING GIST (geog);

-- validate the SRID landed
SELECT id, ST_SRID(geog::geometry) FROM delivery_stop LIMIT 1;   -- expect 4326
```

## Guardrails
- Never declare a bare `geometry` / `geometry(Point)` with no SRID — it silently mixes coordinate systems (the hook flags this).
- Never ship a spatial table without a GiST (or SP-GiST) index — it forces a sequential scan (the hook flags an indexless join).
- If distances must be in metres, prefer `geography` or a projected metric CRS — `geometry(…, 4326)` distances are degrees. See [`../write-spatial-query/SKILL.md`](../write-spatial-query/SKILL.md) and [`../../best-practices/always-store-an-srid.md`](../../best-practices/always-store-an-srid.md).
