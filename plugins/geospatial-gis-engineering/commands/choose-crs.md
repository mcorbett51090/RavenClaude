---
description: "Choose a coordinate reference system: storage SRID, display/tile CRS, and the measurement CRS or geography type."
argument-hint: "[what the data is + use + extent]"
---

You are running `/geospatial-gis-engineering:choose-crs`. Use `gis-architect` + the `design-coordinate-reference-system` skill.

## Steps
1. Identify primary use (storage / display / distance / area) and extent.
2. Traverse the CRS tree in `knowledge/geospatial-decision-trees.md`.
3. Decide canonical SRID, display CRS (3857), and measurement CRS/geography; name what you will NOT do (e.g. no area in 3857).
4. Emit using `templates/crs-decision.md` + the Structured Output block.
