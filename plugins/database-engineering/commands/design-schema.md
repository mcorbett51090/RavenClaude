---
description: "Design a normalized relational schema with full constraints and precise types; denormalize only with a named cost."
argument-hint: "[domain + access patterns]"
---

You are running `/database-engineering:design-schema`. Use `schema-architect` + the `relational-schema-design` skill.

## Steps
1. Model to 3NF; constraints in-DB; precise types.
2. Denormalize only with measured evidence + named cost (prefer matview/covering index).
3. Add indexes for the actual access patterns (hand deep tuning to query-performance-engineer).
4. Emit the DDL (from `templates/schema-design.md`) + Structured Output block.
