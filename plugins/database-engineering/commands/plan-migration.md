---
description: "Plan a safe, reversible, lock-aware schema migration with expand/contract and batched backfill, sequenced across deploys."
argument-hint: "[schema change + table traffic]"
---

You are running `/database-engineering:plan-migration`. Use `migration-engineer` + the `safe-schema-migrations` skill.

## Steps
1. Traverse the migration-safety tree; use the online-safe form for locking DDL.
2. Lay out expand -> backfill (batched) -> switch -> contract across deploys.
3. Define rollback for each step; sequence with devops-cicd/release-engineer.
4. Emit (from `templates/migration-plan.md`) + Structured Output block.
