# geospatial-gis-engineering — best-practice docs

Named, citable rules for the `geospatial-gis-engineering` plugin's specialists. Each file is **one rule**.

---

## Index

_10 rules across CRS, spatial SQL, storage, and map serving._

| Doc | Status | Use when |
|---|---|---|
| [`store-one-canonical-srid-per-column.md`](./store-one-canonical-srid-per-column.md) | Absolute rule | Every geometry column — exactly one known SRID, enforced by a typmod; never SRID 0. |
| [`reproject-on-read-store-once.md`](./reproject-on-read-store-once.md) | Absolute rule | Needing another CRS — `ST_Transform` on read; don't keep duplicate geometry columns. |
| [`geography-for-lonlat-distance.md`](./geography-for-lonlat-distance.md) | Pattern | "Near me" / distance on lon/lat — use the `geography` type for correct spheroidal distance. |
| [`never-compute-area-in-web-mercator.md`](./never-compute-area-in-web-mercator.md) | Absolute rule | Any area/length math — never in EPSG:3857; use a projected CRS or `geography`. |
| [`always-add-a-spatial-index.md`](./always-add-a-spatial-index.md) | Absolute rule | Any spatially-filtered/joined column — add a GiST index and verify it's used. |
| [`use-st-dwithin-not-st-distance.md`](./use-st-dwithin-not-st-distance.md) | Absolute rule | Filtering by distance — `ST_DWithin` (index-using), not `ST_Distance < d`. |
| [`validate-geometry-at-load.md`](./validate-geometry-at-load.md) | Absolute rule | Loading spatial data — `ST_IsValid`/`ST_MakeValid` at the boundary, not after it breaks. |
| [`geojson-is-lon-lat.md`](./geojson-is-lon-lat.md) | Absolute rule | Any GeoJSON — coordinates are `[longitude, latitude]` (RFC 7946), WGS84, right-hand winding. |
| [`tile-large-layers-dont-ship-giant-geojson.md`](./tile-large-layers-dont-ship-giant-geojson.md) | Pattern | Large web map layers — vector tiles, not a multi-MB GeoJSON or N DOM markers. |
| [`simplify-per-zoom.md`](./simplify-per-zoom.md) | Pattern | Tiling/rendering — generalize geometry per zoom level deliberately, naming the tolerance. |

---

Each rule cites its provenance and carries a `Last reviewed` date. Volatile tooling specifics live in [`../knowledge/geospatial-stack-2026.md`](../knowledge/geospatial-stack-2026.md).
