---
description: "Design a spatial schema: storage choice, CRS/SRID, geometry-vs-geography, spatial indexes, and validity gates."
argument-hint: "[domain + data volume + read patterns]"
---

You are running `/geospatial-gis-engineering:design-spatial-schema`. Use `gis-architect` (+ `spatial-data-engineer` for the SQL).

## Steps
1. Name the workload; traverse the storage tree in `knowledge/geospatial-decision-trees.md`.
2. Choose the canonical SRID and the reproject-on-read plan (CRS tree).
3. Pick geometry vs geography per column; write the DDL with typmod, validity CHECK, and GiST index.
4. Emit using `templates/spatial-schema-design.md` + the Structured Output block.
