---
description: "Build and run the load/stress/soak/spike test from a modeled workload: the right open/closed model, ramping, think time, realistic data, and in-script thresholds."
argument-hint: "[endpoint/system + target + workload model + tool preference k6/Gatling/Locust/JMeter]"
---

You are running `/performance-engineering:run-load-test`. Use `load-testing-engineer` + the `load-test-design` skill.

## Steps
1. Confirm the workload model (mix, arrival pattern, data, cache warmth). If missing, route back to performance-architect — don't guess.
2. Choose the executor: open (arrival-rate) for user-facing traffic, closed (VUs + think time) only for genuinely closed systems. State why, and confirm it corrects for coordinated omission.
3. Design ramping + think time; parameterize realistic, owned test data (no prod PII — route de-identification if mirroring prod).
4. Build the test set the question needs — load, stress, soak, spike — with in-script threshold assertions (p95/p99/error-rate) that fail the run on a miss.
5. Pin the environment, data, model, and tool version for reproducibility; run and report percentiles (p50/p95/p99/max), not averages.
6. Emit the run report + the Structured Output block (with `Workload modeled:` and `Handoff to fix owner:`). Hand bottleneck localization to profiling-and-capacity-engineer.
