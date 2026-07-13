---
name: design-steady-state-and-hypothesis
description: "Define a system's steady state and the falsifiable hypothesis before any chaos experiment — pick the customer/business-facing metric that means 'healthy', establish its normal band from real data, confirm the observability exists to detect a deviation in real time, write the hypothesis as 'under fault X, metric Y stays within band Z', and tie it to a resilience SLO / error budget. Reach for this when the user asks 'what does healthy mean for this service?', 'define our steady state', 'how do I write a chaos hypothesis?', or 'we want to break something — where do we start?'. This is the gate every experiment passes through: no steady state and no falsifiable hypothesis means no experiment. Used by `resilience-architect` (primary)."
---

# Skill: design-steady-state-and-hypothesis

> **Invoked by:** `resilience-architect` (primary). Also consulted by `chaos-experiment-engineer` to confirm a hypothesis + steady-state metric exist *before* injecting any fault.
>
> **When to invoke:** "What does 'healthy' mean for this service?"; "define our steady state"; "how do I write a chaos hypothesis?"; "we want to start chaos engineering — where do we begin?"; any move from a system to a testable resilience assertion — **before** any fault is injected.
>
> **Output:** the steady-state metric + normal band + the observability-to-detect check + the falsifiable hypothesis + the resilience-SLO/error-budget link + the 1-2 flip conditions. This is the input to [`../run-fault-injection-experiment/SKILL.md`](../run-fault-injection-experiment/SKILL.md) and captured in [`../../templates/chaos-experiment-design.md`](../../templates/chaos-experiment-design.md).

## Procedure

1. **Pick the metric that means "healthy" — prefer a customer/business output.** Choose a measurable output metric (checkout success rate, orders/min, p99 latency, successful-login rate) over an internal one — it's what "the system works" actually means to a user. See [`../../knowledge/chaos-resilience-patterns-2026.md`](../../knowledge/chaos-resilience-patterns-2026.md).
2. **Establish the normal band from real data.** Measure the metric's normal operating range (baseline ± variance across a representative window) *before* any experiment — you cannot detect a deviation you never quantified. Record the band, not a single point.
3. **Confirm the observability to detect a deviation exists.** Verify the metrics/traces/logs to watch the metric *in real time during injection* are in place — this is a hard precondition, and that telemetry is `observability-sre`'s domain. If it isn't there, the deliverable is "instrument first" — do not proceed to an experiment.
4. **Write the falsifiable hypothesis.** State it as **"under fault X, steady-state metric Y stays within band Z."** It must be refutable — if no observation could disprove it, it isn't a hypothesis. Name the specific fault (a real-world event from the failure taxonomy), the metric, and the band.
5. **Tie it to a resilience SLO / error budget.** Connect the steady-state band to the service's SLO where one exists — a hypothesis that "checkout success stays ≥ 99.5% under a payment-gateway timeout" is stronger when 99.5% is the actual SLO and the error budget frames the acceptable deviation.
6. **State what a refuted hypothesis would mean.** Pre-name the resilience gap a refutation would reveal (e.g. "if success drops, we lack a payment-gateway timeout + fallback") so the result reads straight into a fix (owned by the architect), not a shrug.
7. **State the flip conditions.** Name the 1-2 facts that would change the metric, band, or hypothesis (e.g. "if we add a second payment provider, the steady state and the fault both change").

## Worked example

> User: "We want to run chaos on our checkout service. Where do we start?"

- **Steady-state metric:** **checkout success rate** (customer-facing output), not CPU or pod count.
- **Normal band:** measured at **99.6% ± 0.2%** over the last 4 weeks of business-hours traffic — recorded as the band.
- **Observability check:** the success-rate metric is emitted per-request and dashboarded with a 1-minute resolution → we *can* detect a deviation live. (If it weren't, the deliverable would be "instrument this first," full stop.)
- **Hypothesis:** *"Under a 2-second latency injection on the payment-gateway dependency, checkout success rate stays within 99.4–99.8% (i.e. does not drop more than 0.2 pts)."* — falsifiable.
- **SLO link:** the checkout SLO is 99.5%; the hypothesis band sits at the SLO, and the error budget frames the acceptable dip.
- **If refuted:** success drops → we lack a bounded timeout + a graceful fallback on the payment gateway → route to the architect for the resilience pattern (timeout + circuit breaker + fallback), then to the engineer to prove the fix.
- **Flip condition:** if a second payment provider is added, the steady state and the fault both change — re-baseline.

## Guardrails

- **No steady state and no falsifiable hypothesis → no experiment.** This skill is the gate; a "let's break something and see" with no hypothesis is an intentional outage, and the engineer will send it back.
- The metric is a **measured band from real data**, not a guess — you can't detect a deviation you never quantified.
- **Observability to detect the deviation is a precondition** — if it's missing, the deliverable is "instrument first" (→ observability-sre), not an experiment.
- Prefer a **customer/business-facing output metric** over an internal one — it's what "healthy" means to a user.
- A refuted hypothesis is a **finding, not a failure** — pre-name the resilience gap it would reveal so it reads into a fix.
- Volatile claims (SLO tooling, observability-platform features) carry a **retrieval date** — re-verify before a client commitment.
