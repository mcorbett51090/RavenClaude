---
name: profiling-and-bottleneck-triage
description: "Localize the bottleneck and size the system: CPU/memory/IO profiling and flame graphs, USE/RED triage to name the constraining resource, capacity planning with headroom via Little's law and the measured saturation point, and regression detection against a committed baseline."
---

# Profiling & Bottleneck Triage

## Measure before you optimize
Profile first — the first bottleneck is almost never where you guessed, and optimizing an un-profiled guess speeds up the thing that wasn't slow. A flame graph, CPU/memory/IO profile, or USE/RED breakdown names the actual constraint.

## USE for resources, RED for requests
USE (utilization / saturation / errors) walks every resource — CPU, memory, disk, network, locks, pools — to find the saturated one. RED (rate / errors / duration) watches the request stream for where duration spikes. Apply both; **saturation** (a growing queue), not utilization, is the danger signal — it hurts latency long before utilization hits 100%.

## Read the flame graph — including off-CPU
An on-CPU flame graph names the hot path; an off-CPU profile catches the thread blocked on a lock, IO, or a slow downstream — often the real latency. Diff flame graphs across releases to localize what changed.

## Capacity with computed headroom
Little's law (`L = λ·W`: concurrency = arrival rate × mean service time) plus the measured per-instance saturation point gives the instance count. Add explicit headroom for failover and growth; never plan to 100% utilization. Size to the peak and the knee, not the average.

## Regression against a committed baseline
"Feels slower" is not a finding. Gate on a measured p95/p99 delta versus a committed baseline at the same pinned workload/data/environment/tool version; a flame-graph diff localizes the cause when it regresses.

## Output
A capacity-and-bottleneck report: the measured percentiles, the localized constraint (USE/RED + flame graph), the Little's-law capacity math + headroom, the regression verdict, and the fix handoff to `database-engineering` / `frontend-engineering` / `backend-engineering` (and the autoscaler to `cloud-native-kubernetes`).
