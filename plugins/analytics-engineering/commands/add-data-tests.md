---
description: "Add dbt tests, source freshness, model contracts, and anomaly checks that gate the warehouse."
argument-hint: "[models + where bad data slipped through]"
---

You are running `/analytics-engineering:add-data-tests`. Use `data-quality-testing-engineer` + the `data-quality-testing` skill.

## Steps
1. Add not_null/unique/accepted_values/relationships on key columns.
2. Gate source freshness; add model contracts at consumer boundaries.
3. Add singular tests for business invariants + anomaly detection.
4. Wire into CI (devops-cicd); route significance to applied-statistics.
5. Emit (from `templates/data-tests.yml`) + Structured Output block.
