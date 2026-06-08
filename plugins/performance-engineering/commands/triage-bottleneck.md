---
description: "Profile a slow/near-limit system, localize the bottleneck (USE/RED + flame graph), compute capacity + headroom (Little's law), and verdict any regression."
argument-hint: "[symptom + workload it occurs at + profiles/traces available + traffic to size for]"
---

You are running `/performance-engineering:triage-bottleneck`. Use `profiling-and-capacity-engineer` + the `profiling-and-bottleneck-triage` skill.

## Steps
1. Reproduce the symptom at a known workload; report percentiles (p95/p99/max), never the average.
2. Triage with USE (utilization/saturation/errors per resource) + RED (rate/errors/duration per request stream); saturation, not utilization, is the signal.
3. Profile to localize: on-CPU flame graph for hot paths, off-CPU for lock/IO/downstream waits, allocation/heap for memory/GC. Name the single highest-leverage fix.
4. If sizing is asked: compute capacity with Little's law (L = λ·W) + the measured saturation point + explicit failover/growth headroom (never to 100%).
5. If a regression is claimed: compare to a committed baseline at the same pinned workload; report the p95/p99 delta vs. threshold + a flame-graph diff; recommend a gate.
6. Emit the capacity-and-bottleneck report (`templates/capacity-and-bottleneck-report.md`) + the Structured Output block (with `Workload modeled:` and `Handoff to fix owner:`). Route the fix to database-engineering / frontend-engineering / backend-engineering; the autoscaler to cloud-native-kubernetes.
