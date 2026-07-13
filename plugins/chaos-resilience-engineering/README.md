# chaos-resilience-engineering

> The **resilience team** for Claude Code — the two agents that prove a distributed system survives real-world failure *safely*, and answer *"what failure should we prove, and how do we inject it without causing the outage we're trying to prevent?"* Two agents: the **resilience-architect** (decides WHY & WHAT — steady-state hypothesis, failure-mode & dependency analysis, blast-radius design, resilience SLOs, the GameDay program, reading results into fixes) and the **chaos-experiment-engineer** (builds & runs HOW — fault-injection tooling, safety/abort/rollback, staging→prod progression, CI/CD continuous verification).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "We want to start chaos engineering — where do we begin?" | A scoped program: the steady-state hypothesis, the failure modes worth proving first (FMEA-style, ranked), the blast-radius and environment plan, and the first experiment to run |
| "Define our steady state / what does 'healthy' mean for this service?" | A measured steady-state metric (e.g. checkout success rate) with a normal band and the observability needed to detect a deviation, plus the falsifiable hypothesis to test it |
| "How do I inject a dependency timeout / kill a pod / drop a region — safely?" | A fault-injection experiment: the tool (Chaos Mesh / AWS FIS / Gremlin / …), the **blast-radius limit, abort condition, and rollback**, and the staging→prod progression |
| "Our retries are hammering a failing dependency during outages." | A resilience-pattern fix: retries with exponential backoff + jitter + a budget, a circuit breaker, and a timeout — with an experiment to prove it works |
| "Run a GameDay for the checkout service." | A GameDay runbook: objective, roles, scenarios from the failure taxonomy, the SAFETY pre-flight, and the prioritized fix list it must produce |
| "Wire chaos into our pipeline so resilience doesn't regress." | A continuous-verification design: which experiments run in CI/CD or on a schedule, their guardrails, and how a regression halts the pipeline |

**Rules it never breaks:** *no hypothesis, no experiment* (a fault with no steady-state hypothesis is an intentional outage, not a learning), *minimize and expand the blast radius deliberately* (smallest run first, staging before prod), and *resilience is designed in, not injected in* (the fix for a failed experiment is a resilience pattern, not running the experiment less). And one **SAFETY rule it always enforces**: **no experiment runs against production without a stated steady-state hypothesis, an explicit blast-radius limit, and an abort/rollback condition.**

## What's inside

- **2 agents** — `resilience-architect` (WHY & WHAT: steady-state hypothesis, failure-mode & dependency analysis, blast-radius design, resilience SLOs, the GameDay program, reading results into fixes) and `chaos-experiment-engineer` (HOW & RUN: fault-injection tooling, safety/abort/rollback, staging→prod progression, CI/CD continuous verification).
- **3 skills** — `design-steady-state-and-hypothesis`, `run-fault-injection-experiment`, `run-gameday-program`.
- **2 knowledge files** — a Mermaid chaos-resilience decision tree (hypothesis-design vs failure-mode-selection vs blast-radius/environment vs tooling vs GameDay-vs-automated, with the SAFETY gate) and a 2026 chaos-resilience-patterns reference (the Principles of Chaos Engineering, the failure taxonomy, the fault-injection tooling landscape, GameDay practice, the resilience patterns, and continuous verification).
- **2 templates** — a chaos-experiment design record (hypothesis, steady-state, fault, blast-radius, abort conditions, rollback, observations, result, action items) and a GameDay runbook.

## Where it sits

```
observability-sre         →  detect failure / on-call / SLOs & telemetry IN PROD      ("SEE it & RESPOND")
performance-engineering    →  throughput / latency / cost tuning under load            ("make it FAST")
qa-test-automation         →  functional correctness / does the feature work           ("is it RIGHT")
chaos-resilience-eng (HERE) →  prove it survives failure, safely, before the incident  ("does it SURVIVE failure")
```

This plugin proves a system's **resilience to failure** *before* the outage — the steady-state hypothesis, the fault injection, the blast-radius safety, the resilience patterns, continuous verification — and stays clear of *detecting/responding* to a live incident (observability-sre), *speed/cost tuning* (performance-engineering), and *feature correctness* (qa-test-automation). Note: `observability-sre` is also a **precondition** — you cannot run a chaos experiment without the telemetry to detect the deviation.

## Domain stance

Concept-first (the steady-state hypothesis, the failure taxonomy, blast-radius minimization, the SAFETY spine, the resilience patterns — timeouts, retries+jitter, circuit breakers, bulkheads, load shedding — and continuous verification), fluent across the fault-injection tooling (**Chaos Mesh, LitmusChaos, AWS FIS, Gremlin, Steadybit, Azure Chaos Studio, Chaos Toolkit**) and grounded in the **Principles of Chaos Engineering**. Fault-injection tool feature sets, cloud fault-API capabilities, and managed-chaos-service offerings are **volatile** — every such claim carries a **retrieval date**. And the hard rule: **no production experiment without a hypothesis, a blast-radius limit, and an abort/rollback condition** — chaos engineering's legitimacy rests on the experiment being *controlled*.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install chaos-resilience-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
