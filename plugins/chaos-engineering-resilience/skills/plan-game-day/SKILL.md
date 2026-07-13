---
name: plan-game-day
description: "Facilitate a game day end to end — the scenario, the roles (facilitator / operators / observers / scribe), the comms plan, the abort criteria, a scoring rubric, and the follow-up remediation backlog. Game days test PEOPLE and RUNBOOKS under a controlled failure, not just systems — the cheapest way to find the org's real failure modes. Reach for this when the user asks 'run us a game day for X', 'how do we do a failure drill', or 'test our on-call/runbooks against an outage'. Driven by `chaos-experiment-engineer`; the `resilience-architect` is consulted on prerequisites + remediation."
---

# Skill: plan-game-day

> **Invoked by:** `chaos-experiment-engineer` (primary — facilitates). The `resilience-architect` is consulted on the maturity prerequisites and owns the design items in the remediation backlog.
>
> **When to invoke:** "run us a game day for the checkout path"; "do a failure drill"; "test our on-call + runbooks against a simulated outage"; any exercise whose goal is the humans-and-runbooks response, not just a system's behavior.
>
> **Output:** a game-day plan — scenario, roles, comms, abort criteria, scoring rubric, and a ranked follow-up remediation backlog — with the systems findings and the people/runbook findings both captured.

## Procedure

1. **Confirm the maturity prerequisites.** Via [`../../knowledge/chaos-engineering-resilience-decision-tree.md`](../../knowledge/chaos-engineering-resilience-decision-tree.md) Tree A: steady-state observability, defined SLOs, and a ready on-call. A game day without these tests nothing but chaos — send it back to `observability-sre` first if they're missing.
2. **Choose the scenario.** A realistic, plausible failure worth rehearsing — a region loss, a key dependency outage, a database failover, a cascading slowdown. Prefer the highest-blast-radius scenario the org fears but hasn't drilled (Tree B). Write it as a narrative the operators will respond to in real time.
3. **Assign roles.** **Facilitator** (runs the exercise, injects the scenario, holds the abort button), **operators/responders** (the on-call who diagnose and mitigate as if it were real), **observers** (watch and take notes without helping), and a **scribe** (timestamps every action and decision for the debrief). Keep responders blind to the exact fault where possible — you're testing detection, not recall.
4. **Write the comms plan.** Who is told this is a drill and who isn't; the "GAME DAY — not a real incident" banner on every channel; the escalation path being exercised; and the explicit signal that ends the exercise. Never let a game day leak into a real page storm.
5. **Define the abort criteria up front.** The point at which the facilitator halts — real customer impact, a responder unable to recover, or a time box exceeded. Like any experiment, **a game day with no abort criteria is an outage**; if it's run against production, the automatic safeguards from `run-chaos-experiment` apply.
6. **Score against a rubric.** Time-to-detect, time-to-mitigate, whether the runbook existed and was correct, whether the right people were reachable, whether the resilience patterns held, and where the response stalled. Score the **people-and-runbook** dimension explicitly — that's usually where the real gaps are.
7. **Run the debrief and build the remediation backlog.** Blameless. Turn every finding into a ranked backlog item with an owner: missing/wrong runbook → the owning team; a resilience-design gap → `resilience-architect`; a missing signal/alert → `observability-sre`. Capture the systems side in [`../../templates/chaos-experiment-plan.md`](../../templates/chaos-experiment-plan.md) and feed the design gaps to [`../../templates/resilience-review-checklist.md`](../../templates/resilience-review-checklist.md).

## Worked example

> User: "We've never actually tested what happens if our primary region goes down. We think we have failover but nobody's exercised it. Run us a game day."

- **Prerequisites (Tree A):** multi-region SLO dashboards exist, on-call is staffed → GO. (If failover had never been designed, this is premature — `resilience-architect` first.)
- **Scenario:** "At 10:00 the primary region (us-east) becomes unreachable. Responders must detect, decide, and execute failover to us-west, and confirm recovery." Written as a live narrative; responders are told only that "a game day is running today," not the specific fault.
- **Roles:** facilitator injects the region-isolation fault (network partition, from the taxonomy) and holds the abort; two on-call engineers respond; a platform observer and a scribe watch and timestamp.
- **Comms:** every channel banners "GAME DAY — simulated us-east loss, NOT a real incident"; the exec/status-page path is exercised in a drill mode, not published live.
- **Abort criteria:** halt if any real customer traffic is impacted, if failover can't complete in 30 min, or if a responder calls it.
- **Findings (the value):** systems — failover *worked* but took 22 min because the DNS TTL was 15 min (a design gap → `resilience-architect`: lower TTL / pre-warm standby, tie to the RTO target). People/runbooks — the runbook pointed at a decommissioned dashboard, and the person with failover permissions was on PTO with no backup. **The people/runbook gaps were the expensive ones** — exactly what a game day exists to surface.
- **Remediation backlog:** lower DNS TTL + verify RTO (`resilience-architect`); fix + rehearse the failover runbook (platform team); add a permissions backup (on-call process); add a failover-duration alert (`observability-sre`).

## Guardrails

- **Game days test people and runbooks, not just systems** — score the human response explicitly; the costliest gaps are usually there.
- **Confirm the maturity prerequisites first** — no steady state / SLOs / on-call means the drill measures noise.
- **Abort criteria and a "this is a drill" comms banner are defined before you start** — a game day that leaks into a real page storm or real customer impact is an outage.
- **Keep responders blind to the exact fault where you can** — you're testing detection and diagnosis, not memory.
- **Run the debrief blameless** — the goal is the failure mode, not a culprit.
- **Every finding becomes a ranked, owned backlog item** — a game day with no follow-up backlog is theater; route design gaps to `resilience-architect` and signal gaps to `observability-sre`.
- **Volatile tooling/service failover facts carry a retrieval date.** See [`../../knowledge/chaos-engineering-resilience-patterns-2026.md`](../../knowledge/chaos-engineering-resilience-patterns-2026.md).
