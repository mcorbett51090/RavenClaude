# Chaos experiment design — <experiment name / target service>

> The per-experiment design record captured **before** any fault is injected. Pairs with
> [`gameday-runbook.md`](gameday-runbook.md) (the multi-scenario, human-in-the-loop exercise).
> The order matters: **hypothesis → steady state → fault → SAFETY controls → staging → prod → observe → result → actions.**
>
> ⚠️ **SAFETY spine — this experiment does NOT run against production without ALL THREE:**
> **(a) a stated steady-state hypothesis, (b) an explicit blast-radius limit, (c) an abort/rollback condition.**
> Missing any → downgrade to staging or complete this record to spec first. An experiment you can't stop is an incident.

**Target service:** <name> · **Date:** <YYYY-MM-DD> · **Platform:** <k8s / AWS / Azure / other> · **Tool:** <Chaos Mesh / LitmusChaos / AWS FIS / Gremlin / Steadybit / Azure Chaos Studio / Chaos Toolkit + retrieval date>
**Owner / preparer:** <name> · **Status:** draft / approved / run-staging / run-prod / done

## 1. Hypothesis (falsifiable — required)
- **Hypothesis:** "Under fault **<X>**, steady-state metric **<Y>** stays within band **<Z>**."
- **Falsifiable?** <yes — what observation would refute it>

## 2. Steady state (the measured "healthy")
- **Metric:** <customer/business-facing output — e.g. checkout success rate>
- **Normal band (from real data):** <baseline ± variance · measurement window>
- **Observability to detect a deviation in place?** <yes — dashboard/alert · resolution> (if no → INSTRUMENT FIRST, do not run — → observability-sre)
- **Resilience SLO / error-budget link:** <the SLO the band ties to · budget framing>

## 3. The fault (a real-world event)
- **Fault:** <e.g. 2s latency on payment-gateway dependency>
- **Taxonomy class:** <resource / network / state / dependency / region>
- **Why this fault (likelihood × blast-radius × detectability):** <the ranking rationale>

## 4. Blast-radius limit (the hard cap — required for prod)
- **Smallest run that can still falsify:** <one pod / one AZ / N% of traffic>
- **Hard limit (may not exceed):** <scope>
- **Expansion criteria:** <what a smaller run must pass before expanding>

## 5. Abort condition (required for prod)
- **Automated stop trigger:** <"halt if metric Y breaches by > X for <duration>">
- **How it's wired:** <alarm / tool stop-condition / manual watch — automated where possible>

## 6. Rollback (tested — required for prod)
- **How the fault is halted & state restored:** <delete the fault resource / disable the action / …>
- **Rollback tested?** <yes — in staging · time-to-restore>

## 7. Environment progression
- **Staging run:** <date · result · pass?>
- **Prod smallest run:** <date · blast radius · result>
- **Expansion (only if smaller passed):** <date · new blast radius · result>

## 8. Observation vs hypothesis
- **What actually happened:** <the metric's live behavior during injection>
- **Hypothesis:** <HELD / REFUTED>

## 9. Result & action items (the deliverable)
- **If REFUTED — the resilience gap:** <e.g. no payment-gateway timeout + circuit breaker + fallback>
- **Action items:** <item — owner — priority — date — the resilience pattern it needs>
- **Re-run to prove the fix?** <date>

## 10. Continuous verification (if this must not regress)
- **Wire into:** <CI/CD stage · schedule> · **automated guardrail that halts on breach:** <detail> (→ chaos-experiment-engineer)

## SAFETY check (sign before any prod run)
- **Hypothesis present:** <✓ / ✗> · **Blast-radius limit set:** <✓ / ✗> · **Abort/rollback ready & tested:** <✓ / ✗>
- **All three ✓?** <yes → cleared for prod · no → DOWNGRADE to staging>

## Seams (not this team)
- **System failing right now / on-call / the telemetry to detect it:** observability-sre (also the observability precondition)
- **Throughput / latency / cost tuning:** performance-engineering
- **Functional correctness / regression:** qa-test-automation
- **Reading a refuted result into the resilience pattern:** resilience-architect

## Open questions / risks
- <list — especially any tool/API claim carrying a retrieval date to re-verify>

**Prepared by:** <name> · **Tool-capability retrieval date:** <YYYY-MM-DD> · **SAFETY sign-off:** <reviewer>
