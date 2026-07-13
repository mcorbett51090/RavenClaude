---
name: run-fault-injection-experiment
description: "Run a chaos experiment safely from a steady-state hypothesis to a recorded result — confirm the hypothesis + steady-state metric exist, pick a real-world fault and the matching tool (Chaos Mesh/LitmusChaos/AWS FIS/Gremlin/Steadybit/Azure Chaos Studio/Chaos Toolkit), set the explicit blast-radius limit + automated abort condition + tested rollback, run the staging→prod progression starting at the smallest blast radius, observe the metric live against the hypothesis with a hand on the abort, and record whether the hypothesis held or was refuted plus the action items. Reach for this when the user asks 'how do I inject this fault safely?', 'which chaos tool for pod-kill vs latency?', 'set my abort conditions', or 'run this from staging to prod'. NO production run happens without a hypothesis, a blast-radius limit, and an abort/rollback. Used by `chaos-experiment-engineer` (primary)."
---

# Skill: run-fault-injection-experiment

> **Invoked by:** `chaos-experiment-engineer` (primary). Also consulted by `resilience-architect` to design the blast radius / environment progression before the engineer owns the tooling and safety controls.
>
> **When to invoke:** "How do I inject this fault safely?"; "which tool for pod-kill vs latency vs a region?"; "set my blast-radius limit and abort conditions"; "run this from staging to prod"; any move from a hypothesis to a run fault, and back to a recorded result.
>
> **Output:** the fault + tool + the **blast-radius limit + abort condition + tested rollback** + the staging→prod progression + the observation vs hypothesis + the result (held/refuted) + action items — captured in [`../../templates/chaos-experiment-design.md`](../../templates/chaos-experiment-design.md).

> ⚠️ **SAFETY spine — no production experiment runs without ALL THREE: a stated steady-state hypothesis, an explicit blast-radius limit, and an abort/rollback condition.** An experiment you can't stop instantly *is* an incident. Missing any of the three → downgrade to staging or complete to spec first; this skill refuses to inject into prod (or wire into CI/CD) otherwise.

## Procedure

1. **Confirm the hypothesis + steady-state metric exist — else send it back.** Verify you have a falsifiable hypothesis ("under fault X, metric Y stays within band Z") and a measured steady-state band from [`../design-steady-state-and-hypothesis/SKILL.md`](../design-steady-state-and-hypothesis/SKILL.md). No hypothesis / no steady state → do not inject; return it to the architect.
2. **Pick a real-world fault from the taxonomy.** Map the fault to the failure taxonomy (resource / network / state / dependency / region) in [`../../knowledge/chaos-resilience-patterns-2026.md`](../../knowledge/chaos-resilience-patterns-2026.md) — a plausible production event, not a contrived one.
3. **Pick the matching tool for the fault + platform.** Kubernetes-native (**Chaos Mesh** / **LitmusChaos**), managed cloud fault API (**AWS FIS** / **Azure Chaos Studio**), SaaS platform (**Gremlin** / **Steadybit**), or open/declarative (**Chaos Toolkit**). Prefer the tool that provides more of the SAFETY controls for you. Tool features are volatile — carry a **retrieval date**.
4. **Set the blast-radius limit — the hard cap.** Define the smallest scope that can still falsify the hypothesis (one pod, one AZ, N% of traffic) and the hard limit it may not exceed. The first run is the smallest; expansion is earned by passing a smaller run.
5. **Set the automated abort condition.** Define the "**halt if steady-state metric breaches by more than X**" trigger — automated where the tool supports it (e.g. AWS FIS stop conditions on a CloudWatch alarm, a SaaS platform's halt). An experiment with no abort is not run in prod.
6. **Set and test the rollback.** Define how the fault is halted and state restored, and confirm it works — a rollback you haven't tested is a hope, not a control.
7. **Run the staging→prod progression.** Run in **staging** first; graduate to prod only after staging passed, at the **smallest** blast radius, expanding only after a smaller prod run passed. Never run a never-before-run fault straight in prod.
8. **Observe live against the hypothesis, hand on the abort.** Watch the steady-state metric during injection; if it breaches the abort threshold, **halt and roll back immediately**. Record what actually happened vs the hypothesis band.
9. **Record the result + action items.** Note hypothesis **held** or **refuted**; a refuted hypothesis routes to the architect for the resilience-pattern fix (timeout / retry+jitter / circuit breaker / bulkhead / load-shed / fallback). Capture everything in the experiment-design template.

## Worked example

> User: "We hypothesized checkout survives a 2s payment-gateway latency. How do I actually run it safely?"

- **Hypothesis confirmed:** "under 2s latency on payment-gateway, checkout success stays 99.4–99.8%" + the measured band exists → cleared to proceed.
- **Fault + class:** dependency latency (a real-world event) — **network/dependency** class.
- **Tool:** service runs on EKS → **Chaos Mesh** `NetworkChaos` delay of 2s on the payment-gateway egress, scoped by label. _(Chaos Mesh capability retrieved 2026-07-13 — verify.)_
- **Blast-radius limit:** **1% of checkout pods** in **one AZ** — the smallest scope that can still move the success metric; hard cap = never more than that AZ this run.
- **Abort condition:** automated halt if checkout success **drops below 99.2%** for 60s (alarm-driven).
- **Rollback:** delete the `NetworkChaos` resource → latency removed in seconds; tested in staging first.
- **Progression:** staging run passed (success held) → prod at 1% / one AZ → expand only if this passes.
- **Observe:** watch success rate live; hand on the abort. **Result:** success dropped to 98.9% → **hypothesis refuted** → route to architect: add a payment-gateway timeout + circuit breaker + cached-fallback, then re-run to prove the fix.
- **Captured in** [`../../templates/chaos-experiment-design.md`](../../templates/chaos-experiment-design.md).

## Guardrails

- **SAFETY spine — no prod run without a hypothesis, a blast-radius limit, and an abort/rollback.** Missing any → staging-only or complete to spec; refuse the prod injection.
- **No hypothesis / no steady state → no injection.** Send it back to the architect; you don't break a system with no defined "healthy."
- **Blast radius is a hard limit, smallest first** — staging before prod, expand only after a smaller run passed; never a first run at full scope.
- **The abort + rollback come before the injection, and the rollback is tested** — an experiment you can't stop is an incident.
- **Prefer real-world faults** the taxonomy names over contrived ones nobody experiences.
- A **refuted hypothesis routes to the architect** for the resilience-pattern fix — you prove the gap, you don't redesign the system.
- Fault-injection tool / cloud fault-API capabilities are volatile — carry a **retrieval date** and re-verify before a client commitment.
