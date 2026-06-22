---
name: serve-vector-tiles
description: "Serve geospatial data to a web map — decide GeoJSON vs vector tiles (MVT) by feature count and zoom, stand up a tile server (pg_tileserv / Martin / Tegola or MBTiles), and wire the MapLibre source + layer to consume it. Reach for this when a map is slow, you have many features, or you need a tile-serving architecture. Used by `mapping-visualization-engineer` (primary)."
---

# Skill: serve-vector-tiles

> **Invoked by:** `mapping-visualization-engineer` (primary). Routes the source schema/index questions to `geospatial-data-engineer`.
>
> **When to invoke:** "how do I serve N features?"; "my map is slow / blank"; "vector tiles or GeoJSON?"; standing up any tile-serving layer.
>
> **Output:** the format decision (GeoJSON vs MVT, by size/zoom) + a tile-server recipe + the MapLibre source/layer style to consume it, in EPSG:3857.

## Procedure

1. **Make the format decision first.** Count features and consider zoom interactivity:
   - **≲ a few hundred static features, no per-zoom simplification** → ship **GeoJSON** directly to MapLibre (simple, no server).
   - **thousands → millions, or zoom-dependent, or restyleable** → **vector tiles (MVT)** from a tile server.
   - **true imagery / heavy cartography** → **raster tiles** (XYZ/WMTS).
2. **Pick the tile server.** PostGIS-backed dynamic tiles → **pg_tileserv** (zero-config, table-driven) or **Martin** (fast, Rust, config-driven); pre-generated tiles → **Tegola** or an **MBTiles** file served by a static tile host.
3. **Guarantee the projection.** Web tiles are **EPSG:3857**. The server runs `ST_AsMVT(ST_AsMVTGeom(ST_Transform(geom, 3857), tile_bbox))` — reproject from the source SRID and clip to the tile. A mismatch = a blank or mis-placed map.
4. **Simplify per zoom.** `ST_SimplifyPreserveTopology` or tile-level `ST_AsMVTGeom` clipping keeps tiles small; don't ship z18 detail at z3.
5. **Wire the MapLibre source + layer.** Add a `vector` source pointing at the `{z}/{x}/{y}` tile URL, then a layer naming the `source-layer`, with zoom-dependent paint.

## Worked example

> User: "I have 400k parcels in PostGIS and a MapLibre map that hangs. How do I serve them?"

- 400k features → **vector tiles**, not GeoJSON. Use pg_tileserv over the indexed source table; reproject to 3857 in the tile query.

```json
// MapLibre style fragment — consume the vector-tile source
{
  "sources": {
    "parcels": {
      "type": "vector",
      "tiles": ["https://tiles.example.com/public.parcel/{z}/{x}/{y}.pbf"],
      "minzoom": 0, "maxzoom": 16
    }
  },
  "layers": [
    {
      "id": "parcel-fill",
      "type": "fill",
      "source": "parcels",
      "source-layer": "public.parcel",
      "paint": {
        "fill-opacity": ["interpolate", ["linear"], ["zoom"], 10, 0, 13, 0.4]
      }
    }
  ]
}
```

The pg_tileserv source query (run by the server) must `ST_Transform(geom, 3857)` and rely on the table's GiST index for the bbox filter — route that schema/index work to [`../../agents/geospatial-data-engineer.md`](../../agents/geospatial-data-engineer.md).

## Guardrails
- Never ship a multi-megabyte GeoJSON to the browser when feature count says vector tiles — that is the #1 slow-map cause.
- Tiles are 3857: a source in 4326 must be `ST_Transform`ed in the tile query, or the map is blank/mis-placed.
- A `source-layer` name mismatch produces an empty layer with no error — check it first when a styled layer doesn't render. See [`../../best-practices/vector-tiles-over-geojson-at-scale.md`](../../best-practices/vector-tiles-over-geojson-at-scale.md) and [`../../templates/tile-serving-architecture.md`](../../templates/tile-serving-architecture.md).
