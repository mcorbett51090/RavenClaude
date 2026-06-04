---
name: safe-schema-migrations
description: "Evolve schemas without downtime: expand/contract (add -> backfill in batches -> switch -> drop) across separate deploys, lock-aware DDL (create indexes CONCURRENTLY, nullable-add-then-validate), reversibility, and ordered versioned migrations."
---

# Safe Schema Migrations

## Expand/contract
Add new (safely) -> **backfill in batches** -> dual-write/switch reads -> drop old. Across **separate deploys**. A rename = add-copy-switch-drop, not `ALTER RENAME` mid-traffic.

## Lock awareness
Volatile-default add, type change, or `SET NOT NULL` can lock the table. Use: nullable add + batched backfill + `ADD CONSTRAINT ... NOT VALID` then `VALIDATE`; create indexes **CONCURRENTLY**.

## Reversible + ordered
Every migration has a down path / tested rollback. Versioned, ordered, never edit a shipped migration. Sequence with `devops-cicd/release-engineer`.
