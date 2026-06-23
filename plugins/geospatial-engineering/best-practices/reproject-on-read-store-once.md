# Reproject on read, store geometry once

**Status:** Absolute rule
**Domain:** CRS / data modeling
**Applies to:** `geospatial-engineering`

---

## Why this exists

Keeping a separate geometry column for every CRS you display in (one for 4326, one for 3857, …) means every write has to update them all in lockstep — and the moment one update is missed, the columns disagree and the bug is invisible until a map renders wrong. Storing a **single canonical SRID** and reprojecting at read time (`ST_Transform`) keeps one source of truth. It is the corollary of the explicit-SRID rule: one declared SRID per column means *one* column, not a fleet of CRS-shadow copies.

## How to apply

```sql
-- Store canonical 4326; reproject for the web map at read time
SELECT id, ST_AsMVTGeom(ST_Transform(geom, 3857), :bbox) AS geom
FROM roads
WHERE ST_Intersects(geom, ST_Transform(:bbox, 4326));
```

**Do:**
- Store one canonical SRID (4326 by default; a projected CRS if one dominates every query).
- `ST_Transform` on read for display / analysis CRSs.
- Cache or pre-render tiles if the reproject-on-read cost is hot.

**Don't:**
- Maintain duplicate geometry columns per CRS in application tables.

## Edge cases / when the rule does NOT apply

A read-heavy analytics table where one projected CRS dominates every query may store *in* that projected CRS — still one canonical SRID, just not 4326. The rule is "one canonical column," not "always 4326."

## See also

- [`./always-store-an-srid.md`](./always-store-an-srid.md) — the one-SRID-per-column rule this builds on.
- [`./never-compute-area-in-web-mercator.md`](./never-compute-area-in-web-mercator.md) — what you `ST_Transform` *to* depends on the operation.
- [`../knowledge/projection-decision-tree.md`](../knowledge/projection-decision-tree.md) — choosing the canonical and the read-time CRS.

## Provenance

Codifies the `geospatial-engineering` house opinion "pick the CRS before the columns" and "CRS hygiene through every pipeline hop" ([`../CLAUDE.md`](../CLAUDE.md) §3). Grounded in PostGIS `ST_Transform` / PROJ and standard CRS-management practice, retrieved 2026-06-22.

---

_Last reviewed: 2026-06-22 by `claude`_
