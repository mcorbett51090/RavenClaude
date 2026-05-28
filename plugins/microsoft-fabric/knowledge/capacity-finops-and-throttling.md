# Capacity, FinOps & throttling

**Last reviewed:** 2026-05-28 · **Confidence:** high (first-party Microsoft Learn, retrieved 2026-05-28).
**Owner:** `fabric-admin`.
**Source:** [Throttling policy](https://learn.microsoft.com/fabric/enterprise/throttling), [Plan capacity](https://learn.microsoft.com/fabric/enterprise/plan-capacity), [Optimize capacity](https://learn.microsoft.com/fabric/enterprise/optimize-capacity), [Cost optimization (WAF)](https://learn.microsoft.com/azure/well-architected/microsoft-fabric/cost-optimization).

## The capacity model

One **capacity** drives all Fabric workloads in its workspaces, including OneLake. You buy a **SKU** (F2…F2048); each gives a fixed number of **Capacity Units (CUs)**:

| SKU | CUs | (old Premium) |
|---|---|---|
| F2 | 2 | |
| F8 | 8 | |
| F64 | 64 | P1 |
| F128 | 128 | P2 |
| F256 | 256 | P3 |
| F512 | 512 | P4 |
| F1024 | 1024 | P5 |

OneLake **storage** is billed like ADLS (pay for data stored); OneLake **transactions** (read/write/list) consume CUs from the capacity that issues them — there's no separate per-transaction charge. A **shortcut** read bills compute to the *consuming* capacity, storage to the *owning* capacity.

## Bursting, smoothing, throttling (the three you must explain)

- **Bursting** — an operation may temporarily use **more** compute than the SKU provisions, so it finishes fast (a small SKU can run a large job). Warehouse burstable scale factor is 1×-32× on small SKUs, 1×-12× on F64+.
- **Smoothing** — consumed CUs are **averaged over future time**: interactive ops over 5-64 min, **background ops over 24 h**. So you size to **average**, not peak. A background job consuming 6× the next-10-min budget still doesn't throttle, because its cost spreads across 2,880 30-sec timepoints.
- **Throttling** — sustained overuse (above SKU limits after smoothing) delays then rejects operations. It is **per-capacity**: one overloaded capacity is throttled while others run normally.

## FinOps playbook (`fabric-admin` prescribes)

1. **Rightsize the SKU.** Run a scoped POC on a trial/pay-as-you-go F SKU, measure CU with the **[Fabric Capacity Metrics app](https://learn.microsoft.com/fabric/enterprise/metrics-app)**, then commit. Start conservative; scaling is online.
2. **Reserve when steady.** A **1-year capacity reservation** is the lowest cost for predictable load; pay-as-you-go / autoscale for spiky load.
3. **Isolate noisy workloads (house opinion #5).** Throttling is per-capacity — put data-prep/pipelines on a separate capacity from interactive BI so one can't starve the other. Use **surge protection / capacity limits** to cap background consumption.
4. **Use smoothing deliberately.** Schedule heavy background jobs to ride the 24-h smoothing window; don't size for peak.
5. **Optimize per experience.** Stop idle Spark sessions (default timeout 20 min); reserve only the executors you need (avoid HTTP 430 "too many requests"); enable the **Native Execution Engine**; pre-aggregate in OneLake; enable Power BI query folding; push heavy transforms to Spark. KQL DB autoscales on usage.
6. **Estimate up front.** [Fabric Capacity Estimator](https://www.microsoft.com/microsoft-fabric/capacity-estimator) + [Azure Pricing Calculator]; monitor actuals with Cost Management + the [fabric-toolbox cost analysis](https://github.com/microsoft/fabric-toolbox).

## Signals it's time to scale (vertical = bigger SKU; horizontal = more capacities)
Consistently high CU utilization · slower interactive queries · rising query latency · memory failures. Validate with load tests over a **long** window (smoothing hides short stress tests). Use **Workspace Monitoring** + the Capacity Metrics app.

> The WAF for Fabric is the spine here: cost decisions are *design* decisions — query patterns, data movement, and retention drive both compute and storage.
