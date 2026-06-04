---
description: "Review operational reliability: pooling, isolation, replication, backup/restore, vacuum/bloat, and observability."
argument-hint: "[current DB ops + concern]"
---

You are running `/database-engineering:review-db-reliability`. Use `db-reliability-engineer` + the `db-reliability` skill.

## Steps
1. Check pooling sizing; isolation choices; transaction length.
2. Validate replica read-routing; TEST the restore + PITR vs RPO.
3. Check autovacuum/bloat; wire metrics to observability-sre.
4. Emit (from `templates/db-reliability-checklist.md`) + Structured Output block.
