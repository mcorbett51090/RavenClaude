# Backfill runbook — <pipeline-name> · <date-range / partition-keys>

> A backfill is a **production change**. Fill this in and get sign-off before reprocessing. Pairs with
> [`dag-design-doc.md`](dag-design-doc.md) (the pipeline's design).

**Owner:** <name> · **Date:** <YYYY-MM-DD> · **Orchestrator:** <Airflow / Dagster / Prefect / …> · **Status:** planned / approved / running / done / rolled-back

## 1. Why & scope
- **Reason:** <bug fix / late-arriving data / new column / schema change / data correction>
- **Exact partitions to reprocess:** <date range YYYY-MM-DD..YYYY-MM-DD · keys/regions/tenants — be precise>
- **Affected datasets:** <tables/assets that will be rewritten>
- **Downstream consumers to notify:** <dashboards/models/exports + owners>

## 2. Idempotency precondition (BLOCKER — verify before running)
- [ ] Each affected task is **idempotent**: deterministic partition key + **overwrite-by-partition** (MERGE / INSERT OVERWRITE / delete-then-insert), **not append**.
- [ ] Confirmed a single-partition re-run **replaces** (does not duplicate) data: <how verified>
- **If not idempotent:** STOP. Fix idempotency first (see `handle-backfills-and-retries`); backfilling a non-idempotent pipeline corrupts data.

## 3. Run plan
- **Mechanism:** <Airflow `dags backfill` / scoped catchup · Dagster partition backfill · Prefect run>
- **Catchup safety:** <confirm scoped to the range above — NO unbounded auto-catchup>
- **Concurrency cap:** <max parallel partitions — pools / max_active_runs / backfill concurrency — so live runs aren't starved and the warehouse isn't overloaded>
- **Estimated duration / cost:** <partitions × per-partition cost>
- **Run window:** <off-peak? avoid clashing with the nightly run?>

## 4. Monitoring during the run
- **Watch:** <progress (partitions done) · error rate · downstream freshness · warehouse load>
- **Abort criteria:** <error rate > X% / live SLA at risk → pause>

## 5. Validation after the run
- [ ] Row counts / aggregates per partition match expected: <check>
- [ ] No duplicates introduced: <check>
- [ ] Downstream consumers picked up corrected partitions; freshness SLAs green.

## 6. Rollback
- **How to revert:** <restore pre-backfill partition snapshot / re-run from last-good / time-travel restore>
- **Snapshot taken before run?** <yes/no + location>
- **Rollback validation:** <how you confirm the revert is clean>

## 7. Sign-off & log
- **Approved by:** <name> · <date>
- **Started / finished:** <timestamps>
- **Outcome:** <success / partial / rolled-back + notes>
