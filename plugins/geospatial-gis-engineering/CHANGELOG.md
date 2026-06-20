# Changelog — geospatial-gis-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-20

Initial release.

### Added

- **3 agents** — `gis-architect` (storage / CRS / serving-topology decisions), `spatial-data-engineer` (correct + fast spatial SQL, validity, reprojection, loading), `geospatial-app-engineer` (web-map rendering, format choice, coordinate correctness).
- **5 skills** — `choose-spatial-storage`, `design-coordinate-reference-system`, `write-spatial-queries`, `build-map-tiles-and-serving`, `spatial-data-quality`.
- **Knowledge bank** — `geospatial-decision-trees.md` (4 Mermaid trees: storage, CRS, geometry-vs-geography, web-serving format) and `geospatial-stack-2026.md` (dated capability map; re-verify versions before quoting).
- **10 best-practices** — one canonical SRID per column, reproject-on-read, geography for lon/lat distance, never area in Web Mercator, always a spatial index, ST_DWithin over ST_Distance, validate geometry at load, GeoJSON is [lon, lat], tile large layers, simplify per zoom.
- **3 templates** — spatial-schema-design, crs-decision, tile-pipeline-plan.
- **3 commands** — `/design-spatial-schema`, `/choose-crs`, `/review-geospatial`.
- **1 advisory hook** — `check-geospatial-anti-patterns.sh` (4 checks; `GEOENG_STRICT=1` to block).

### Verify-at-use

- All product/library versions and capabilities in `geospatial-stack-2026.md` (PostGIS, BigQuery GIS, MapLibre, tippecanoe/PMTiles, pg_tileserv/martin, GDAL/PROJ) — volatile; re-confirm against the vendor/project before quoting. EPSG codes resolve against epsg.io.
