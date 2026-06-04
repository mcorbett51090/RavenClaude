---
description: "Build layered dbt models (staging/intermediate/marts) with the right materializations and correct incremental logic."
argument-hint: "[domain + sources in the warehouse]"
---

You are running `/analytics-engineering:model-in-dbt`. Use `analytics-engineer` + the `dbt-modeling` skill.

## Steps
1. Stage each source; compose in intermediate; expose fct/dim marts.
2. Traverse the materialization tree; for incremental, set unique key + is_incremental + late-data.
3. DRY with refs/sources/macros; add owner/description/docs.
4. Emit models (from the structure + incremental templates) + Structured Output block.
