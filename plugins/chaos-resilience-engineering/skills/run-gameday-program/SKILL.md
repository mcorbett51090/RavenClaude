---
name: run-gameday-program
description: "Plan and run a GameDay that produces a prioritized fix list — set the objective and the system in scope, assign the roles (facilitator / operator / observer / scribe), select scenarios from the failure taxonomy each with a steady-state hypothesis, run the SAFETY pre-flight (every scenario has a hypothesis, a blast-radius limit, and an abort/rollback), execute the injections through the staging→prod progression, capture the timeline and findings, and turn them into assigned, prioritized action items plus the continuous-verification follow-up so the resilience doesn't regress. Reach for this when the user asks 'run a GameDay for this service', 'how do I structure a resilience exercise?', 'what roles and scenarios for a GameDay?', or 'how do we make GameDay findings stick?'. A GameDay's deliverable is a fix list, not a war story. Used by `resilience-architect` (primary)."
---

# Skill: run-gameday-program

> **Invoked by:** `resilience-architect` (primary, owns the program). The `chaos-experiment-engineer` executes the injections within the GameDay.
>
> **When to invoke:** "Run a GameDay for the checkout service"; "how do I structure a resilience exercise?"; "what roles and scenarios for a GameDay?"; "how do we make GameDay findings actually stick?"; any planned, facilitated, human-in-the-loop resilience exercise.
>
> **Output:** the GameDay runbook (objective, roles, scenarios, SAFETY pre-flight, run timeline) + the findings + the **prioritized, assigned action-item list** + the continuous-verification follow-up — captured in [`../../templates/gameday-runbook.md`](../../templates/gameday-runbook.md).

## Procedure

1. **Set the objective and the system in scope.** Name what this GameDay is proving (a specific service's resilience, a runbook's validity, the on-call team's response) and the environment (staging, or prod behind the SAFETY spine). A GameDay without a sharp objective drifts into a demo.
2. **Assign the roles.** **Facilitator** (runs the plan, owns the abort call), **operator** (injects the fault / executes the runbook), **observer(s)** (watch the steady-state metric and system behavior), **scribe** (records the timeline, findings, and action items). See [`../../knowledge/chaos-resilience-patterns-2026.md`](../../knowledge/chaos-resilience-patterns-2026.md).
3. **Select scenarios from the failure taxonomy — each with a hypothesis.** Pick 2–4 real-world scenarios (resource / network / state / dependency / region) ranked by likelihood × blast radius × detectability; each scenario carries its own **steady-state hypothesis** ("under fault X, metric Y stays within Z") from [`../design-steady-state-and-hypothesis/SKILL.md`](../design-steady-state-and-hypothesis/SKILL.md).
4. **Run the SAFETY pre-flight — every scenario, no exceptions.** Before injecting anything, the facilitator confirms each scenario has (a) a hypothesis, (b) a blast-radius limit, (c) an abort/rollback. A scenario missing any of the three is **cut or downgraded to staging** — never run in prod. This is the SAFETY spine.
5. **Execute through the staging→prod progression.** The operator injects each scenario (via [`../run-fault-injection-experiment/SKILL.md`](../run-fault-injection-experiment/SKILL.md)), smallest blast radius first; observers watch the metric; the facilitator aborts on breach. The scribe timestamps everything.
6. **Capture findings as they happen.** For each scenario: hypothesis held / refuted, what the system actually did, what the runbook got right or wrong, and any surprise. A refuted hypothesis or a broken runbook step is a finding, not an embarrassment.
7. **Turn findings into a prioritized, assigned fix list — the deliverable.** Every finding becomes an action item with an **owner, a priority, and a date**, mapped to the resilience pattern or runbook fix it needs. A GameDay that ends without assigned actions wasted the risk.
8. **Schedule the continuous-verification follow-up.** Where a scenario should never regress, hand the engineer the job of wiring it into CI/CD or a schedule (with an automated abort) so the property stays proven — a one-time GameDay decays.

## Worked example

> User: "Run a GameDay for our checkout service before Black Friday."

- **Objective:** prove checkout survives its top 3 failure modes and validate the incident runbook, in **staging** first, then a bounded prod run.
- **Roles:** facilitator (resilience lead), operator (platform engineer), 2 observers (checkout on-call + SRE), scribe (PM).
- **Scenarios (each with a hypothesis):** (1) payment-gateway 2s latency — "success stays ≥ 99.4%"; (2) one AZ loss — "success stays ≥ 99% via failover"; (3) Redis cache down — "success stays ≥ 99% via DB fallback".
- **SAFETY pre-flight:** each scenario gets a blast-radius limit (1% / one AZ) + an automated abort (success < 99.2%) + a tested rollback. Scenario 2's prod rollback wasn't tested → **downgraded to staging** for this GameDay.
- **Run:** scenario 1 refuted (dropped to 98.9%) → finding: no gateway timeout/circuit breaker. Scenario 3 held. Runbook step 4 pointed at a stale dashboard → finding.
- **Fix list:** P0 add payment-gateway timeout + circuit breaker + fallback (owner: checkout team, by Nov 10); P1 fix runbook step 4 (owner: SRE, by Nov 5); P1 test scenario-2 prod rollback then re-run.
- **Continuous verification:** wire scenario 1 into the pre-deploy pipeline with an automated abort so the fix can't regress.
- **Captured in** [`../../templates/gameday-runbook.md`](../../templates/gameday-runbook.md).

## Guardrails

- **A GameDay's deliverable is a prioritized, assigned fix list** — no assigned action items means the risk was spent for adrenaline.
- **SAFETY pre-flight every scenario** — a scenario missing a hypothesis, a blast-radius limit, or an abort/rollback is cut or downgraded to staging; never run in prod.
- **Every scenario carries its own steady-state hypothesis** — a "let's just see what breaks" scenario is an intentional outage.
- **Staging before prod**, smallest blast radius first — the same progression as any experiment.
- **A refuted hypothesis or a broken runbook step is a finding, not a failure** — the point is to find it here, not in the incident.
- **Follow up with continuous verification** where a property must not regress — a one-time GameDay decays as the system changes.
- Volatile claims (tool features, cloud fault-API capabilities) carry a **retrieval date** — re-verify before a client commitment.
