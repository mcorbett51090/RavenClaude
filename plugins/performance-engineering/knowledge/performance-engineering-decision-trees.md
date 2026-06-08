# Performance Engineering — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the tool/project before quoting. Last reviewed: 2026-06-08._

Traverse before designing a performance test, choosing a workload model, or chasing a bottleneck.

## Decision Tree: Which performance test type answers the question?

The test type is chosen by the open question, not by habit. One run is not a performance test.

```mermaid
graph TD
  A[A performance question is open] --> B{What are you trying to learn?}
  B -- Does it hold the target at expected traffic? --> C[Load test: steady at expected + peak load; assert p95/p99/error-rate]
  B -- Where does it fall over? --> D[Stress test: ramp past expected to find the knee/saturation point]
  B -- Does it degrade over time? --> E[Soak test: steady load for hours; watch memory growth, latency creep, pool exhaustion]
  B -- Does it survive a sudden surge? --> F[Spike test: step from baseline to peak; measure error rate during + recovery after]
  C --> G{Target met with headroom below the knee?}
  G -- No --> D
  G -- Yes --> H[Move to soak + spike before sign-off - one run is not coverage]
```

_Load proves the target, stress finds the knee, soak finds the leak, spike proves elasticity. Cover all four before a performance sign-off._

## Decision Tree: Open or closed workload model?

The model is a first-class choice; the two diverge sharply under saturation and answer different questions.

```mermaid
graph TD
  A[Designing the workload] --> B{Does real traffic arrive independent of system speed?}
  B -- Yes, user/event-driven open arrival --> C[Open model: fix the ARRIVAL RATE req/s]
  B -- No, fixed clients looping with think time --> D[Closed model: fix the VIRTUAL USERS + think time]
  C --> E{Does the tool/executor correct for coordinated omission?}
  E -- No --> F[Risk: stalled generator never requests the worst latencies - tail is a lie. Use an arrival-rate executor + latency correction]
  E -- Yes --> G[Report real p95/p99/max at the fixed arrival rate]
  D --> H[Valid for closed systems batch workers, fixed connection pools - but it self-throttles and hides saturation on open traffic]
```

_Prefer an open arrival-rate model for user-facing traffic — a closed model throttles itself and hides the failure. Always name whether coordinated omission is corrected._

## Decision Tree: Triaging a bottleneck (USE/RED → profile → capacity)

Measure before you optimize. USE walks resources, RED watches requests; the flame graph names the hot path.

```mermaid
graph TD
  A[System is slow / near limit] --> B{Saturation rising on any resource? USE: util/sat/errors}
  B -- Yes, a resource is saturated --> C{Which resource?}
  C -- CPU --> D[On-CPU flame graph: name the hot path]
  C -- Memory/GC --> E[Allocation/heap profile: leak or GC-pause pressure]
  C -- IO/network/downstream --> F[Off-CPU profile: blocked on lock/IO/slow downstream]
  C -- DB --> G[Localize the query - route the fix to database-engineering]
  B -- No clear saturation --> H[RED on the request stream: rate/errors/duration - where does duration spike?]
  D --> I[Name the single highest-leverage fix; route to the owning plugin]
  E --> I
  F --> I
  H --> I
  I --> J{Need to size for more traffic?}
  J -- Yes --> K[Capacity: Little's law L=lambda*W + measured saturation point + failover/growth headroom]
  J -- No --> L[Re-run the load test after the fix to confirm + commit a new baseline]
```

_Profile first — the first bottleneck is almost never where you guessed. Saturation (a growing queue), not utilization, is the danger signal._

## Decision Tree: Is this result a real regression — and does it gate the release?

A latency number means nothing without a committed baseline and a threshold. "Feels slower" is not a finding; a p99 delta past the gate is.

```mermaid
graph TD
  A[A run finished - is it a pass?] --> B{Is there a committed baseline for this workload?}
  B -- No --> C[Not a regression check yet: commit this run as the baseline first, with env+data+model+tool pinned]
  B -- Yes --> D{Same workload model, data, env, and tool version as the baseline?}
  D -- No --> E[Not comparable - re-run reproducibly before comparing; an unpinned delta is noise]
  D -- Yes --> F{p95/p99 delta beyond the agreed threshold?}
  F -- No, within threshold --> G[Pass: record the run; refresh the baseline if intentionally faster]
  F -- Yes, p99 regressed --> H{Mean flat but tail moved?}
  H -- Yes --> I[Still a regression - the tail is the user-visible failure; block on the percentile not the mean]
  H -- No --> J[Block the release; profile the delta to localize the new bottleneck]
```

_A regression needs a committed baseline plus a percentile threshold; compare like-for-like or not at all. A p99 delta is real even when the mean is flat — gate on the tail._

## Decision Tree: The bottleneck is localized — who owns the fix?

This layer proves and localizes the constraint; it does not fix it in place. Name the constraint, then route the fix to the plugin that owns that craft.

```mermaid
graph TD
  A[Bottleneck localized + evidenced] --> B{What kind of constraint is it?}
  B -- A specific slow query / missing index / schema --> C[Route the fix to database-engineering: this plugin proved the DB is the bottleneck]
  B -- Browser paint: LCP / CLS / bundle / render path --> D[Route to frontend-engineering Core Web Vitals - server-side stays here]
  B -- A dependency that needs retry / bulkhead / circuit-breaker / backpressure --> E[Route to backend-engineering resilience past the knee]
  B -- The gap is a customer SLO / error budget / alerting --> F[Route to observability-sre: NFR targets link to the SLO]
  B -- Need more nodes / autoscaling / instance sizing --> G[Supply the capacity math + headroom; cloud-native-kubernetes implements HPA/sizing]
  B -- Prod-derived test data could carry PII --> H[Mandatory security-reviewer + data-governance-privacy de-identification]
  B -- It is genuinely a system throughput/latency/capacity job --> I[Owned here: re-run the load test after the fix and commit a new baseline]
```

_Prove the number; let the owner move it. Tuning the query, rewriting the front-end, or designing the retry policy here drifts the domain boundary and skips the owning team's review._

---

## Capability map (2026, `[verify-at-build]`)

| Layer | Options | Notes |
|---|---|---|
| Load testing (scripted) | k6 (JS, open + closed executors), Gatling (Scala/Java DSL), Locust (Python) | k6 has first-class arrival-rate executors that correct coordinated omission `[verify-at-build]` |
| Load testing (GUI/protocol-heavy) | Apache JMeter, Gatling | JMeter is closed-model by default; mind coordinated omission on open traffic `[verify-at-build]` |
| CPU profiling (JVM) | async-profiler, JFR (Java Flight Recorder) | async-profiler does on- and off-CPU + allocation flame graphs `[verify-at-build]` |
| CPU profiling (Go) | `pprof` (built-in) | CPU, heap, block, mutex profiles → flame graphs `[verify-at-build]` |
| CPU profiling (native/Linux-wide) | `perf`, eBPF (bcc/bpftrace), `flamegraph` (Brendan Gregg) | System-wide + off-CPU; eBPF for low-overhead production profiling `[verify-at-build]` |
| Continuous/production profiling | Parca, Pyroscope (Grafana), Datadog/other APM profilers | Always-on flame graphs in prod; lower overhead than dev profilers `[verify-at-build]` |
| Memory/leak detection | heap profilers (lang-specific), valgrind/massif (native) | Soak-test pairing: watch RSS/heap growth over hours `[verify-at-build]` |
| Tracing / RED metrics | OpenTelemetry, APM (request rate/errors/duration) | RED method source; localizes duration spikes per service `[verify-at-build]` |

_Method references: **USE** (Brendan Gregg) — for every resource, check Utilization / Saturation / Errors. **RED** (Tom Wilkie) — for every request stream, track Rate / Errors / Duration. **Little's law** — `L = λ·W` (concurrency = arrival rate × mean service time), the basis for capacity from a measured saturation point. **Coordinated omission** (Gil Tene) — a load generator that stalls waiting on a slow response never requests the worst-case latencies, so they go unrecorded and the reported tail is optimistic. Re-verify any tool/version specific before quoting it to a consumer._
