---
description: "Set the performance strategy: turn vague goals into falsifiable NFRs, model the workload, link to the SLO, and pick the test type (load/stress/soak/spike)."
argument-hint: "[system + performance goal + expected/peak traffic + existing SLO if any]"
---

You are running `/performance-engineering:design-performance-test`. Use `performance-architect` + the `performance-test-strategy` skill.

## Steps
1. Turn the goal into NFRs: each a percentile + threshold + the load it holds at. If product can't give a number, say so and propose one to confirm.
2. Model the workload — request mix, arrival pattern (open vs. closed, steady vs. peak), data distribution, cache warmth, peak multiplier.
3. Link the targets to the customer SLO (route the SLO itself to observability-sre); name which target is latency- vs. throughput-protected.
4. Pick the test type(s) and sequence (load → stress → soak → spike) by the open questions; set pass/fail thresholds per run.
5. Specify the environment + test-data plan (realistic, owned, no prod PII — route de-identification to security-reviewer if needed).
6. Emit the performance test plan (`templates/performance-test-plan.md`) + the Structured Output block (with `Workload modeled:` and `Handoff to fix owner:`). Hand the build to load-testing-engineer.
