# CRS decision record — <project / layer>

> A standalone record for the coordinate-reference-system choice — one per layer / dataset
> where it isn't obvious. Lighter than the full spatial-data-model template: when the schema
> is settled and only the CRS call needs writing down, use this. Traverse the projection
> decision tree first.

**Author:** <name> · **Date:** <YYYY-MM-DD>

## 1. Context
- **Data:** <what the geometry represents>
- **Primary use:** <storage / interchange / display tiles / distance / area>
- **Geographic extent:** <local / regional / national / global>

## 2. Decision (from the projection decision tree)
- **Canonical storage SRID:** EPSG:<____> · **Why:** <one line tied to the job>
- **Display / tile CRS:** EPSG:3857 (reproject on read) — if served on a web map
- **Measurement CRS / type:** <`geography` on 4326 | UTM zone EPSG:<____> | national grid EPSG:<____>>
- **geometry vs geography:** <which, and why>

## 3. What we explicitly will NOT do
- <e.g. "no area math in 3857"; "no distance in degrees on `geometry(…, 4326)`">

## 4. Enforcement
- Typmod on the column (`geometry(<Type>, <SRID>)`); SRID set on ingest; `ST_Transform` on read (store once).

## 5. Re-verify
- Any EPSG code or transform looked up against epsg.io on <date> — `[unverified — region-specific]` until confirmed.

## 6. Seams
- **Schema / DDL / index** → `geospatial-data-engineer` (`design-postgis-schema`).
- **Served on a map?** → `mapping-visualization-engineer`.

---
_Plus the ravenclaude-core Structured Output block._
