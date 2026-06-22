# Tile-serving architecture — <map / dataset name>

> Fill this in **before** standing up the serving layer. The format decision (GeoJSON
> vs vector tiles vs raster) is the whole game — make it explicitly by feature count
> and zoom, then wire the server and the MapLibre style to match.

**Author:** <name> · **Date:** <YYYY-MM-DD> · **Source table:** <PostGIS table + its SRID>

## 1. The data on the map
- **Feature count:** <N> · **Geometry:** <points / lines / polygons>
- **Zoom range:** <min>–<max> · **Interactive / restyleable?** <yes / no>
- **Imagery or vector data?** <vector (restyleable) / raster (imagery)>

## 2. Format decision
- **Chosen format:** <GeoJSON (≲ few hundred static) | vector tiles / MVT (thousands–millions, zoom-dependent) | raster tiles (imagery)>
- **Why:** <one line tied to feature count + zoom + interactivity>

## 3. Serving layer
- **Tile server:** <pg_tileserv (zero-config from PostGIS) | Martin | Tegola | static MBTiles/PMTiles>
- **Tile URL contract:** `https://<host>/<source>/{z}/{x}/{y}.pbf`
- **Source-layer name:** <e.g. `public.parcel`> (must match the MapLibre layer's `source-layer`)
- **Projection:** tiles in **EPSG:3857** — source `ST_Transform(geom, 3857)` from <source SRID>
- **Simplification:** <`ST_SimplifyPreserveTopology` / `ST_AsMVTGeom` clipping per zoom>
- **Index relied on:** <GiST on the source `geom` — route to geospatial-data-engineer if missing>

## 4. MapLibre client wiring
```json
{
  "sources": {
    "<src>": {
      "type": "vector",
      "tiles": ["https://<host>/<source>/{z}/{x}/{y}.pbf"],
      "minzoom": <min>, "maxzoom": <max>
    }
  },
  "layers": [
    {
      "id": "<layer-id>",
      "type": "<fill|line|circle|symbol>",
      "source": "<src>",
      "source-layer": "<source-layer name — must match the server>",
      "paint": { "<zoom-dependent paint expressions>": "…" }
    }
  ]
}
```

## 5. Failure-mode checklist
- **Blank map?** → projection mismatch (source not 3857) or wrong `source-layer` name.
- **Slow map?** → GeoJSON where vector tiles belong, or over-dense geometry (no per-zoom simplification).
- **Empty layer, no error?** → `source-layer` name does not match the server's layer.

## 6. Seams
- **Source schema / index / `ST_` query** → `geospatial-data-engineer`.
- **Surrounding UI chrome / CSS / layout** → `frontend-engineering` / `web-design`.
