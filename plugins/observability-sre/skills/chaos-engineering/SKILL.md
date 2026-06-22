---
name: chaos-engineering
description: "Verify resilience proactively with chaos experiments — a steady-state hypothesis, a controlled fault injection, a blast-radius limit, and a game day — instead of waiting for the real outage. Reach for this to prove (not assume) a system tolerates failure."
---

# Skill: Chaos engineering

You don't know a system is resilient until you've broken it on purpose, in a controlled way. Chaos engineering is experimentation to *build confidence* in a system's behavior under turbulent conditions — the proactive complement to the reactive incident-response practice.

## Step 1 — Define steady state
Pick a measurable output that means "the system is healthy" — a business or SLI metric (e.g. checkout success rate, p99 latency), not an internal cause metric. This is what the experiment watches.

## Step 2 — Form a hypothesis
State what you believe will happen: "steady state will hold when we inject <fault>." A chaos experiment tests a *belief* about resilience — if you have no hypothesis, you're just breaking things.

## Step 3 — Limit the blast radius
Decide the smallest scope that still tests the hypothesis (one instance, one AZ, a traffic %, a non-peak window), and define the **abort conditions** up front. Start in staging; earn production. The blast-radius limit is what makes this engineering, not gambling.

## Step 4 — Inject a real-world fault
Introduce a fault that mimics a real failure mode: instance/pod kill, latency injection, dependency timeout/error, resource exhaustion, network partition, AZ loss. Inject one variable so the result is attributable.

## Step 5 — Observe, then learn
Watch steady state against the hypothesis. If it held, confidence grows. If it broke, you found a resilience gap *before* a customer did — feed it back as a reliability action item (the same backlog as a postmortem's).

## Game days
Run the above as a scheduled, cross-team exercise (a "game day"): rehearse a failure scenario end-to-end, exercising both the system's resilience *and* the team's incident response. A game day is where chaos engineering and the [`incident-response`](../incident-response/SKILL.md) practice meet.

> The resilience patterns being verified (timeouts, retries with backoff, circuit breakers, bulkheads, graceful degradation) are implemented by `backend-engineering`; this skill *proves* they work. Fault-injection automation in the delivery pipeline routes to `devops-cicd`; cluster-level fault injection to `cloud-native-kubernetes`. See [`../../knowledge/chaos-engineering-reference.md`](../../knowledge/chaos-engineering-reference.md).
