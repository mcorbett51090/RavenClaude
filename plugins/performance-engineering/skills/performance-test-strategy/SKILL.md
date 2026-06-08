---
name: performance-test-strategy
description: "Set the performance strategy before testing: turn vague goals into falsifiable NFRs (percentile + threshold + load), model the real workload, link targets to the customer SLO, and choose the test type (load/stress/soak/spike) that answers the open question."
---

# Performance Test Strategy

## Start from a falsifiable target, not "fast"
Every NFR is a percentile + a threshold + the load it holds at — "p99 ≤ 200 ms at 5,000 req/s, 70/30 read/write", never "the API should be fast". A target with no load attached can't be passed, failed, or sized from. Set targets on p95/p99 (and max), never the average.

## Model the workload before any test
The traffic mix, arrival pattern, data distribution, cache warmth, and peak multiplier drive the result. Specify them first: request weights, open vs. closed arrival, steady vs. peak, data skew/cardinality, and the cache-warmth assumption. The workload model is the contract you hand to the load-testing-engineer.

## Link the target to the SLO, don't replace it
Your NFRs are the engineering targets that keep the customer SLO/error budget safe. Make the two consistent; the SLO itself is owned by `observability-sre`. Name which is latency-protected and which is throughput-protected — you can't max both.

## Choose the test type by the open question
Load proves the steady-state target; stress finds the knee; soak finds the slow leak/degradation; spike proves elasticity. Name the unanswered question and pick the test that answers it — one steady-state load run is not a performance sign-off.

## Output
A performance test plan: the NFR targets, the workload model, the test type(s) and sequence, the environment + data plan, and the pass/fail thresholds. Hand the test build to `load-testing-engineer`; route the SLO to `observability-sre`.
