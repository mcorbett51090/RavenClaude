# Tile / Map-Serving Plan — <layer>

> Output template for `geospatial-app-engineer` + `gis-architect` for getting a layer onto a web map performantly.

## Layer profile
- **Feature count:** _approx_
- **Update cadence:** _static / hourly / live_
- **Type:** _points / lines / polygons / imagery_
- **Zoom range:** _min–max_

## Format decision
- **Format:** _GeoJSON / vector tiles (MVT) / raster tiles_ — _why (count + cadence)_

## Serving
- **Source:** _PostGIS ST_AsMVT via pg_tileserv/martin / pre-rendered PMTiles-MBTiles via tippecanoe / COG via TiTiler_
- **Pre-rendered vs on-the-fly:** _decision tied to update cadence_
- **Hosting:** _tile server / object storage + CDN_

## Client rendering
- **Library:** _MapLibre GL / Leaflet / deck.gl_ — _why_
- **Performance:** _viewport-bound fetch, clustering, per-zoom simplification (tolerance)_
- **Interaction:** _feature-state hover/select, data-driven styling on the tile_

## Correctness & licensing
- _GeoJSON [lon, lat] confirmed; display CRS 3857; basemap attribution + usage terms named._

## Seams
- _Spatial SQL/tile generation → spatial-data-engineer · App shell/perf budget → frontend-engineering · Cartographic design → web-design_

---
_Plus the ravenclaude-core Structured Output block._
