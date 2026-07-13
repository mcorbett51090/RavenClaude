# Knowledge — Chaos & resilience patterns (2026)

> **Last reviewed:** 2026-07-13 · **Confidence:** High on the durable concepts (the Principles of Chaos Engineering, the failure taxonomy, the steady-state hypothesis, blast-radius minimization, the resilience patterns, continuous verification); **Medium on the dated landscape — fault-injection tool features, cloud fault-API capabilities, and managed-chaos-service offerings are volatile and carry retrieval dates below.**
> The reference both agents read when working any experiment or resilience decision: the chaos principles, the failure taxonomy, the tooling landscape, GameDay practice, the resilience patterns (timeouts, retries+jitter, circuit breakers, bulkheads, load shedding), and continuous verification.

The team's discipline: **define the steady state and a falsifiable hypothesis before any experiment; minimize and expand blast radius deliberately (staging → prod); enforce the SAFETY spine on every production run; and attach a retrieval date to every volatile tool/API claim.**

---

## The Principles of Chaos Engineering

Chaos engineering is **the discipline of experimenting on a system to build confidence in its capability to withstand turbulent conditions in production.** The five principles that make it an *experiment* rather than an outage:

1. **Build a hypothesis around steady-state behavior.** Define "healthy" as a measurable output metric (business or system) with a normal band, and hypothesize that it *stays within band* under a fault. The steady state — not the internals — is what you assert about.
2. **Vary real-world events.** Inject faults that model what actually happens in production — hardware failures, network latency/loss, dependency failures, region loss, resource exhaustion, clock skew — not contrived faults nobody experiences.
3. **Run experiments in production** (with guardrails). Only production has the real traffic, real state, and real dependencies; a staging-only result under-samples reality. **This team's rule:** production runs happen *only* behind the SAFETY spine (hypothesis + blast-radius limit + abort/rollback), and *only* after the same experiment passed in staging.
4. **Minimize blast radius.** Contain the potential harm — the first run is the smallest that can still falsify the hypothesis (one pod, one AZ, a small % of traffic), and you expand deliberately only after a smaller run passed.
5. **Automate experiments to run continuously.** Manual experiments don't scale and their results decay as the system changes — automate them into CI/CD or a schedule so resilience is *continuously verified*, not proven once.

> **The through-line:** an experiment is a controlled test of a hypothesis. Remove the hypothesis, the steady-state metric, the blast-radius limit, or the ability to abort — and you've removed what separates chaos *engineering* from a self-inflicted outage.

---

## The steady-state hypothesis — the heart of an experiment

- **Steady state** = the normal operating behavior of the system expressed as a **measured metric** with a band (e.g. checkout success rate ≥ 99.5%, p99 latency ≤ 300 ms, orders/min within ±10% of baseline). Prefer a **customer/business-facing output metric** over an internal one — it's what "the system works" actually means.
- **The hypothesis** = "**under fault X, steady-state metric Y stays within band Z**." It must be **falsifiable** — the experiment can *refute* it.
- **Precondition:** you can only detect a deviation you've instrumented. Confirm the observability (metrics/traces/logs to watch Y in real time) exists *before* injecting — that telemetry is `observability-sre`'s domain and a hard precondition here.
- **Refuted ≠ failure.** A refuted hypothesis is the *point* — it found a resilience gap cheaply, before an outage did. The fix is a resilience pattern (below), not "make the experiment gentler."

---

## The failure taxonomy — where real-world faults come from

| Class | Real-world faults to inject | Resilience it stresses |
|---|---|---|
| **Resource** | CPU/memory pressure, disk full, FD/thread-pool exhaustion | Load shedding, bulkheads, autoscaling, graceful degradation |
| **Network** | Latency injection, packet loss, DNS failure, network partition / split-brain | Timeouts, retries+jitter, circuit breakers |
| **State** | Clock skew, stale/corrupt cache, replica lag, data inconsistency | Idempotency, reconciliation, cache fallback, read-repair |
| **Dependency** | A downstream service slow / erroring / timing out; a poisoned response | Timeouts, circuit breakers, fallbacks, bulkheads |
| **Region / zone** | AZ loss, full region failure, control-plane outage | Multi-AZ/region failover, replication, degraded-mode operation |

Rank candidates by **likelihood × blast radius × detectability** and prove the highest-value ones first.

---

## Fault-injection tooling landscape (dated — volatile, re-verify before quoting)

- **Chaos Mesh** — CNCF, Kubernetes-native; injects pod/container/node kills, network faults, stress, and IO faults as Kubernetes CRDs, with a dashboard and workflow orchestration. _(Retrieved 2026-07-13; feature set evolves — verify.)_
- **LitmusChaos** — CNCF, Kubernetes-native; a chaos-experiment framework with a hub of reusable experiments (ChaosHub) and GitOps-style declarative chaos. _(Retrieved 2026-07-13.)_
- **AWS Fault Injection Service (AWS FIS)** — managed AWS fault-injection with stop conditions tied to CloudWatch alarms and actions across EC2/ECS/EKS/RDS and more. _(Cloud action coverage changes — retrieval-date any specific action, 2026-07-13.)_
- **Azure Chaos Studio** — managed Azure fault injection (agent-based and service-direct faults) with experiments and targets. _(Retrieved 2026-07-13; capability coverage changes — verify.)_
- **Gremlin** — commercial SaaS chaos platform; broad target support, a fault catalog, and built-in blast-radius/safety controls and a "halt" button. _(Terms & features volatile — verify before quoting.)_
- **Steadybit** — commercial chaos/resilience platform; experiment builder, weak-point discovery, and safety guardrails. _(Retrieved 2026-07-13.)_
- **Chaos Toolkit** — open-source, declarative experiments (JSON/YAML) with a steady-state hypothesis block built into the spec, driving many providers via extensions. _(Retrieved 2026-07-13; you assemble the safety controls yourself.)_

> **Choosing:** match the tool to the **fault class + platform**, and to how much of the **SAFETY spine it provides for you** (managed services and SaaS platforms build in stop conditions and blast-radius controls; open tools leave more to you). Tool feature parity shifts — carry a retrieval date on any specific capability claim.

---

## GameDay practice

- **What it is:** a scheduled, facilitated exercise where a team deliberately injects failures into a system (in staging or, behind the SAFETY spine, production) to validate resilience, exercise runbooks, and train the on-call response — a human-in-the-loop complement to automated experiments.
- **Roles:** a **facilitator** (runs the plan, calls the abort), an **operator** (injects the fault / executes the runbook), one or more **observers** (watch the steady-state metric and system behavior), and a **scribe** (records the timeline, findings, and actions).
- **The output is a fix list.** A GameDay's deliverable is the **prioritized action items** — the resilience gaps found and assigned — plus validated (or corrected) runbooks. A GameDay that ends without assigned actions spent the risk for adrenaline.
- **Pre-flight (the SAFETY spine):** every scenario has a hypothesis, a blast-radius limit, and an abort/rollback — the facilitator confirms all three before injecting.

---

## Resilience patterns — the fixes for a refuted hypothesis

Chaos experiments *reveal* whether these exist and work; they don't create resilience. The fix for a failed experiment is the missing pattern.

- **Timeouts** — every remote call has a bound; **each caller's timeout is shorter than its callee's**, or one slow dependency hangs the whole call graph by exhausting threads/connections upstream.
- **Retries with exponential backoff + jitter + a budget** — naive retries amplify a partial failure into a full one (retry storms / thundering herd). Always back off, add jitter to de-synchronize, cap attempts, and enforce a retry budget.
- **Circuit breakers** — stop calling a dependency that's failing (open the circuit), fail fast, and periodically probe to recover (half-open). Prevents a dead dependency from consuming caller resources and gives it room to recover.
- **Bulkheads** — isolate resources (thread pools, connection pools, queues) per dependency or tenant so one saturated dependency can't sink the whole service — the ship-compartment metaphor.
- **Load shedding & rate limiting** — under overload, reject or degrade low-priority work to protect the core; better a shed request than a collapsed service.
- **Fallbacks & graceful degradation** — a cached/default/degraded response when a dependency is down, so the user gets *something* instead of an error.
- **Idempotency & reconciliation** — safe retries and eventual-consistency repair for state faults.

> **Composition matters:** timeouts + retries+jitter + circuit breakers work *together* — a timeout bounds the wait, the circuit breaker stops retrying a dead dependency, and backoff+jitter keeps the retries from becoming the outage.

---

## Continuous verification

- **What it is:** running resilience experiments **automatically and repeatedly** — as a CI/CD pipeline stage, on a schedule, or triggered by a deploy — so a regression in a timeout, retry policy, circuit breaker, or failover is caught by an *experiment*, not by an outage.
- **The guardrail:** the automated steady-state check that **halts the pipeline (or the experiment)** on breach — continuous verification without an automated abort is an unstoppable scheduled outage.
- **Why it matters:** a resilience property proven once decays as the system changes; only continuous verification keeps the confidence current.

---

## Provenance

- Durable concepts (the Principles of Chaos Engineering, the steady-state hypothesis, the failure taxonomy, blast-radius minimization and the staging→prod progression, the resilience patterns — timeouts, retries+jitter, circuit breakers, bulkheads, load shedding, fallbacks — GameDay practice, and continuous verification) are consensus chaos/resilience engineering practice, reviewed 2026-07-13 — **High confidence on the concepts**.
- The fault-injection tooling landscape (**Chaos Mesh, LitmusChaos, AWS FIS, Azure Chaos Studio, Gremlin, Steadybit, Chaos Toolkit**) is a **2026-07 snapshot** — features, cloud fault-API coverage, and commercial terms are volatile and carry the retrieval dates above; re-verify with `ravenclaude-core/deep-researcher` before pinning in a client deliverable.
- **The SAFETY spine (no production experiment without a hypothesis, a blast-radius limit, and an abort/rollback) is this team's hard, non-negotiable rule** — an uncontrolled experiment is an outage, and the whole legitimacy of chaos engineering rests on the experiment being controlled.
