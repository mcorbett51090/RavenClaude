# Capacity & Bottleneck Report

> Output of `profiling-and-capacity-engineer` (the `profiling-and-bottleneck-triage` skill). A bottleneck with no
> profile, a capacity number with no headroom, or a regression claim with no baseline is not ready to act on.

## 1. Measured behavior

- **Workload it was measured at:** <mix / arrival rate / data shape — the result only holds here>
- **Percentiles:** p50 <…> / p95 <…> / p99 <…> / max <…> _(never the average)_
- **Throughput:** <req/s sustained>
- **Saturation point / knee:** <the req/s where latency runs away>

## 2. Bottleneck localization

| Method | Finding |
|---|---|
| USE (utilization/saturation/errors) | <which resource is saturated — CPU / memory / IO / lock / pool> |
| RED (rate/errors/duration) | <where duration spikes in the request stream> |
| Flame graph (on-CPU) | <the hot path> |
| Flame graph (off-CPU) | <thread blocked on lock / IO / downstream> |

- **The single highest-leverage fix:** <named change>
- **Routed to:** <database-engineering / frontend-engineering / backend-engineering>

## 3. Capacity plan

- **Little's law:** `L = λ·W` → concurrency = <arrival rate> × <mean service time> = <L>
- **Per-instance saturation point (measured):** <req/s per instance below the knee>
- **Instances for target load:** <count>
- **Headroom:** <failover (survive N node loss) + growth (peak multiplier)> — **not planned to 100% utilization**
- **Routed to:** `cloud-native-kubernetes` / cloud plugin for the HPA/instance config

## 4. Regression verdict (if applicable)

| | Baseline | This run | Delta | Threshold | Verdict |
|---|---|---|---|---|---|
| p95 | | | | | <pass/fail> |
| p99 | | | | | <pass/fail> |

- **Flame-graph diff (what changed):** <localized cause>
- **Gate recommendation:** <block / allow>

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
