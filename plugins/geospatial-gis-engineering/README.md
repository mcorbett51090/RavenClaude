# geospatial-gis-engineering

A RavenClaude plugin: a **geospatial / GIS engineering** specialist team for building location-aware systems that are correct, fast, and scalable — the storage decision, coordinate reference systems, spatial SQL, and map serving.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

## What it's for

Adding maps, location features, or spatial analytics to a product and wanting them done right: where the data lives, what coordinate system it's in, queries that use the index, and a map that stays smooth as the data grows. PostGIS-leaning; principles port to BigQuery GIS / Snowflake / GeoParquet.

## Agents

| Agent | Use for |
|---|---|
| **gis-architect** | Storage choice (PostGIS vs geospatial warehouse vs tile/feature service), CRS/SRID, map-serving topology |
| **spatial-data-engineer** | Correct + fast spatial SQL (ST_DWithin, KNN, spatial joins), geometry validity, reprojection, data loading |
| **geospatial-app-engineer** | Web-map rendering (MapLibre/Leaflet), GeoJSON vs vector tiles vs raster, client performance, coordinate correctness |

## What's inside

- **5 skills** — choose-spatial-storage, design-coordinate-reference-system, write-spatial-queries, build-map-tiles-and-serving, spatial-data-quality.
- **Knowledge bank** — [`geospatial-decision-trees.md`](knowledge/geospatial-decision-trees.md) (4 Mermaid trees: storage, CRS, geometry-vs-geography, web-serving format) + [`geospatial-stack-2026.md`](knowledge/geospatial-stack-2026.md) (dated capability map).
- **10 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **3 templates** — spatial schema design, CRS decision record, tile-pipeline plan.
- **3 commands** — `/design-spatial-schema`, `/choose-crs`, `/review-geospatial`.
- **1 advisory hook** — `check-geospatial-anti-patterns.sh` (non-sargable distance filter, area-in-3857, unknown SRID, no-typmod column). `GEOENG_STRICT=1` to block.

## Seams

OLTP schema / generic tuning → [`database-engineering`](../database-engineering/) · warehouse/ELT → [`data-platform`](../data-platform/) · app shell / map UI → [`frontend-engineering`](../frontend-engineering/) · cartographic design → [`web-design`](../web-design/) · vehicle routing → [`fleet-logistics`](../fleet-logistics/) · agronomic layers → [`precision-agriculture`](../precision-agriculture/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install geospatial-gis-engineering@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for routing rules, house opinions, and the output contract.
