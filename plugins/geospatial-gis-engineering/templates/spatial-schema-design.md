# Spatial Schema Design — <domain>

> Output template for `gis-architect` + `spatial-data-engineer`. Fill every section; delete the guidance in italics.

## Workload
- **Use:** _transactional map app / analytics / mostly-read service_
- **Volume:** _rows, features, growth rate_
- **Read pattern:** _e.g. "points within radius", "point-in-polygon", "nearest k", "viewport tiles"_

## Storage decision
- **Store:** _PostGIS / geospatial warehouse / tile-feature service_ — _why (tie to workload)_

## Coordinate reference system
- **Canonical SRID:** _EPSG:____ (default 4326)_
- **Reproject on read to:** _3857 for tiles / UTM for area / none_
- **geometry vs geography:** _per column, with reason_

## Schema (DDL)
```sql
CREATE TABLE <table> (
  id   BIGSERIAL PRIMARY KEY,
  geom geometry(<Type>, <SRID>) NOT NULL,
  -- attributes ...
  CONSTRAINT <table>_geom_valid CHECK (ST_IsValid(geom))
);
CREATE INDEX idx_<table>_geom ON <table> USING GIST (geom);
```

## Index plan
- _Which spatial columns get a GiST index; any composite/attribute indexes._

## Data quality gates
- _Validity (ST_IsValid), SRID enforcement, extent sanity, topology if needed._

## Seams handed off
- _Spatial SQL → spatial-data-engineer · Map UI → geospatial-app-engineer · OLTP → database-engineering · ELT → data-platform_

---
_Plus the ravenclaude-core Structured Output block._
