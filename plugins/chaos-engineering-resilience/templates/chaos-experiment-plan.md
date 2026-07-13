# Chaos experiment plan — <system / experiment name>

> The plan for a single hypothesis-driven chaos experiment. Order matters:
> **maturity gate → steady state → hypothesis → smallest blast radius → abort condition → inject → observe → result → remediation.**
> An experiment with **no abort condition is an outage**. No injection until the maturity gate passes.
> Pairs with [`resilience-review-checklist.md`](resilience-review-checklist.md) (the design the hypothesis tests).

**Owner:** <chaos-experiment-engineer> · **Date:** <date> · **Pattern under test:** <circuit breaker / fallback / failover / …> · **Status:** planned / running / held / did-not-hold / aborted

## 0. Maturity gate (must PASS before injecting — Tree A)
- [ ] **Steady-state observability** present (can measure "healthy" in real time)
- [ ] **SLOs / steady-state metrics** defined and agreed
- [ ] **On-call ready** and **automatic abort/rollback** wired
- [ ] **Resilience pattern designed in** (this experiment PROVES it; it does not create it)
- **Verdict:** GO / NOT-YET — <if not-yet, the prerequisite to close first + owner (often observability-sre / resilience-architect)>

## 1. Steady state
- **Metric(s) that define "healthy":** <e.g. checkout success ≥ 99.5%, order-service p99 ≤ 800ms>
- **Measurement window:** <e.g. 5-minute rolling>
- **Baseline (pre-injection):** <the observed healthy numbers>

## 2. Hypothesis (falsifiable)
> "When **\<fault\>**, **\<steady-state metric\>** stays within **\<bound\>** because **\<resilience pattern\>**."
- <write it here — it must be disprovable; "the system will be fine" is not a hypothesis>

## 3. Fault & blast radius
- **Fault type (taxonomy):** latency / error / resource-exhaustion / dependency-outage / network-partition / zone-failure
- **Parameters:** <e.g. +2000ms latency on the payment dependency>
- **Why this first (Tree B):** highest-blast dependency / most-likely fault
- **Smallest disproving scope:** <one instance / one cell / staging> → widen only after it holds
- **Environment:** staging → cell (~_%) → region

## 4. Abort condition (DEFINE BEFORE INJECTING)
- **Automatic halt when:** <steady-state breach, e.g. checkout success < 99% for 60s · error-budget burn · site error rate > baseline + 2%>
- **Rollback / restore action:** <how the fault is removed automatically>
- **Human abort:** <who can call it and how>

## 5. Method
- **Load profile (inject UNDER load):** <realistic traffic — performance-engineering generates it>
- **Injection window:** <start–end timestamps>
- **What we observe & how we correlate:** <the metric tied to the injection window — "nothing broke" is not a pass>

## 6. Result
- **Verdict:** HELD / DID-NOT-HOLD / ABORTED
- **Evidence:** <the steady-state metric read against the injection window, under load — link the dashboard/graph>
- **What the pattern actually did:** <e.g. breaker opened at t+8s, fallback served>

## 7. Remediation backlog (if it didn't hold, or aborted)
| Finding | Severity | Owner | Fix |
|---|---|---|---|
| <e.g. async-capture queue backed up under load> | <high> | resilience-architect | <size queue / add backpressure, retest> |

## Seams (not this plan)
- **Steady-state signals / SLOs / on-call:** observability-sre (prerequisite)
- **Load generation:** performance-engineering
- **The resilience-pattern design gap:** resilience-architect
- **A real, customer-impacting incident:** incident-response-dfir (stop the experiment; run the incident)

**Sign-off:** <reviewer> · <date>
