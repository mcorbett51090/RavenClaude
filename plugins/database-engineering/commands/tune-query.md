---
description: "Tune a slow query from its EXPLAIN plan: name the bottleneck, choose the right index or a sargable rewrite."
argument-hint: "[slow query + EXPLAIN output or schema]"
---

You are running `/database-engineering:tune-query`. Use `query-performance-engineer` + the `query-and-index-tuning` skill.

## Steps
1. Read EXPLAIN (ANALYZE, BUFFERS); fill the worksheet.
2. Traverse the index-choice tree; pick the right index OR a sargable rewrite.
3. Check the write cost; flag N+1 to backend-engineering if app-generated.
4. Emit (from `templates/explain-analysis.md`) + Structured Output block.
