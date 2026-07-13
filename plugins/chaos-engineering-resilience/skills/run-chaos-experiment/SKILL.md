---
name: run-chaos-experiment
description: "Run the full chaos-experiment loop safely — steady-state definition → falsifiable hypothesis → the smallest disproving blast radius → inject a fault from the taxonomy → observe (metrics correlated to the injection window, under load) → abort-or-learn → remediate. Gate on the maturity check first (no steady-state observability = no experiment) and never inject without an automatic abort condition. Reach for this when the user asks 'design/run a chaos experiment for X', 'which fault do we inject first?', or 'did the resilience pattern actually hold?'. Used by `chaos-experiment-engineer` (primary)."
---

# Skill: run-chaos-experiment

> **Invoked by:** `chaos-experiment-engineer` (primary). The `resilience-architect` is consulted where the hypothesis is really a claim about a pattern they designed, and owns the remediation backlog.
>
> **When to invoke:** "design a chaos experiment for X"; "which fault do we inject first?"; "did the circuit breaker / failover actually hold?"; any hypothesis-driven test of whether a resilience pattern survives a real fault.
>
> **Output:** an experiment plan + verification — steady-state + falsifiable hypothesis + smallest blast radius + fault + automatic abort conditions + a did-it-hold verdict correlated under load + a remediation backlog — captured in the chaos-experiment plan.

## Procedure

1. **Run the maturity gate first — refuse if it fails.** Via [`../../knowledge/chaos-engineering-resilience-decision-tree.md`](../../knowledge/chaos-engineering-resilience-decision-tree.md) Tree A: is steady-state observability present? Are SLOs/steady-state metrics defined? Is on-call ready? If any is missing, the deliverable is the prerequisite list, **not** an experiment — immature observability means you can't tell an experiment from an outage.
2. **Define steady state.** The measurable "healthy" — the business/system metric(s) and their SLO thresholds (e.g. checkout success ≥ 99.5%, p99 latency ≤ 800ms). Steady state is what you'll watch to know whether the system held; without it there is no experiment.
3. **State a falsifiable hypothesis.** Format: *"When `<fault>`, `<steady-state metric>` stays within `<bound>` because `<resilience pattern>`."* It must be disprovable — "the system will be fine" is not a hypothesis. This ties the experiment to a specific pattern claim from `design-resilience-patterns`.
4. **Pick the fault and the smallest disproving blast radius.** Via Tree B (highest-blast dependency vs most-likely fault) and the taxonomy (latency, error, resource exhaustion, dependency outage, network partition, zone failure). Choose the *smallest* scope that could still disprove the hypothesis — one instance/one cell/one dependency in staging first. Widen only after it holds small.
5. **Define the automatic abort condition BEFORE injecting.** The steady-state breach (or error-budget burn) that halts the experiment and rolls back, wired to fire automatically. **An experiment with no abort condition is an outage.** Stage the environment from non-prod outward; enter prod only carefully, cell by cell.
6. **Inject, under realistic load, and observe.** Combine the fault with representative traffic (a pattern that holds idle can shatter under load — `performance-engineering` generates it). Watch the steady-state metrics through the injection window.
7. **Verify honestly — correlate, don't assume.** Correlate the steady-state metric to the *injection window*; "nothing broke" on an uncorrelated dashboard is not a pass. Emit a **HELD / DID-NOT-HOLD** verdict. Capture everything in [`../../templates/chaos-experiment-plan.md`](../../templates/chaos-experiment-plan.md).
8. **Abort-or-learn, then remediate.** If it held: record the confidence gained and consider widening the blast radius next round. If it didn't (or aborted): write the **remediation backlog** — the design/runbook gaps — ranked, with owners (a design gap is `resilience-architect`'s; a real incident stops the experiment and goes to `incident-response-dfir`).

## Worked example

> User: "We added a circuit breaker + fallback to our order service's call to the payment API. We want to prove it works before Black Friday. How do we run this without taking down prod?"

- **Maturity gate (Tree A):** checkout-success and latency SLOs exist, dashboards are live, on-call is staffed → **GO**. (If SLOs were missing, we'd stop here and send it back to `observability-sre` first.)
- **Steady state:** checkout success ≥ 99.5%, order-service p99 ≤ 800ms, over a 5-min window.
- **Hypothesis (falsifiable):** *"When the payment API adds 2000ms latency, checkout success stays ≥ 99.5% because the circuit breaker opens and orders fall back to async capture."*
- **Fault + smallest blast radius:** latency injection (taxonomy) on the payment dependency, **staging first**, then one production cell (~2% of traffic) — not the whole fleet. Highest-blast dependency (Tree B) is exactly the payment call, so it's the right first target.
- **Abort condition (defined before injecting):** if checkout success drops below 99% for 60s, or site-wide error rate exceeds baseline + 2%, auto-halt the injection and restore. Wired to the fault-injection tool's automatic stop.
- **Run under load:** replay Black-Friday-scale checkout traffic (`performance-engineering`) while injecting — because the breaker's behavior at 2 RPS tells us nothing about 2000 RPS.
- **Verify:** correlate checkout success + breaker-open events to the injection window. **Result: HELD** — success stayed at 99.6%, breaker opened at t+8s, fallback served. *Or* DID-NOT-HOLD — breaker opened but the async-capture queue backed up, success fell to 97% → remediation backlog item for `resilience-architect` (size the queue / add backpressure), retest.
- **Seam:** SLO signals + on-call → `observability-sre`; load → `performance-engineering`; the queue-sizing design gap → `resilience-architect`.

## Guardrails

- **No experiment without the maturity gate passing** — no steady-state observability, no SLOs, no on-call → no injection. You'd just be breaking prod.
- **No injection without an automatic abort condition defined first** — an experiment with no abort is an outage with paperwork.
- **Every experiment is a falsifiable hypothesis and the smallest blast radius** — "let's see what happens" is gambling, not chaos engineering.
- **Widen scope only after it holds small** — staging → one cell → one region; never region-first, never prod-first.
- **Inject under realistic load** — a pattern proven idle is not proven.
- **"Nothing broke" is not a pass** — correlate the steady-state metric to the injection window or the result is meaningless.
- **A real incident stops the experiment** — if the fault triggers actual customer impact, halt, restore, and hand to `incident-response-dfir`; the experiment is over.
- **Volatile fault-injection tooling facts carry a retrieval date** and are re-verified before a production run. See [`../../knowledge/chaos-engineering-resilience-patterns-2026.md`](../../knowledge/chaos-engineering-resilience-patterns-2026.md).
