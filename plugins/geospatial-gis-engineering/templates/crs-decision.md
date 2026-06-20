# CRS Decision Record — <project / layer>

> Output template for the coordinate-reference-system choice. One per layer/dataset where it isn't obvious.

## Context
- **Data:** _what the geometry represents_
- **Primary use:** _storage / display tiles / distance / area_
- **Geographic extent:** _local / regional / national / global_

## Decision
- **Canonical storage SRID:** _EPSG:_____
- **Display/tile CRS:** _EPSG:3857 (reproject on read)_
- **Measurement CRS / type:** _geography on 4326, or UTM zone EPSG:____, or national grid EPSG:_____

## Rationale
- _Why this CRS for this use — accuracy vs interoperability vs tiling._
- _What we explicitly will NOT do (e.g. "no area math in 3857")._

## Enforcement
- _Typmod on the column; SRID set on ingest; ST_Transform on read._

## Re-verify
- _Any EPSG code or transform looked up against epsg.io on <date>._

---
_Plus the ravenclaude-core Structured Output block._
