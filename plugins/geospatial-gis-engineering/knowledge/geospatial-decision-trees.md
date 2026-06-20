# Geospatial / GIS — Decision Trees

> Reference decision trees for the `geospatial-gis-engineering` team. Agents **traverse the relevant tree top-to-bottom before choosing** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> _Last reviewed: 2026-06-20 by `claude`. Principles are durable; specific product/library names live (dated) in [`geospatial-stack-2026.md`](geospatial-stack-2026.md)._

---

## Decision Tree: where should spatial data live?

```mermaid
flowchart TD
    A[Spatial data to store] --> B{Transactional?<br/>CRUD + low-latency reads}
    B -- yes --> C{Volume per query}
    C -- "moderate (≤10⁷ rows scanned)" --> D[PostGIS<br/>GiST index, full spatial SQL]
    C -- "huge (10⁸–10⁹+)" --> E{Need single-feature CRUD?}
    E -- yes --> F[PostGIS hot table<br/>+ warehouse for analytics]
    E -- no --> G[Geospatial warehouse<br/>BigQuery GIS / Snowflake / GeoParquet]
    B -- no --> H{Mostly-read, large or static?}
    H -- "yes (basemaps, big layers)" --> I[Tile / feature service<br/>pre-rendered MVT/raster pyramid]
    H -- "analytics only" --> G
```

**Rule:** name the workload first. Transactional + moderate → PostGIS; analytics at scale → a geospatial warehouse; mostly-read large/static → a tile/feature service. Don't use a warehouse as a map backend or PostGIS as a billion-point scanner.

---

## Decision Tree: which coordinate reference system (CRS)?

```mermaid
flowchart TD
    A[Choosing a CRS] --> B{Primary use}
    B -- "storage / interchange" --> C[EPSG:4326 WGS84<br/>lon/lat default]
    B -- "web map tiles / display" --> D[EPSG:3857 Web Mercator<br/>display only — never area]
    B -- "accurate distance / area" --> E{Extent}
    E -- "local / regional" --> F[UTM zone<br/>EPSG:326xx/327xx]
    E -- "national" --> G[National grid<br/>e.g. 27700, 25831]
    B -- "distance on lon/lat, no projecting" --> H[geography type on 4326]
```

**Rule:** store 4326 by default; reproject on read. Project to a metric CRS (UTM/national grid) only for true distance/area math, or use the `geography` type. Web Mercator is for tiles, never for area.

---

## Decision Tree: geometry vs geography column type

```mermaid
flowchart TD
    A[Picking a column type] --> B{Need correct distance/area<br/>over large lon/lat extents?}
    B -- yes --> C{Hot-path performance critical?}
    C -- no --> D[geography on 4326<br/>spheroidal, correct, simpler]
    C -- yes --> E[geometry in a projected CRS<br/>fast planar math]
    B -- no --> F{Mostly local extent?}
    F -- yes --> E
    F -- no --> D
```

**Rule:** `geography` when correctness on lon/lat over big extents matters and you can afford it; `geometry` (projected) when you need speed or area/length math. Decide per column, profile before optimizing.

---

## Decision Tree: serve features to a web map as…?

```mermaid
flowchart TD
    A[Layer to render] --> B{Feature count}
    B -- "small (≲ few thousand)" --> C{Changes often?}
    C -- yes --> D[GeoJSON to client]
    C -- no --> E[GeoJSON or small MVT]
    B -- "large" --> F{Imagery or heavy cartography?}
    F -- yes --> G[Raster tiles<br/>XYZ/WMTS pyramid]
    F -- no --> H{Updates often?}
    H -- yes --> I[On-the-fly vector tiles<br/>ST_AsMVT / pg_tileserv / martin]
    H -- no --> J[Pre-rendered MVT pyramid<br/>cheap CDN reads]
```

**Rule:** format follows feature count + cadence. Small/dynamic → GeoJSON; large/styleable → vector tiles (on-the-fly if it changes, pre-rendered if it doesn't); imagery → raster. Never ship a giant GeoJSON or render N DOM markers.

---

## See also

- [`geospatial-stack-2026.md`](geospatial-stack-2026.md) — dated tooling/library capability map (re-verify before quoting versions).
- Skills: [`../skills/choose-spatial-storage/SKILL.md`](../skills/choose-spatial-storage/SKILL.md), [`../skills/design-coordinate-reference-system/SKILL.md`](../skills/design-coordinate-reference-system/SKILL.md), [`../skills/write-spatial-queries/SKILL.md`](../skills/write-spatial-queries/SKILL.md), [`../skills/build-map-tiles-and-serving/SKILL.md`](../skills/build-map-tiles-and-serving/SKILL.md).
