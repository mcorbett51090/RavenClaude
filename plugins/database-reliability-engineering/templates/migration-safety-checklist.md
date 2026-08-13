# Migration safety checklist — `<migration name>`

> Output of `database-operations-engineer`. One per production schema change. The
> gate a migration passes before it touches prod. Expand-contract by default.

## 1. The change
- **What's changing:** `<column / table / index / constraint / type>`
- **Additive, or non-additive?** `<additive → §3 short path | non-additive → full expand-contract>`
- **Target table size / hot?** `<row count, write QPS>`

## 2. Lock & lag risk
- **Lock each step takes + duration under load:** `<…>`
- **`lock_timeout` set:** `<value>`
- **Index builds use CONCURRENTLY / online:** `<yes/no>`
- **Backfill paced against replication lag:** `<yes — how>`

## 3. Expand-contract steps (each reversible)
- [ ] **Expand** — additive new shape deployed alone. Rollback: `<…>`
- [ ] **Dual-write** — app writes old + new. Rollback: `<…>`
- [ ] **Backfill** — batched / throttled / idempotent / resumable, kill switch.
      Batch size: `<…>` · Pacing: `<…>` · Progress tracking: `<…>`
- [ ] **Cutover** — reads move to new shape; parity verified before + after.
- [ ] **Contract** — drop old shape once nothing reads it. Rollback: `<…>`

## 4. Verification
- **Parity check (old vs new):** `<query / method>`
- **Tested on a prod-scale copy:** `<yes/no — result>`

## 5. Blast-radius & abort
- **Kill switch / abort procedure:** `<…>`
- **Who's on call during the migration:** `<…>`
- **Rollback rehearsed:** `<yes/no>`

## Hand-offs
- [ ] Target schema design → `database-engineering`
- [ ] CI/CD shipping the steps → `devops-cicd`
- [ ] If it triggers a live incident → `database-incident-responder`
