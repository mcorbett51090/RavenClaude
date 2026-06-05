---
scenario_id: 2026-06-05-warehouse-cost-blowout-dashboard-launch
contributed_at: 2026-06-05
plugin: data-platform
product: snowflake
product_version: "unknown"
scope: likely-general
tags: [warehouse, cost, snowflake, pre-aggregation, autosuspend, finops]
confidence: medium
reviewed: false
---

## Problem

A client already on Snowflake launched a new customer-facing dashboard (Cube → React, ~40 viewers across the org). Within the first full billing week the Snowflake bill jumped several-fold over the pre-launch baseline. The dashboard worked and was fast — but every KPI tile, on every page load, was firing a fresh query straight against the warehouse, and the warehouse was staying warm essentially around the clock because traffic never fully stopped. The client's finance team flagged it before we did, which is the worst way to find a cost problem.

## Context

- The dashboard had **no pre-aggregation layer**: each widget's query hit raw/large fact tables directly through Cube with caching effectively disabled, so concurrent viewers each triggered full warehouse scans.
- The compute warehouse's **auto-suspend was set high** (several minutes of idle), and steady trickle traffic kept resetting the idle timer — so it almost never suspended, and credits burned continuously even off-peak.
- Some tiles ran `SELECT`-heavy queries over unpartitioned, unclustered tables, so each refresh scanned far more micro-partitions than the answer required.
- Constraint: the client was *already* on Snowflake (house opinion #10 — don't reinvent the warehouse), so "move off Snowflake" was off the table; the job was to make the existing warehouse economical under dashboard load, not to re-platform.

## Attempts

- Tried: simply sizing the warehouse down a tier. Outcome: cut the per-second rate but slowed the dashboard and didn't address the root cause (it was still scanning raw tables continuously). A blunt lever, not the fix — masked the symptom.
- Tried: **pre-aggregating in the semantic layer** — Cube rollup pre-aggregations for the dashboard's KPI/chart measures, refreshed on a schedule, so the common viewer queries are served from the pre-agg (and Cube's cache) instead of a fresh warehouse scan. Outcome: the overwhelming majority of viewer queries stopped touching the warehouse at all; warehouse load dropped to the scheduled refresh plus rare cache-misses.
- Tried: **lowering auto-suspend to ~60s** on the dashboard's warehouse and isolating dashboard traffic onto its own warehouse so it could suspend independently of the ELT/transform workload. Outcome: the warehouse now actually suspends between refreshes; idle credit burn collapsed.
- Tried: **partitioning/clustering the hot fact tables** on the dashboard's filter/sort keys (date + tenant) so the residual live queries scan far fewer micro-partitions. Outcome: the cache-miss queries got cheaper too.

## Resolution

The root cause was **shipping raw per-viewer warehouse queries with no pre-aggregation, on a warehouse that never suspended**. The fix layered four standing defaults: pre-aggregate in the semantic layer before the viewer; size *and* auto-suspend the warehouse for the workload (not just size); isolate dashboard compute from ELT compute; and partition/cluster the hot tables for scan cost. The single biggest lever was pre-aggregation — it removed the warehouse from the hot path for most queries — but the auto-suspend fix is what stopped the *idle* burn that sizing alone never touches.

**Action for the next consultant hitting this pattern:** before launching a customer-facing dashboard on a credit/scan-billed warehouse (Snowflake, BigQuery, Databricks), **assume per-viewer raw queries will blow up the bill** and design the pre-aggregation + cache layer up front, not after the finance flag. Check three things on day one: (1) is there a pre-agg/rollup serving the common tiles, or is every load a fresh scan? (2) does the dashboard warehouse actually *suspend* (low auto-suspend + isolated from steady ELT traffic), or is trickle traffic keeping it warm? (3) are the hot fact tables partitioned/clustered on the filter keys? Traverse the `## Decision Tree: Dashboard performance problem — where is the bottleneck?` and the new warehouse-cost-control tree in [`../knowledge/data-platform-decision-trees.md`](../knowledge/data-platform-decision-trees.md); cost and latency share the same root fix here.

**Sources (retrieved 2026-06-05):** Snowflake auto-suspend / warehouse-cost guidance and micro-partition/clustering behavior are version- and account-specific — treat dollar figures and specific credit rates as `[verify-at-use]` against the retrieval-dated [`../knowledge/cloud-database-landscape-2026.md`](../knowledge/cloud-database-landscape-2026.md) and [`../knowledge/snowflake-warehouse-sizing-recipes.md`](../knowledge/snowflake-warehouse-sizing-recipes.md) before quoting a client. Cube pre-aggregations: https://cube.dev/docs/product/caching/using-pre-aggregations (`[verify-at-use]`). Canonical rules this corroborates — [`../best-practices/cube-preaggregate-before-viewer.md`](../best-practices/cube-preaggregate-before-viewer.md), [`../best-practices/warehouse-partition-and-cluster-for-cost.md`](../best-practices/warehouse-partition-and-cluster-for-cost.md), [`../best-practices/warehouse-select-by-workload-not-brand.md`](../best-practices/warehouse-select-by-workload-not-brand.md).
