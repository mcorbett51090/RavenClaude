---
description: Review a Fabric capacity for cost and throttling — measure smoothed usage over days with the Capacity Metrics app, right-size to average not peak, isolate noisy workloads from interactive BI, and tune surge-protection thresholds.
argument-hint: "[the capacity/symptom, e.g. 'F128 throttling and dashboards stalling']"
---

# Review capacity and cost

You are running `/microsoft-fabric:review-capacity-and-cost`. Diagnose and right-size the capacity for what the user described (`$ARGUMENTS`), following this plugin's `fabric-admin` FinOps discipline — capacity is a shared, throttleable resource, and smoothing changes the math.

## When to use this

A capacity is throttling, costing too much, or being sized for a new workload. For a tiny single-purpose capacity with no interactive/background contention there's nothing to isolate — say so. "Is this metric movement real?" routes to `applied-statistics/applied-statistician`.

## Steps

1. **Measure over days, not minutes** — use the Fabric Capacity Metrics app over a long window; smoothing (background ops over 24h, interactive over 5–64 min) hides short load tests, so a 5-minute burst is exactly what you must not size on (`capacity-size-to-average-not-peak.md`).
2. **Size to the smoothed average + headroom, not the instantaneous peak** — buying a bigger SKU to cover a spike that smoothing already absorbs is the over-provisioning anti-pattern; use bursting for short spikes instead (same file).
3. **Do the scale-down math** — to safely drop F128→F64, smoothed usage on F128 should sit <40%; allow a 25–50% buffer for peak/throttling headroom (same file). Remember memory/concurrency limits are *not* smoothed — a model that doesn't fit needs a bigger SKU regardless of average CU.
4. **Isolate noisy workloads from interactive BI** — throttling is per-capacity, so put exec dashboards on their own capacity (or a Mission-Critical workspace) separate from Spark/pipeline/AI jobs (`capacity-isolate-noisy-workloads.md`).
5. **Tune surge protection from the metrics charts, not by guess** — set background-rejection and recovery thresholds off the Background/Interactive rejection + Utilization charts; remember SQL/UI ops can count as background and get rejected (same file).
6. **Reserve for steady load, pay-as-you-go/autoscale for spiky load** (`capacity-size-to-average-not-peak.md`). Use the `templates/fabric-capacity-cost-review.md` shape for the client deliverable.

## Guardrails

- Never treat surge protection as a substitute for sizing or isolation — to fully protect a critical solution it must live on its own correctly-sized capacity.
- Never size for instantaneous peak or trust a short load test — smoothing hides exactly that.
- This plugin is advisory: emit the metrics-app analysis + `fab`/REST snippets the consultant runs against their own tenant.
