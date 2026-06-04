---
description: "Refactor a messy dbt project into clean layers with restored lineage and right-sized materializations."
argument-hint: "[dbt project pain]"
---

You are running `/analytics-engineering:refactor-dbt-project`. Use `analytics-engineer` + the `dbt-modeling` skill.

## Steps
1. Identify giant/multi-purpose models; split into staging/intermediate/marts.
2. Extract macros; replace copy-paste with refs.
3. Fix materializations; add tests + docs.
4. Emit the refactor plan + Structured Output block.
