# Geospatial-engineering Plugin — Team Constitution

> Team constitution for the `geospatial-engineering` Claude Code plugin. Two specialist agents — the **geospatial-data-engineer** and the **mapping-visualization-engineer** — plus a knowledge bank, skills, templates, best-practice rules, and an advisory hook, all aimed at one thing: **the engineering of location data** — making it correct, fast, queryable, and visible on a map.
>
> **Inherits `ravenclaude-core` protocols.** This file is **domain-specific** to geospatial/GIS work. For the domain-neutral team constitution inherited by every plugin (architect, coders, reviewers, project-manager, Capability Grounding Protocol, Structured Output Protocol, Claim Grounding), see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`geospatial-data-engineer`](agents/geospatial-data-engineer.md) | Spatial data modeling & storage (PostGIS, GiST/SP-GiST indexes, SRID/projection hygiene — 4326 vs 3857, geometry vs geography), spatial SQL & analysis (`ST_` functions, spatial joins, nearest-neighbor, buffers), geospatial pipelines (GDAL/OGR, geocoding, OSRM/Valhalla routing). CRS-before-columns; explicit SRID; GiST-indexed. | "which SRID?"; "geometry or geography?"; "why is this spatial query slow / in degrees?"; "load & reproject this with GDAL"; "geocode / route these" |
| [`mapping-visualization-engineer`](agents/mapping-visualization-engineer.md) | The serving & visualization layer — vector tiles/MVT, tile servers (pg_tileserv/Martin/Tegola), MapLibre/Mapbox GL styling, raster tiles, the GeoJSON-vs-vector-tile tradeoff. Format-by-size-and-zoom; tiles in 3857. | "how do I serve N features?"; "vector tiles or GeoJSON?"; "my MapLibre map is slow/blank/mis-projected"; "style these layers" |

Two agents is one coherent team split along the natural seam in geospatial work: **data correctness/performance in the database** vs **getting it onto a screen**. (Per the marketplace house rule, domain plugins may ship specialist *doing*-agents; they must not fork core's *review* roles — architect/security-reviewer. This plugin does neither.)

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates.

---

## 2. Routing rules (Team Lead)

- **"Model this in PostGIS" / "which SRID?" / "geometry or geography?"** → `geospatial-data-engineer` (drives `design-postgis-schema`).
- **"Why is this spatial query slow / in degrees?" / "nearest N" / "within X"** → `geospatial-data-engineer` (drives `write-spatial-query`).
- **"Load / reproject this dataset" / "geocode" / "route"** → `geospatial-data-engineer` (GDAL/OGR + routing-engine recipes).
- **"How do I serve N features?" / "vector tiles or GeoJSON?" / "my map is slow/blank"** → `mapping-visualization-engineer` (drives `serve-vector-tiles`).
- **"Style these layers in MapLibre"** → `mapping-visualization-engineer`.
- **Generic warehouse / ELT of non-spatial facts** → escalate to `data-platform` or `ravenclaude-core/data-engineer`.
- **Non-spatial OLTP schema (keys, normalization, migrations)** → `database-engineering`.
- **Surrounding map UI chrome / CSS / layout** → `frontend-engineering` / `web-design`.

**The seams** (this plugin = the engineering of location data):

| Adjacent concern | Owner |
|---|---|
| Generic warehouse / ELT of non-spatial facts | `data-platform` |
| Non-spatial OLTP schema craft | `database-engineering` |
| Map UI styling / component framework | `frontend-engineering` / `web-design` |
| Precision-agriculture / fleet-logistics | **consumers** of this layer, not part of it |

---

## 3. Cross-cutting house opinions (the agents enforce)

1. **Pick the CRS before the columns.** Traverse the projection decision tree; web map → 3857, global analysis → 4326 geography, local accuracy → UTM/state-plane.
2. **Every geometry/geography column carries an explicit SRID.** Never bare `geometry`; `geometry(Point, 4326)`. The SRID is part of the data.
3. **Geometry vs geography is a deliberate choice.** `geometry` = planar/fast/projection-units; `geography` = spheroidal/true-metres/slower. Name which and why.
4. **Index every spatial column with GiST before optimizing anything else.** An unindexed spatial join is a sequential scan.
5. **Distances in degrees are a bug.** `ST_Distance` on `geometry(…, 4326)` returns degrees — cast to `geography` or reproject to a metric CRS.
6. **Use index-aware operators.** `ST_DWithin` (not `ST_Distance < d`), `&&`, the `<->` KNN operator — or the index does nothing.
7. **CRS hygiene through every pipeline hop.** Assert source SRID, set target SRID, range-validate the result (GDAL/OGR, geocoding, routing).
8. **Serving format is chosen by feature count and zoom.** Vector tiles over GeoJSON at scale; raster for imagery; GeoJSON only for a few hundred static features.
9. **Web tiles are EPSG:3857.** A tile server over a 4326 source must `ST_Transform` to 3857 — a mismatch is a blank or mis-placed map.
10. **Volatile tooling claims carry a retrieval date** (PostGIS/GDAL/MapLibre/tile-server/routing-engine versions) and are re-verified before quoting to a client.

---

## 4. Anti-patterns the agents flag

- A geometry/geography column created with **no SRID** (the hook flags this).
- Reporting an `ST_Distance` on `geometry(…, 4326)` as metres — it is **degrees** (the hook flags this).
- An `ST_Distance(...) < d` proximity filter that **defeats the GiST index** instead of `ST_DWithin` (the hook flags this).
- A spatial table or join with **no GiST index** — a sequential scan at scale.
- Comparing or joining two geometries with **different SRIDs** without `ST_Transform`.
- Shipping a **multi-megabyte GeoJSON** to the browser where vector tiles belong.
- Serving vector tiles **not in 3857** (blank/mis-placed map) or with a mismatched `source-layer` name.
- Full-resolution geometry at low zoom — **no per-zoom simplification**.
- A GDAL/OGR load with **no source/target SRID asserted**.
- Quoting a PostGIS/GDAL/MapLibre/routing version with **no retrieval date**.

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before either agent says "I can't" or declares a result, it must:

1. **Check the 3 skills** (`design-postgis-schema`, `write-spatial-query`, `serve-vector-tiles`) plus core skills.
2. **Traverse the projection decision tree** ([`knowledge/projection-decision-tree.md`](knowledge/projection-decision-tree.md)) before selecting an SRID — don't keyword-match a CRS to the request.
3. **Try the next-easiest correct approach** before declaring blocked (e.g. `geography` cast before a full reprojection; geometry simplification before a full tiling pipeline).
4. **Escalate with the mandatory phrasing** — what was tried, what was ruled out, the recommended next path.

See the upstream protocol in [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 6. Output Contracts

Each agent ends every report with its Output Contract (full form in the agent file) plus the cross-plugin **Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)):

- **`geospatial-data-engineer`** — Question / CRS decision (SRID + geometry|geography + why) / Schema or query (runnable, index-aware) / Index / Units check / Pipeline hygiene / Verdict.
- **`mapping-visualization-engineer`** — Question / Format decision (GeoJSON|MVT|raster + why) / Serving (tile-server config) / Projection (3857) / Style (MapLibre source+layer) / Verdict.

---

## 7. Automated checks (hooks)

The `hooks/` directory ships [`flag-geo-smells.sh`](hooks/flag-geo-smells.sh) — a PreToolUse Write/Edit/MultiEdit hook on spatial files (`.sql`/`.py`/`.js`/`.ts`/`.md`):

| Check | Triggers on | Rule (§3 / §4) |
|---|---|---|
| geometry/geography column declared with no SRID | spatial files | house opinion #2 / always-store-an-srid |
| `ST_Distance`/`ST_DWithin` on a 4326 geometry with no geography cast / `ST_Transform` | spatial files | house opinion #5 (degree-distance bug) |
| `ST_Distance(...) <` proximity filter (defeats the index) | spatial files | house opinion #4/#6 / index-geometry-with-gist |

Advisory by default (`exit 0` with stderr warnings). Set `GEO_SMELLS_STRICT=1` to make it blocking.

---

## 8. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/design-postgis-schema/SKILL.md`](skills/design-postgis-schema/SKILL.md) | `geospatial-data-engineer` | CRS-first table design: SRID + geometry-vs-geography + GiST index + runnable DDL |
| [`skills/write-spatial-query/SKILL.md`](skills/write-spatial-query/SKILL.md) | `geospatial-data-engineer` | Index-aware `ST_` queries (joins, KNN, buffers, `ST_DWithin`) + the units fix |
| [`skills/serve-vector-tiles/SKILL.md`](skills/serve-vector-tiles/SKILL.md) | `mapping-visualization-engineer` | Format decision (GeoJSON vs MVT) + tile-server recipe + MapLibre source/layer wiring |

---

## 8a. Knowledge bank

Reference docs with `Last reviewed:` dates + confidence notation. Inline priors live on the agents; the files in `knowledge/` are the source of truth, re-read on demand.

| File | Read when |
|---|---|
| [`knowledge/projection-decision-tree.md`](knowledge/projection-decision-tree.md) | Choosing a CRS — the Mermaid tree (web map → 3857; global → 4326 geography; local → UTM/state-plane) + the geometry-vs-geography decision + a tradeoffs table |
| [`knowledge/geospatial-stack-2026.md`](knowledge/geospatial-stack-2026.md) | Recommending tooling — Tier-1/Tier-2 across storage (PostGIS), pipelines (GDAL), serving (pg_tileserv/Martin/Tegola), visualization (MapLibre), routing (OSRM/Valhalla), with retrieval dates |

---

## 9. Templates in this plugin

| Template | Use for |
|---|---|
| [`templates/spatial-data-model.md`](templates/spatial-data-model.md) | CRS-first spatial table design — the SRID/type/index decision recorded before the DDL |
| [`templates/tile-serving-architecture.md`](templates/tile-serving-architecture.md) | The serving-layer decision — GeoJSON vs MVT vs raster, tile server, MapLibre wiring, failure-mode checklist |

---

## 9a. Best-practice rules

Named, citable single-rule docs ([`best-practices/README.md`](best-practices/README.md)): [`always-store-an-srid.md`](best-practices/always-store-an-srid.md), [`index-geometry-with-gist.md`](best-practices/index-geometry-with-gist.md), [`vector-tiles-over-geojson-at-scale.md`](best-practices/vector-tiles-over-geojson-at-scale.md). Each takes one house opinion and makes it a standalone, exception-documented rule.

---

## 10. Escalating out of the geospatial-engineering team

- **`data-platform`** — generic warehouse / ELT modelling of non-spatial facts.
- **`database-engineering`** — the non-spatial OLTP schema (keys, normalization, migrations, locking).
- **`frontend-engineering` / `web-design`** — surrounding map UI chrome, layout, CSS, component framework.
- **`ravenclaude-core/data-engineer`** — generic pipelines feeding the spatial source table.
- **`ravenclaude-core/deep-researcher`** — verifying volatile claims (PostGIS/GDAL/MapLibre/routing versions, projection authority).
- **`ravenclaude-core/documentarian`** — turning a spatial design into a stakeholder-facing deliverable.

> Note: precision-agriculture and fleet-logistics are **consumers** of this engineering layer — they call into it; this plugin does not own their domain logic.

---

## 11. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- Meta-repo developer guide: [`../../CLAUDE.md`](../../CLAUDE.md)
