---
description: "Produce a cutover runbook with go/no-go gates and a tested rollback for a data migration or system switch-over. Reach for this for any zero-downtime move or final switch."
argument-hint: "[the migration / switch-over]"
---

# Plan cutover

You are running `/legacy-modernization:plan-cutover` for `$ARGUMENTS`. Run it the way the `migration-engineer` would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §2.

## Steps (traverse top-to-bottom; do not skip)
1. Choose the migration pattern — dual-write / shadow-read / backfill+reconcile / expand-contract.
2. Run in parallel and reconcile — until old and new agree to tolerance.
3. Define go/no-go gates — reconciliation clean, SLOs healthy, rollback rehearsed.
4. Rehearse the rollback — actually exercise it in non-prod or canary.
5. Cut over incrementally and watch — shift one cohort at a time, ready to flip back.

## Output
A cutover runbook in the [`../templates/cutover-runbook.md`](../templates/cutover-runbook.md) shape. See [`../skills/data-migration-and-cutover/SKILL.md`](../skills/data-migration-and-cutover/SKILL.md).

## Guardrails
- Every cutover needs a tested rollback (§2 #6) — a cutover you can't undo is a bet, not a plan.
- DDL mechanics route to `database-engineering`; traffic-shift automation to `devops-cicd`.
- Cite a source + date for every external figure (or mark it).
