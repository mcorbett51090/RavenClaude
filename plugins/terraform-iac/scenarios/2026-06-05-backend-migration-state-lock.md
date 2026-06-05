---
scenario_id: 2026-06-05-backend-migration-state-lock
contributed_at: 2026-06-05
plugin: terraform-iac
product: s3-backend
product_version: "unknown"
scope: likely-general
tags: [backend-migration, state-lock, force-unlock, remote-state, locking, ci]
confidence: high
reviewed: false
---

## Problem

A team migrating from a local `terraform.tfstate` (committed to git — itself a problem) to an S3 remote backend with locking hit two failures in one afternoon. First, after adding the `backend "s3"` block and running `terraform init`, the init **failed midway** and they weren't sure whether state had been copied — they nearly ran `init` again, which could have produced two divergent state copies. Second, once on the remote backend, a CI run was killed mid-`apply` (a runner timeout), leaving a **stale lock** in the lock table; every subsequent `plan` failed with `Error acquiring the state lock`. An engineer was about to `terraform force-unlock` with a guessed lock ID.

## Constraints context

- State was previously local and git-committed (no locking, secrets-in-state exposure, merge conflicts on every change) — the migration itself was the right call.
- The CI runner that died held the lock; there was no human "are you done?" to ask — the holder was a dead process.
- `force-unlock` is **destructive if wrong**: unlocking a lock still held by a *live* `apply` lets a second `apply` corrupt state. The danger is unlocking the wrong (live) operation, not the mechanics.

## Attempts

- Tried: re-running `terraform init` after the failed migration "to be safe." Stopped — re-running a partially-completed state migration risks double-copy / divergence. Instead verified what actually landed: checked whether the S3 object existed and compared resource counts against the pre-migration local state. Outcome: confirmed state copied cleanly; the failure was a transient credential timeout on the *post-copy* step, safe to re-init.
- Tried: `force-unlock` with a guessed ID. Stopped — the lock error message **prints the actual lock ID, who/what holds it, and when it was created**. Read it: the holder was the timed-out CI run ID, created 40 minutes ago, and no other run was active. Outcome: confirmed the lock was genuinely stale (dead holder), not a live apply.
- Tried (the move that worked): `terraform force-unlock <exact-lock-id-from-the-error>` only after confirming (a) the holding operation was dead and (b) no other apply was in flight. Then added a CI guard: a max apply timeout shorter than the runner timeout, and a documented runbook for stale-lock recovery. Outcome: lock released safely; future stale locks have a procedure instead of a guess.

## Resolution

**Two separate disciplines for two separate failures.** For the **backend migration**: a migration is a state-copy operation — verify the copy landed (object exists + resource count matches) before re-running anything; never re-`init` a half-migrated backend blind. For the **stale lock**: `force-unlock` is safe *only* when the holder is provably dead and no other apply is in flight, and you use the **exact lock ID from the error message**, never a guess. The error already tells you who holds it and when — read it before acting.

**Action for the next engineer:** before `force-unlock`, answer two questions: "is the holding operation actually dead (not a live apply on another machine/runner)?" and "am I using the exact ID the lock error printed?" If either is no, do not unlock. Treat `force-unlock` and any mid-migration re-`init` as **high-blast, operator-reviewed** operations (Capability Grounding Protocol; route via `iac-policy-and-state-engineer`). Prevent the recurrence with a CI apply-timeout shorter than the runner timeout so a killed run is rarer, plus a written stale-lock runbook.

Cross-reference: [`../best-practices/remote-state-with-locking.md`](../best-practices/remote-state-with-locking.md), [`../best-practices/never-edit-state-by-hand.md`](../best-practices/never-edit-state-by-hand.md), [`../templates/remote-state-backend.md`](../templates/remote-state-backend.md), and the "Which remote state backend?" tree in [`../knowledge/terraform-iac-decision-trees.md`](../knowledge/terraform-iac-decision-trees.md). The specific S3/DynamoDB/GCS lock-resource arguments belong to the cloud plugin; this team owns the migration-safety and lock-recovery discipline.
