# Performance Test Plan

> Output of `performance-architect` / `load-testing-engineer` (the `performance-test-strategy` + `load-test-design` skills).
> A target with no load, a workload with no model, or a run with no threshold is not ready to execute.

## 1. Targets (NFRs)

| Capability | Percentile | Threshold | Holds at (load) | Objective | Linked SLO |
|---|---|---|---|---|---|
| <e.g. checkout API> | p99 | <= 250 ms | 3,000 req/s, 80/20 r/w | latency-protected | <SLO link / route to observability-sre> |
| | p95 | | | throughput-protected | |

_Every target is a percentile + threshold + the load it holds at. No averages._

## 2. Workload model

- **Request mix:** <endpoint weights, read/write ratio>
- **Arrival pattern:** <open arrival-rate / closed VUs+think-time; steady / peak>
- **Peak multiplier:** <e.g. 4x average for a sale window>
- **Data distribution:** <cardinality, skew, size>
- **Cache warmth:** <warm-as-prod / cold — stated, not assumed>

## 3. Test types & sequence

| Test type | Question it answers | Load profile | Pass/fail threshold |
|---|---|---|---|
| Load | Holds the target at expected + peak? | <ramp → steady at target rate> | <p99/p95/error-rate> |
| Stress | Where's the knee? | <ramp past expected to saturation> | <find + report the knee> |
| Soak | Degrades over time? | <steady for N hours> | <no mem growth / latency creep> |
| Spike | Survives a surge? | <step baseline → peak> | <error rate + recovery time> |

## 4. Environment & data plan

- **Environment (pinned):** <prod-like infra, versions, network origin of load>
- **Test data:** <generated/synthesized; representative skew> — **no prod PII** (route de-identification to security-reviewer if mirroring prod)
- **Tool + version:** <k6 / Gatling / Locust / JMeter @ version>
- **Coordinated omission:** <executor named; corrected? yes/no>
- **Baseline:** <committed baseline run id for regression comparison>

## 5. Build handoff

| What | Routed to |
|---|---|
| The customer SLO / error budget | `observability-sre` |
| The slow query a test localizes | `database-engineering` |
| The browser-side paint | `frontend-engineering` |
| Resilience past the saturation point | `backend-engineering` |
| De-identifying prod-derived data | `security-engineering` / `data-governance-privacy` |

---

```
Status: ...
Files changed: ...
Workload modeled: ...
Target vs. measured: ...
Handoff to fix owner: ...
Open questions: ...
Grounding checks performed: ...
```
