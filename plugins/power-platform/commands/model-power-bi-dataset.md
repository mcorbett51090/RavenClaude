---
description: Model a Power BI semantic model the right way — star schema not a flat table, measures not calculated columns, deliberate storage mode (Import/DirectQuery/Direct Lake), and row-level security tested as the role. Includes DAX-correctness-as-code.
argument-hint: "[the report subject, e.g. 'sales by region and quarter']"
---

# Model a Power BI dataset

You are running `/power-platform:model-power-bi-dataset`. Design the semantic model for what the user described (`$ARGUMENTS`), following this plugin's `power-bi-engineer` discipline. A good model is fast, correct, and secure by construction — a flat table with calculated columns is none of those.

## When to use this

A new report/dataset is being built, or a slow/incorrect one is being remodeled.

## Steps

1. **Star schema, not a flat table** (`bi-star-schema-not-flat-table`): fact table(s) + conformed dimensions; avoid the one-big-table anti-pattern that kills performance and correctness.
2. **Measures, not calculated columns** (`bi-measures-not-calculated-columns`): aggregations are DAX measures (computed at query time over the filter context), not materialized columns that bloat the model and mislead.
3. **Storage mode deliberately** (`bi-storage-mode-selection`): Import for speed on bounded data; DirectQuery for freshness/volume; Direct Lake for Fabric lakehouse scale — pick on data size + freshness need, not habit.
4. **Row-level security tested AS the role** (`bi-row-level-security-tested-as-role`): define RLS roles and **test by viewing as the role**, not as admin — admin sees everything and hides the bug.
5. **DAX correctness as code** (`test-dax-correctness-as-code`): capture expected measure values as test cases so a refactor can't silently change a number.

## Guardrails

- A calculated column where a measure belongs is a performance + correctness defect.
- Never validate RLS as admin — always view-as-role.
- If the data is Fabric-scale, coordinate storage mode with the `microsoft-fabric` plugin's Direct Lake guidance.
