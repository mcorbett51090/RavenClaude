# Geospatial-engineering — best-practice docs

Named, citable rules for the `geospatial-engineering` plugin's two agents. Each file is **one rule**, grounded in the plugin's knowledge bank and the agents' house opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md)) or the automated smell checks in the advisory hook. They take one opinion each and make it a standalone, exception-documented rule.

---

## Index

_3 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`always-store-an-srid.md`](./always-store-an-srid.md) | Absolute rule | Creating or reviewing any geometry/geography column — declare an explicit SRID, never bare `geometry`, and never quote a `geometry(…, 4326)` distance as metres. |
| [`index-geometry-with-gist.md`](./index-geometry-with-gist.md) | Absolute rule | Building or optimizing a spatial table/query — add a GiST index and use index-aware operators (`ST_DWithin`, `<->`), not `ST_Distance(...) < d`. |
| [`vector-tiles-over-geojson-at-scale.md`](./vector-tiles-over-geojson-at-scale.md) | Pattern (strong default; deviate only with a written reason) | Choosing a serving format for a web map — pick vector tiles vs GeoJSON vs raster by feature count and zoom, not by reflex. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — geospatial-engineering team constitution (house opinions, anti-patterns, Output Contracts, smell hook).
- [`../knowledge/projection-decision-tree.md`](../knowledge/projection-decision-tree.md) — the CRS + geometry-vs-geography decision tree the SRID rule leans on.
- [`../knowledge/geospatial-stack-2026.md`](../knowledge/geospatial-stack-2026.md) — the tiered 2026 tooling reference.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs and the `_TEMPLATE.md` these follow.
