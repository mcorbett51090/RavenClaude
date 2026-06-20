# Store exactly one known SRID per geometry column

**Status:** Absolute rule
**Domain:** CRS / data modeling
**Applies to:** `geospatial-gis-engineering`

---

## Why this exists

A geometry column with an unknown SRID (`0`) or a mix of SRIDs is a silent correctness bug: spatial predicates either error or — worse — compare coordinates as if they share a CRS when they don't, putting features in the wrong place and distances off by orders of magnitude. Pinning one declared SRID per column makes every downstream query, join, and reprojection unambiguous.

## How to apply

```sql
-- Good: the type modifier enforces geometry kind AND SRID
CREATE TABLE parcels (
  id   BIGSERIAL PRIMARY KEY,
  geom geometry(MultiPolygon, 4326) NOT NULL   -- one known CRS, checked by Postgres
);

-- Check what you actually have
SELECT DISTINCT ST_SRID(geom) FROM parcels;     -- should be exactly {4326}
```

**Do:**
- Use a typmod (`geometry(Point, 4326)` / `geography(Point, 4326)`) so the database rejects the wrong SRID.
- Pick the canonical SRID once (4326 by default) and document it.

**Don't:**
- Leave columns as bare `geometry` with SRID `0`.
- Mix SRIDs in one column "to save a reproject" — reproject on read instead.

## Edge cases / when the rule does NOT apply

A staging/ingest table may temporarily hold raw geometry before SRID assignment — but it sets the SRID (`ST_SetSRID`/`ST_Transform`) before the data becomes queryable.

## See also

- [`./reproject-on-read-store-once.md`](./reproject-on-read-store-once.md)
- [`../skills/design-coordinate-reference-system/SKILL.md`](../skills/design-coordinate-reference-system/SKILL.md)

## Provenance

PostGIS documentation (typmod columns, `ST_SRID`/`ST_SetSRID`); EPSG registry. Codifies the `gis-architect` CRS discipline.

---

_Last reviewed: 2026-06-20 by `claude`_
