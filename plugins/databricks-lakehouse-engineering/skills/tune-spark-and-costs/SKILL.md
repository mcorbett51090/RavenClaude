---
name: tune-spark-and-costs
description: "Diagnose a slow or failing Databricks/Spark job from the EVIDENCE (the Spark UI stages/task-skew/shuffle-spill/GC and the query plan) rather than guessing, then apply the fix the evidence points to — AQE skew-join or key salting for a hot key, broadcast for a small-dim join, repartition/coalesce for partition sizing, OPTIMIZE/compaction for the small-file problem, and writing-instead-of-collecting for driver OOM — and bring the DBU cost down (auto-termination, jobs-vs-all-purpose compute, right-sized warehouses, Photon where it pays). Reach for this when the ask is 'this job is slow/spilling/OOMing', 'why is this taking hours?', or 'our Databricks bill is too high'. Used by `databricks-platform-engineer` (primary)."
---

# Skill: tune-spark-and-costs

> **Invoked by:** `databricks-platform-engineer` (primary). Consulted by `lakehouse-architect` to sanity-check that a design's compute/shuffle/cost profile is sound before committing.
>
> **When to invoke:** "this job is slow / spilling to disk / OOMing"; "why is this taking hours?"; "our Databricks/DBU bill is too high"; any Spark-performance or cost-reduction ask.
>
> **Output:** an evidence-grounded root-cause diagnosis + the specific fix + the cost impact — never a guessed tuning knob.

## Procedure

1. **Read the evidence before proposing anything.** Open the **Spark UI**: stage timeline, per-task time distribution (skew shows as one task ≫ its peers), shuffle read/spill, GC time, and the **query plan** (AQE active? broadcast vs sort-merge join? partition pruning happening?). Traverse [`../../knowledge/databricks-decision-tree.md`](../../knowledge/databricks-decision-tree.md) Tree 4. Do not name a fix before you've named the symptom.
2. **Map symptom → cause → fix** (Tree 4 table):
   - One task 100× its peers → **skew** → AQE skew-join / salting / broadcast the small side.
   - Heavy **shuffle spill** → too-few partitions / wide shuffle → tune shuffle partitions, let AQE coalesce.
   - Millions of tiny files → **small-file problem** → `OPTIMIZE`/compaction, right-size writes.
   - Sort-merge join on a small dim → missing **broadcast** → `broadcast()` hint.
   - **Driver OOM** → `collect()`/`toPandas()` on a big DF → write to a table / stream instead.
   - Executor OOM / high GC → oversized partitions / cache bloat → repartition, cache selectively.
3. **Prefer AQE and built-ins over config knobs.** Leave AQE on and let it coalesce/handle skew before hand-tuning `spark.conf`. Replace row-at-a-time Python UDFs with built-in/SQL functions or vectorized pandas UDFs (they break Catalyst/Photon).
4. **Verify the fix on the evidence, not vibes.** Re-run and confirm the skewed stage / spill / file count actually changed in the Spark UI. A fix that doesn't move the metric isn't the fix.
5. **Then attack DBU cost (Tree 5).** Auto-terminate idle compute (the top leak), move scheduled work to **jobs compute**, right-size and auto-stop SQL warehouses, use spot workers + on-demand driver for fault-tolerant batch, compact tables, and enable Photon only where it accelerates (vectorizable SQL/DataFrame, not UDF-bound Python). Give the order-of-magnitude DBU impact; mark pricing **verify-at-use + dated**.
6. **Name the seams.** Job SLOs/alerting/on-call → `observability-sre`; data tests/expectations → `data-quality-observability`; cross-cloud spend beyond DBUs → `finops-cloud-cost`.

## Worked example

> User: "Our nightly silver-load job used to take 20 minutes and now runs 3 hours and spills to disk. Nothing changed in the code."

- **Evidence first:** Spark UI shows one task in the join stage running ~90× longer than its peers, and heavy shuffle spill. Query plan shows a sort-merge join on `customer_id`.
- **Cause:** **data skew** — a single `customer_id` (a bulk/system account) now dominates the join key, so one partition holds most rows and spills. It grew over time; "nothing changed in the code" because the _data_ changed.
- **Fix:** enable AQE skew-join handling (if not already), and/or salt the hot key; broadcast the small dimension side if it's under threshold. Re-run and confirm the task-time distribution in the Spark UI is now even and spill is gone.
- **Cost angle:** the 3-hour job was billing all-purpose DBUs; move it to jobs compute with auto-termination — the runtime fix plus the compute-type fix cut the bill materially (figures verify-at-use).
- **Seam:** add a freshness/duration SLO + alert so the next drift is caught early → `observability-sre`.

## Guardrails

- **Read the Spark UI / query plan BEFORE proposing a fix** — tuning by guesswork wastes cluster hours; the skewed stage and the spilling task are right there.
- **A non-idempotent write is a correctness bug, not a perf detail** — retries happen; guard against double-counting.
- **Never `collect()` a big DataFrame to the driver** — write to a table or stream; it's a driver OOM.
- **AQE and built-ins first, `spark.conf` knobs last.**
- **Confirm the fix moved the metric** — a change that doesn't alter the Spark UI symptom isn't the fix.
- **Every runtime-specific API/behavior and every DBU/price figure carries a retrieval date + verify-at-use** — DBR versions differ. See [`../../knowledge/databricks-patterns-2026.md`](../../knowledge/databricks-patterns-2026.md).
