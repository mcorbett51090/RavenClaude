---
name: handle-backfills-and-retries
description: Make pipeline tasks safe to re-run and plan backfills that don't corrupt state — prove idempotency (deterministic partition keys, overwrite-by-partition), then add bounded retries with exponential backoff + jitter, and run a controlled backfill (partition strategy, catchup config, concurrency caps, monitoring, rollback). Reach for this when the user says "our pipeline isn't safe to re-run", "add retries", or "we need to backfill <range>". Used by `pipeline-orchestration-engineer` (primary).
---

# Skill: handle-backfills-and-retries

> **Invoked by:** `pipeline-orchestration-engineer` (primary). Also consulted by `orchestration-architect` to confirm an engine's catchup/backfill model fits the data's partitioning.
>
> **When to invoke:** "our pipeline isn't safe to re-run / we got duplicates"; "add retries to these tasks"; "we need to backfill <date range> for <table>"; any re-run, recovery, or historical-reprocessing question.
>
> **Output:** an idempotency fix + a retry policy (bounded attempts, exponential backoff, jitter, transient-vs-deterministic split) + a controlled backfill plan captured in [`../../templates/backfill-runbook.md`](../../templates/backfill-runbook.md).

## Procedure

1. **Prove idempotency BEFORE adding any retry.** A retry is only safe if re-running a task produces the same result. Make each task:
   - keyed on a **deterministic partition key** (logical/event date, not `now()`),
   - **overwrite-by-partition** (delete-then-insert or `INSERT OVERWRITE` / `MERGE` the target partition), **not append** — append + retry = duplicate rows,
   - free of nondeterministic side effects (no unconditional "send email" mid-task; make external effects deduped/keyed too).
   If you cannot make a task idempotent, that is the bug to fix first — do not paper over it with retries.
2. **Add bounded retries with exponential backoff.** Set a sane `retries` (e.g. 3-5), `retry_delay` growing exponentially (e.g. base 2 → 1m, 2m, 4m…) with **jitter** to avoid a thundering herd of synchronized retries hammering a recovering upstream.
3. **Split transient vs deterministic failures.** Retry transient errors (timeouts, throttling, 5xx); **fail fast** on deterministic ones (schema mismatch, bad SQL) — retrying those just burns time and masks the alert.
4. **Define the on-exhaustion action.** When retries are spent: alert with the partition + error, route to a dead-letter / quarantine where applicable, and ensure the failure is visible in the SLA/lineage view (don't fail silently).
5. **Plan the backfill as a production change.** Using [`../../templates/backfill-runbook.md`](../../templates/backfill-runbook.md):
   - **Scope** the exact partitions (date range / keys) to reprocess.
   - **Idempotency precondition:** confirm step 1 holds — backfilling a non-idempotent pipeline corrupts data.
   - **Catchup/run model:** Airflow `catchup`/`backfill` or Dagster partition backfill, scoped to the range — never trigger an unbounded auto-catchup.
   - **Concurrency cap:** limit parallel partitions (pools / max_active_runs / backfill concurrency) so the backfill doesn't starve live runs or overload the warehouse.
   - **Monitoring:** watch progress, error rate, and downstream freshness during the run.
   - **Rollback:** how to revert (restore prior partition snapshot / re-run from last-good) if the backfill goes wrong.
6. **Re-validate downstream + freshness SLAs** after the backfill; confirm lineage consumers picked up the corrected partitions.

## Worked example

> User: "We backfilled last month and got double-counted revenue. Fix it and re-run safely."

- Root cause: the load task **appended** rows keyed on run time, so the backfill re-inserted partitions that already existed → duplicates. Not a retry bug — an **idempotency** bug.
- Fix: re-key on **event date**; switch to **`MERGE`/overwrite-by-partition** so a re-run of `2026-05-12` replaces that partition rather than adding to it.
- Retries: 4 attempts, exponential backoff (1m/2m/4m/8m) + jitter; retry on warehouse throttling, fail fast on schema errors.
- Backfill: runbook with scope = the affected May partitions, idempotency precondition now satisfied, concurrency cap = 4 partitions, monitor row counts vs expected, rollback = restore the pre-backfill snapshot.

## Guardrails

- **No idempotency proof → no retry policy.** This ordering is non-negotiable.
- Overwrite-by-partition, never blind append, for anything that can be re-run.
- Never trigger unbounded auto-catchup; scope every backfill to explicit partitions with a concurrency cap.
- A backfill is a production change: runbook, monitoring, and rollback every time. See [`../../knowledge/orchestration-patterns-2026.md`](../../knowledge/orchestration-patterns-2026.md).
