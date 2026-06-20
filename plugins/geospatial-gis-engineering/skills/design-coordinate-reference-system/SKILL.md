---
name: design-coordinate-reference-system
description: "Choose and manage coordinate reference systems: store in EPSG:4326 (WGS84 lon/lat) for interoperability vs a projected CRS (UTM, national grid, 3857) for accurate distance/area or tiling; set one known SRID per column; reproject on read with ST_Transform."
---

# Design the Coordinate Reference System (CRS)

A CRS bug is silent: data lands in the wrong place or distances/areas are wrong by a lot.

## The default and the exceptions
- **Store EPSG:4326 (WGS84, lon/lat)** as the interoperable default. GeoJSON, GPS, and most exchange formats are 4326.
- **Use a projected CRS** when you need true distance/area math (`geometry`) or you're rendering tiles:
  - **UTM zone** (e.g. EPSG:326xx/327xx) for accurate local metric work.
  - **A national grid** (e.g. EPSG:27700 British National Grid, EPSG:25831) where the data is national.
  - **Web Mercator EPSG:3857** for web tiles only — never compute area in it.

## Rules
1. **Exactly one known SRID per geometry column.** Unknown (`0`) or mixed SRID = latent bug. Enforce with a typmod (`geometry(Point, 4326)`).
2. **Match SRID before any spatial predicate** — `ST_Transform` the outlier, don't compare across CRSs.
3. **Reproject on read, store once.** `ST_Transform(geom, 3857)` for display; don't keep a duplicate column.
4. **For "near me" on lon/lat, prefer `geography`** (correct spheroidal distance) over reprojecting to compute distance.

## Quick reference
| Need | CRS |
|---|---|
| Interchange / storage default | 4326 |
| Web map tiles / display | 3857 |
| Accurate local distance & area | UTM zone or national grid |
| Correct distance on lon/lat without projecting | `geography` on 4326 |

Traverse the CRS tree in [`../../knowledge/geospatial-decision-trees.md`](../../knowledge/geospatial-decision-trees.md).
