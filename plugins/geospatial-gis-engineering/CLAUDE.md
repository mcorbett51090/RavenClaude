# Geospatial / GIS Engineering Plugin — Team Constitution

> Team constitution for the `geospatial-gis-engineering` Claude Code plugin. Three specialist agents — **gis-architect**, **spatial-data-engineer**, **geospatial-app-engineer** — plus a decision-tree knowledge bank, skills, templates, best-practices, and an advisory hook, all aimed at building **location-aware systems that are correct (CRS, validity), fast (spatial indexes), and scalable (tiling)**.
>
> **Orientation:** this file is **domain-specific** to geospatial/GIS engineering. For the domain-neutral team constitution every plugin inherits, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`gis-architect`](agents/gis-architect.md) | Spatial-storage decision (PostGIS vs warehouse vs tile/feature service), CRS choice, serving topology | "PostGIS or BigQuery GIS?"; "what SRID?"; "how do I serve a million features?" |
| [`spatial-data-engineer`](agents/spatial-data-engineer.md) | Correct + fast spatial SQL, spatial joins, KNN, geometry validity, reprojection, loading | "this proximity query times out"; "tag pings with their district"; "load this Shapefile" |
| [`geospatial-app-engineer`](agents/geospatial-app-engineer.md) | Web-map rendering, format choice (GeoJSON/MVT/raster), client performance, GeoJSON correctness | "my map of 50k markers locks up"; "GeoJSON or vector tiles?"; "data shows in the ocean" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. Per the marketplace house rule, this plugin ships specialist *doing*-agents and does not fork core's *review* roles (architect/security-reviewer).

---

## 2. Routing rules (Team Lead)

- **"Where should spatial data live?" / "what CRS?" / "how do I serve this?"** → `gis-architect`.
- **"Write/fix this spatial query" / "load this data" / "this is slow"** → `spatial-data-engineer`.
- **"Put it on a map" / "the map is slow" / "wrong place on the map"** → `geospatial-app-engineer`.
- **Non-spatial OLTP schema, generic indexing, migrations** → escalate to `database-engineering`.
- **Warehouse provisioning, ELT pipelines** → `data-platform`.
- **The app shell / routing / build budget around the map** → `frontend-engineering`.
- **Vehicle routing / ETA / field-crew dispatch** → `fleet-logistics`; **agronomic layers** → `precision-agriculture`.

---

## 3. Cross-cutting house opinions (the agents enforce)

1. **Decide the CRS deliberately and write it down.** One known SRID per column (4326 default); reproject on read, store once.
2. **The index is the query plan.** GiST-index every spatially-filtered column; verify with `EXPLAIN (ANALYZE)`.
3. **Use the sargable predicate.** `ST_DWithin` over `ST_Distance < d`; `<->` KNN over cross-join-then-sort.
4. **geometry vs geography is a per-column call** — `geography` for correct lon/lat distance, `geometry` (projected) for speed and area/length math.
5. **Web Mercator (3857) is for tiles, never for area.**
6. **Validate geometry at the boundary** (`ST_IsValid`/`ST_MakeValid`), not after it breaks `ST_Area`/`ST_Union`.
7. **GeoJSON is `[lon, lat]`** (RFC 7946), WGS84, right-hand winding.
8. **Tile large layers**; never ship a giant GeoJSON or render N DOM markers.
9. **Simplify per zoom deliberately**, naming the tolerance.
10. **The browser is not a GIS** — push heavy spatial work to the server/tile pipeline.

---

## 4. Anti-patterns the agents flag (and the advisory hook detects)

The `hooks/` directory ships [`check-geospatial-anti-patterns.sh`](hooks/check-geospatial-anti-patterns.sh) — a PreToolUse Write/Edit/MultiEdit hook on `.sql`/`.py`/`.js`/`.ts`/`.md`/`.geojson`/`.json`:

| Check | Triggers on | Rule (§3) |
|---|---|---|
| `ST_Distance(...) < d` used as a filter | spatial files | #3 (non-sargable) |
| Area/length computed in EPSG:3857 | spatial files | #5 |
| SRID 0 / unknown SRID | spatial files | #1 |
| `geometry`/`geography` column without a typmod | spatial files | #1 |

Advisory by default (`exit 0` with stderr warnings). Set `GEOENG_STRICT=1` to make it blocking.

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before an agent says "I can't" or commits to an approach, it must:

1. **Check the 5 skills** plus core skills.
2. **Traverse the decision tree** ([`knowledge/geospatial-decision-trees.md`](knowledge/geospatial-decision-trees.md)) before choosing storage/CRS/serving — don't keyword-match.
3. **Try the next-easiest defensible method** before declaring blocked.
4. **Escalate with the mandatory phrasing** — what was tried, what was ruled out, the recommended next path.

Volatile tooling claims carry a retrieval date and are re-verified before quoting ([`knowledge/geospatial-stack-2026.md`](knowledge/geospatial-stack-2026.md)).

---

## 6. Output Contract

```
Workload / question: <what was asked, in the decision tree's terms>
Decision: <storage / CRS / query / format + WHY>
CRS & SRID: <canonical SRID; reproject plan; geometry vs geography>
Index / performance: <GiST index; sargable predicate; EXPLAIN check>
Validity / correctness: <ST_IsValid; GeoJSON [lon,lat]; extent sanity>
Seams handed off: <database-engineering / data-platform / frontend-engineering / fleet-logistics / precision-agriculture>
```

**Plus the cross-plugin Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)).

---

## 7. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/choose-spatial-storage/SKILL.md`](skills/choose-spatial-storage/SKILL.md) | `gis-architect` | PostGIS vs warehouse vs tile/feature service by workload |
| [`skills/design-coordinate-reference-system/SKILL.md`](skills/design-coordinate-reference-system/SKILL.md) | `gis-architect` | 4326 vs projected vs geography; one SRID per column; reproject on read |
| [`skills/write-spatial-queries/SKILL.md`](skills/write-spatial-queries/SKILL.md) | `spatial-data-engineer` | Index-using spatial SQL: ST_DWithin, KNN, spatial joins, EXPLAIN |
| [`skills/build-map-tiles-and-serving/SKILL.md`](skills/build-map-tiles-and-serving/SKILL.md) | `geospatial-app-engineer` | GeoJSON vs MVT vs raster; rendering at scale; coordinate correctness |
| [`skills/spatial-data-quality/SKILL.md`](skills/spatial-data-quality/SKILL.md) | `spatial-data-engineer` | Validity, SRID, extent sanity, topology, validate-at-load |

---

## 8. Knowledge bank

| File | Read when |
|---|---|
| [`knowledge/geospatial-decision-trees.md`](knowledge/geospatial-decision-trees.md) | Choosing storage, CRS, geometry/geography, or web-serving format — the Mermaid decision trees |
| [`knowledge/geospatial-stack-2026.md`](knowledge/geospatial-stack-2026.md) | Recommending a tool/library — the dated 2026 capability map (re-verify versions before quoting) |

---

## 9. Templates & commands

| Template | Use for |
|---|---|
| [`templates/spatial-schema-design.md`](templates/spatial-schema-design.md) | The storage + CRS + DDL + index + quality plan |
| [`templates/crs-decision.md`](templates/crs-decision.md) | A coordinate-reference-system decision record |
| [`templates/tile-pipeline-plan.md`](templates/tile-pipeline-plan.md) | Getting a layer onto a web map performantly |

Commands: [`/design-spatial-schema`](commands/design-spatial-schema.md), [`/choose-crs`](commands/choose-crs.md), [`/review-geospatial`](commands/review-geospatial.md).

---

## 10. Escalating out of the geospatial team

- **`database-engineering`** — non-spatial OLTP schema, generic query tuning, migrations, transactions.
- **`data-platform`** — warehouse provisioning, ELT pipelines, embedded BI.
- **`frontend-engineering`** — the app shell, state, build/perf budget around the map.
- **`web-design`** — cartographic/brand design of the map.
- **`fleet-logistics`** — vehicle routing, ETA, dispatch; **`precision-agriculture`** — agronomic/field layers.
- **`ravenclaude-core/security-reviewer`** — security verdicts (e.g. exposing a tile server, location-data privacy).

---

## 11. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol: [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- The database seam: [`../database-engineering/CLAUDE.md`](../database-engineering/CLAUDE.md)
- The data-platform seam: [`../data-platform/CLAUDE.md`](../data-platform/CLAUDE.md)

---

## 12. Milestones

- **v0.1.0** — initial build-out: 3 agents (gis-architect, spatial-data-engineer, geospatial-app-engineer), 5 skills, a decision-tree knowledge bank (4 Mermaid trees) + a dated 2026 stack map, 10 best-practices, 3 templates, 3 commands, and 1 advisory hook (4 checks). PostGIS-leaning, principles portable to BigQuery GIS / Snowflake / GeoParquet. Seams to database-engineering, data-platform, frontend-engineering, fleet-logistics, precision-agriculture.
