---
name: write-spatial-query
description: Write or fix a spatial SQL query in PostGIS — spatial joins, nearest-neighbor (KNN), buffers, ST_DWithin proximity — so it uses the GiST index and returns sensible units. Reach for this when a query is slow, returns degrees, or you need an index-aware ST_ query. Diagnoses the common smells (no index, degrees-not-metres, SRID mismatch). Used by `geospatial-data-engineer` (primary).
---

# Skill: write-spatial-query

> **Invoked by:** `geospatial-data-engineer` (primary). Pairs with `design-postgis-schema` when a query reveals the schema is missing an SRID or index.
>
> **When to invoke:** "why is this spatial query slow?"; "this distance is in weird tiny numbers"; "nearest N features to a point"; "everything within X of Y"; any `ST_` query that needs to be index-aware.
>
> **Output:** an index-aware rewritten query (using `&&`, `<->`, `ST_DWithin`, geography casts) + the units fix + the index it relies on.

## Procedure

1. **Restate the spatial intent:** is it a *proximity filter* (within X), a *nearest-neighbor* (closest N), a *spatial join* (which polygon contains which point), or a *buffer/overlay*?
2. **Confirm the index path.** Index-aware operators use the GiST index; function calls on the raw geometry often don't:
   - proximity → **`ST_DWithin(a, b, d)`** (index-aware), not `ST_Distance(a, b) < d` (scans);
   - nearest-neighbor → the **`<->` KNN operator** in `ORDER BY a.geom <-> point LIMIT n` (index-assisted);
   - spatial join → **`ST_Intersects` / `ST_Contains`** with the bbox `&&` short-circuit the index provides.
3. **Fix the units.** `ST_Distance` / `ST_DWithin` on `geometry(…, 4326)` are in **degrees** — meaningless on the ground. Cast to `geography`, or reproject with `ST_Transform(geom, <metric SRID>)`, so the answer is metres.
4. **Match SRIDs.** Both operands must share an SRID; `ST_Transform` the odd one out, never compare across coordinate systems.
5. **Emit the runnable query** + an `EXPLAIN` hint so the user can confirm an *Index Scan*, not a *Seq Scan*.

## Worked example

> User: "Find the 5 nearest stores to a customer point — this is slow and the distances look like 0.0xx."

- "0.0xx" = degrees → the geometry is in 4326 planar; cast to `geography` for metres.
- "Slow" + nearest-N → use the `<->` KNN operator so the GiST index orders the candidates.

```sql
-- 5 nearest stores to a lon/lat point, distance in METRES, index-assisted
SELECT s.id,
       ST_Distance(s.geog, c.geog) AS metres
FROM   store s,
       (SELECT ST_MakePoint(-122.42, 37.77)::geography AS geog) c   -- lon, lat
ORDER  BY s.geog <-> c.geog          -- KNN operator → uses the GiST index
LIMIT  5;
-- run EXPLAIN (ANALYZE) and confirm an Index Scan on store_geog_gix, not a Seq Scan
```

## Guardrails
- Never write `ST_Distance(a, b) < d` for a proximity filter — use `ST_DWithin(a, b, d)` so the index applies.
- Never report a distance in degrees as if it were a real-world unit — cast to `geography` or reproject to metres (the hook flags degree-distance smells).
- Both geometries in any predicate must share an SRID — `ST_Transform` to align, never compare mismatched CRSs. See [`../../best-practices/always-store-an-srid.md`](../../best-practices/always-store-an-srid.md) and [`../../best-practices/index-geometry-with-gist.md`](../../best-practices/index-geometry-with-gist.md).
