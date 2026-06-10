---
name: load-test-design
description: "Design the load/stress/soak/spike test from a modeled workload: pick the open- vs closed-model executor deliberately, design ramping and think time, generate realistic owned test data, avoid coordinated omission, and assert thresholds in-script — tool-neutral across k6/Gatling/Locust/JMeter."
---

# Load Test Design

## Pick the workload model deliberately
A closed model (fixed VUs + think time) and an open model (fixed arrival rate) diverge sharply under saturation. Prefer an **open** arrival-rate executor for user-facing traffic — a closed model self-throttles when the system slows and hides the failure. Reserve closed for genuinely closed systems (batch workers, fixed pools). State which and why.

## Avoid coordinated omission
A generator that stalls waiting on a slow response never *issues* the worst-case requests, so the tail goes unrecorded and the reported p99 lies. Use an arrival-rate executor that keeps issuing on schedule and a tool with latency correction; name the executor and whether it corrects.

## Ramp and pace like real traffic
Ramp up rather than slamming full load from t=0, and apply a think-time distribution — a zero-think-time stampede measures a thundering herd, not your workload. Warm the cache the way prod is warmed, or state explicitly that you're testing cold.

## Realistic, owned test data — never prod PII
Generate or synthesize representative data (cardinality, skew, size, cache-miss rate); uniform synthetic data on a warm cache proves nothing. Any prod-mirrored data routes through de-identification (`security-reviewer` + `data-governance-privacy`) first.

## Build the set, assert in-script
Load (target at expected + peak), stress (ramp to the knee), soak (hours; watch memory/latency creep/pool exhaustion), spike (step to peak; measure error rate + recovery). Put the pass/fail threshold (p95/p99/error-rate) in the script so the run fails on a miss — a gate, not a chart to eyeball. Pin environment, data, model, and tool version for reproducibility.

## Output
Runnable load/stress/soak/spike scripts (k6/Gatling/Locust/JMeter) with the right model, ramping, think time, data, and thresholds. Hand bottleneck localization to `profiling-and-capacity-engineer`; the fix to the owning plugin.
