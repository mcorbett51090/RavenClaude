# chaos-engineering-resilience

> The **resilience-by-design + prove-it-with-chaos layer** for Claude Code — the engineering team that answers *"how do we make this distributed system survive failure?"* Two agents: the **resilience-architect** (the DESIGN side — failure-mode analysis, resilience patterns, the maturity gate, and capacity/redundancy & DR) and the **chaos-experiment-engineer** (the EXPERIMENT + VERIFICATION side — hypothesis-driven experiments, blast-radius containment, game-day facilitation, and verifying the pattern actually held).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "A slow / failing dependency takes our whole page down — what do we add?" | An FMEA-grounded pattern set (timeout + circuit breaker + fallback + bulkhead, not a naked retry), placed at the right boundary, with each pattern's own failure mode defended |
| "Is a retry safe here?" | The idempotency + backoff + jitter + budget check — and a "no, this is a slow-dependency case" when a retry would be a self-inflicted DDoS |
| "Where are our single points of failure?" | A dependency map + FMEA ranking failure modes by blast radius × likelihood, the SPOFs called out, and the pattern or redundancy that removes each |
| "Are we mature enough to run chaos at all?" | A GO / NOT-YET verdict from the maturity gate (steady-state observability? SLOs? on-call?) with the exact prerequisites to close first |
| "Design / run a chaos experiment for X." | A full experiment plan: steady-state → falsifiable hypothesis → smallest disproving blast radius → the fault → automatic abort conditions → the observation that confirms or refutes |
| "Which fault do we inject first?" | A prioritized target (highest-blast dependency vs most-likely fault), the fault type from the taxonomy, and the smallest scope that can still disprove the hypothesis |
| "Run us a game day." | A game-day plan: scenario, roles, comms, abort criteria, a scoring rubric, and a follow-up remediation backlog — people and runbooks tested, not just systems |
| "Did the circuit breaker / failover actually hold?" | A verification read: metrics correlated to the injection window, load + fault combined, and a clear held / did-not-hold verdict with the remediation backlog |
| "Do we need multi-region, and what RTO/RPO?" | A costed redundancy/DR posture tied to explicit RTO/RPO targets, with the conditions that would change it |

**Three rules it never breaks:** *resilience is designed in, not tested in* (chaos proves the design; it never creates it), *no chaos without steady-state observability* (immature observability = you're just breaking prod), and *no experiment ships without an abort condition* (an experiment with no automatic halt is an outage).

## What's inside

- **2 agents** — `resilience-architect` (FMEA/SPOFs, the resilience-pattern set, the maturity gate, capacity/redundancy & DR RTO/RPO) and `chaos-experiment-engineer` (hypothesis-driven experiment design, blast-radius containment & automatic abort, game-day facilitation, the fault-injection taxonomy, and did-it-hold verification).
- **3 skills** — `design-resilience-patterns`, `run-chaos-experiment`, `plan-game-day`.
- **2 knowledge files** — a Mermaid decision tree (the maturity gate, which failure to inject first, which pattern for a failure mode) and a 2026 patterns reference (the resilience-pattern catalog, the principles of chaos, the fault-injection taxonomy, a dated tooling/service snapshot, and the anti-patterns).
- **2 templates** — a chaos-experiment plan and a per-service resilience-review checklist.

## Where it sits among the reliability plugins

```
observability-sre        →  the METRICS / SLO / ALERTING / ON-CALL platform  ("measure & watch 'healthy'; page when it breaks")  — a HARD PREREQUISITE
devops-cicd              →  the DEPLOY / RELEASE pipeline                     ("ship it — canary / blue-green / rollback")
performance-engineering  →  LOAD & capacity                                  ("how much traffic can it take?")
incident-response-dfir   →  the REAL incident                                ("it's actually on fire — respond & investigate")
chaos-engineering-resilience (HERE)  →  DESIGN survival + PROVE it with chaos  ("build it to survive failure; then break it on purpose, safely, to prove it does")
```

This plugin **designs and proves resilience** and **consumes** those disciplines rather than replacing them: it reads the steady-state signals `observability-sre` owns (a hard prerequisite), runs *under* the load `performance-engineering` generates, relies on the rollback `devops-cicd` wires, and hands a real incident to `incident-response-dfir` — while owning the resilience-*specific* work (failure-mode analysis, pattern design, the maturity gate, hypothesis-driven experiments, blast-radius control, game days) that none of them cover.

## Domain stance

Design-first and hypothesis-driven: resilience is designed in (FMEA → timeouts, retries with backoff + jitter + budget, bulkheads, circuit breakers, load shedding, graceful degradation, fallbacks, idempotency, backpressure, redundancy/failover with RTO/RPO), then *proven* with the smallest disproving chaos experiment — never created by it. No chaos without steady-state observability; every experiment has a falsifiable hypothesis, the smallest blast radius, and an automatic abort; verification correlates metrics to the injection window under real load. Fault-injection tooling and managed-chaos-service specifics are named generically with retrieval dates — re-verify before a production commitment.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install chaos-engineering-resilience@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
