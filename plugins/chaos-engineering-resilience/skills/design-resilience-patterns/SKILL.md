---
name: design-resilience-patterns
description: "Pick and place the right resilience patterns for a given failure mode — the timeout / retry+backoff+jitter+budget / circuit-breaker / bulkhead / load-shedding / graceful-degradation / fallback / idempotency / backpressure decision. Start from an FMEA, choose the pattern that defends the NAMED failure, and defend the pattern's OWN failure mode. Reach for this when the user asks 'what do we add so a slow/failing dependency doesn't take us down?', 'is a naked retry safe here?', or 'where are our single points of failure?'. Used by `resilience-architect` (primary)."
---

# Skill: design-resilience-patterns

> **Invoked by:** `resilience-architect` (primary). Also consulted by `chaos-experiment-engineer` to understand which pattern a hypothesis is really testing.
>
> **When to invoke:** "a slow/failing dependency takes the page down — what do we add?"; "is a retry safe here?"; "circuit breaker or bulkhead?"; "where are our SPOFs?"; any move on the design side of surviving failure.
>
> **Output:** an FMEA-grounded pattern set — each pattern mapped to the named failure it defends, placed at the right boundary, with the pattern's OWN failure mode defended — captured in the resilience-review checklist.

## Procedure

1. **Frame the system and the failure history.** Architecture, dependency graph, traffic, SLOs, and the failures actually seen (cascades, retry storms, timeouts). The pattern set must defend *this* system's real failure modes, not a generic checklist.
2. **Run the FMEA first — start from the failure, not the pattern.** Enumerate failure modes per dependency/boundary; rank by **blast radius × likelihood**; mark the single points of failure. A pattern that doesn't defend a named, ranked failure is decoration — cut it.
3. **Choose the pattern via [`../../knowledge/chaos-engineering-resilience-decision-tree.md`](../../knowledge/chaos-engineering-resilience-decision-tree.md) Tree C.** Match the failure mode to the pattern: **transient blip → retry + backoff + jitter + budget** (idempotent calls only); **slow dependency → timeout + circuit breaker** (bound the wait, stop hammering a sick service); **noisy neighbor / resource contention → bulkhead + load shedding** (isolate pools, shed low-priority work); **hard outage → fallback + graceful degradation** (serve a reduced experience, not a blank page). Layer them — a slow dependency usually needs timeout + breaker + fallback together.
4. **Defend each pattern's OWN failure mode — this is the step people skip.** A retry gets backoff + jitter + a budget (or it's a self-inflicted DDoS). A circuit breaker gets a fallback (or it just fails faster). A timeout gets an actual value (an unset timeout is infinite). A bulkhead gets sized pools. Backpressure gets a shed path. Idempotency keys protect the retries. Name the defense for every pattern you place.
5. **Place the pattern at the right boundary.** Client-side vs server-side, per-dependency vs per-tenant, edge vs service mesh. A circuit breaker belongs at the caller of the sick dependency; rate limiting at the edge; bulkheads around the shared resource. Wrong boundary = the pattern doesn't fire when it matters.
6. **Frame redundancy & DR as a costed target.** If the failure mode is a zone/region loss, the answer is redundancy (multi-AZ/region, active-active vs failover) tied to explicit RTO/RPO — say the cost. Capture the audit in [`../../templates/resilience-review-checklist.md`](../../templates/resilience-review-checklist.md).
7. **State the seams, flip conditions, and the experiment that proves it.** The metrics/SLO stack → `observability-sre`; load → `performance-engineering`; the pipeline → `devops-cicd`. Every pattern is a *claim* — name the chaos experiment (`chaos-experiment-engineer`) that would prove it, and the 1-2 facts that would change the design.

## Worked example

> User: "Our checkout page calls a third-party payment API synchronously. When that API gets slow, checkout threads pile up waiting, the pool exhausts, and the *whole* site goes down — even pages that don't touch payments. We 'fixed' it by adding a retry. It got worse. What do we actually do?"

- **FMEA read:** the failure mode is a **slow dependency causing resource exhaustion that cascades** (blast radius: entire site; likelihood: high — third-party APIs degrade routinely). This is a SPOF: one slow dependency takes everything down.
- **The retry made it worse — predictably.** Retrying a *slow* dependency multiplies load on an already-sick service and holds threads longer. A naked retry here is a self-inflicted DDoS. Tree C: a slow dependency is **not** a retry case.
- **Pattern set (layered):**
  - **Timeout** on the payment call — a real, aggressive deadline so a slow call fails fast instead of holding a thread.
  - **Circuit breaker** at the checkout→payment boundary — after N failures/timeouts, open the breaker and stop hammering the sick API.
  - **Fallback / graceful degradation** — when the breaker is open, queue the order for async payment capture and show "payment processing," rather than blocking. *A breaker with no fallback just fails faster.*
  - **Bulkhead** — isolate the payment call's thread/connection pool so its exhaustion can never starve the pages that don't touch payment. This removes the cascade — the SPOF becomes a contained, degraded feature.
- **Retry — but bounded:** only for the idempotent capture retry path, with exponential backoff + jitter + a budget and an idempotency key, off the synchronous path.
- **Prove it:** this whole set is a hypothesis. Hand it to `chaos-experiment-engineer`: inject 2s of latency on the payment API under load, hypothesize checkout stays within SLO because the breaker opens and the bulkhead contains it, with an abort condition on site-wide error rate.
- **Seam:** the SLO/error-rate signals the breaker and abort read → `observability-sre` (prerequisite); realistic checkout load → `performance-engineering`.

## Guardrails

- **Start from the FMEA, never the pattern** — a pattern that doesn't defend a named, ranked failure mode is decoration.
- **A retry without backoff + jitter + a budget is a self-inflicted DDoS** — and never retry a *slow* or non-idempotent dependency on the hot path.
- **A circuit breaker with no fallback just fails faster** — always pair the breaker with graceful degradation.
- **An unset timeout is an infinite timeout** — every remote call gets a real deadline.
- **Layer patterns; place them at the right boundary** — a slow dependency usually needs timeout + breaker + fallback + bulkhead together, at the caller.
- **Redundancy is a costed RTO/RPO target, not the adjective "highly available."**
- **Every pattern is a claim to be proven** — resilience is designed here, but `chaos-experiment-engineer` verifies it held; a design never ships as "done" unproven.
- **Volatile library/tooling defaults carry a retrieval date** and are re-verified before a production commitment. See [`../../knowledge/chaos-engineering-resilience-patterns-2026.md`](../../knowledge/chaos-engineering-resilience-patterns-2026.md).
