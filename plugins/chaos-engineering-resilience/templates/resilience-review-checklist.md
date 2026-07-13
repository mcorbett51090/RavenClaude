# Resilience review checklist — <service / system name>

> A per-service resilience audit. Order matters: **FMEA first (name the failure modes), then confirm each pattern defends a named failure AND defends its own failure mode, then confirm it's been PROVEN under fault.**
> Resilience is **designed in, not tested in** — this checklist audits the design; a chaos experiment ([`chaos-experiment-plan.md`](chaos-experiment-plan.md)) proves it held.

**Service:** <name> · **Reviewer:** <resilience-architect> · **Date:** <date> · **Upstream deps:** <list> · **SLOs:** <the steady-state targets>

## 1. Failure-mode analysis (do this FIRST)
- [ ] **FMEA done** — failure modes enumerated per dependency/boundary
- [ ] **Ranked by blast radius × likelihood**
- [ ] **Single points of failure identified** — <list the SPOFs>
- **Top failure modes:** <1> · <2> · <3>

## 2. Bounding & retries
- [ ] **Timeout set on every remote call** (an unset timeout is infinite) — tuned to the dep's healthy p99
- [ ] **Retries only on idempotent calls**, and off the hot path for slow deps
- [ ] **Retries have exponential backoff + jitter + a budget** (or they're a self-inflicted DDoS)
- [ ] **Idempotency keys** guard side effects where retries/redelivery are possible

## 3. Containment
- [ ] **Circuit breaker** at the caller of each failure-prone dependency
- [ ] **Every breaker has a fallback** (a breaker with no fallback just fails faster)
- [ ] **Bulkheads** isolate thread/connection pools per dependency (or tenant) — sized
- [ ] **Load shedding / rate limiting** protects core capacity, prioritizing high-value work
- [ ] **Backpressure** with bounded queues + a shed path (no unbounded buffering)

## 4. Degradation
- [ ] **Graceful degradation / fallback** for each hard-dependency outage (reduced experience, never a blank page)
- [ ] **Fallback paths are themselves tested** (a stale/wrong fallback is its own failure)

## 5. Redundancy & DR
- [ ] **Multi-AZ** (and/or multi-region where the failure mode warrants it)
- [ ] **Failover** designed (active-active / active-passive) — and **rehearsed** (→ game day)
- [ ] **Explicit RTO / RPO targets** committed and costed (not "highly available" as an adjective)

## 6. Proven under fault (the design isn't "done" until it's proven)
- [ ] **Each critical pattern has a chaos experiment** proving it held under load + fault
- [ ] **Game day run** for the region/failover scenario (people + runbooks, not just systems)
- **Open experiments / gaps:** <link the chaos-experiment plans; list unproven patterns>

## Pattern → failure-mode map (summary)
| Failure mode | Pattern(s) placed | Boundary | Proven? (experiment) |
|---|---|---|---|
| <slow payment API cascades> | timeout + breaker + fallback + bulkhead | checkout→payment caller | <exp link / NOT YET> |
| <transient network blip> | retry + backoff + jitter + budget | <client> | <exp link / NOT YET> |
| <region loss> | multi-region + failover, RTO/RPO | <infra> | <game-day link / NOT YET> |

## Seams (not this checklist)
- **Steady-state metrics / SLOs / on-call:** observability-sre (prerequisite)
- **The pipeline / progressive delivery / rollback wiring:** devops-cicd
- **Load generation:** performance-engineering
- **The experiment that proves each pattern:** chaos-experiment-engineer
- **A real incident:** incident-response-dfir

**Sign-off:** <reviewer> · <date>
