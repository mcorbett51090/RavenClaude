# GameDay runbook — <system / service · date>

> The runbook for a planned, facilitated resilience exercise. Pairs with
> [`chaos-experiment-design.md`](chaos-experiment-design.md) (the single-experiment record; one per scenario below).
> The order matters: **objective → roles → scenarios → SAFETY pre-flight → run → findings → fix list → continuous verification.**
>
> ⚠️ **SAFETY spine — every scenario runs against production ONLY with a hypothesis, a blast-radius limit, and an abort/rollback.**
> A scenario missing any of the three is cut or downgraded to staging. **The deliverable is a prioritized, assigned fix list — not a war story.**

**System in scope:** <service(s)> · **Date / time:** <YYYY-MM-DD, window> · **Environment:** <staging / prod-behind-SAFETY-spine>
**Objective:** <what this GameDay proves — resilience of X / validate runbook Y / train on-call> · **Facilitator:** <name>

## 1. Roles
| Role | Person | Responsibility |
|---|---|---|
| **Facilitator** | <name> | Runs the plan · owns the ABORT call |
| **Operator** | <name> | Injects the fault / executes the runbook |
| **Observer(s)** | <name(s)> | Watch the steady-state metric & system behavior |
| **Scribe** | <name> | Timeline · findings · action items |

## 2. Scenarios (2–4, each with its own hypothesis)
| # | Scenario (fault) | Taxonomy class | Steady-state hypothesis ("under X, Y stays within Z") | Env |
|---|---|---|---|---|
| 1 | <e.g. payment-gateway 2s latency> | <network/dependency> | <"checkout success ≥ 99.4%"> | <staging→prod> |
| 2 | <e.g. one AZ loss> | <region/zone> | <"success ≥ 99% via failover"> | <staging> |
| 3 | <e.g. cache down> | <state> | <"success ≥ 99% via DB fallback"> | <staging→prod> |

## 3. SAFETY pre-flight (facilitator confirms EACH scenario before any injection)
| # | Hypothesis ✓ | Blast-radius limit ✓ | Abort/rollback tested ✓ | Cleared for prod? |
|---|---|---|---|---|
| 1 | <✓/✗> | <✓/✗ — scope> | <✓/✗> | <yes / DOWNGRADE to staging> |
| 2 | <✓/✗> | <✓/✗> | <✓/✗> | <yes / DOWNGRADE to staging> |
| 3 | <✓/✗> | <✓/✗> | <✓/✗> | <yes / DOWNGRADE to staging> |

> Any scenario without all three ✓ is **cut or run in staging only** — never in prod.

## 4. Run timeline (scribe fills live)
| Time | Scenario | Action / injection | Metric behavior | Aborted? |
|---|---|---|---|---|
| <hh:mm> | <#> | <inject / observe / abort / rollback> | <metric value> | <no / yes — why> |

## 5. Findings (per scenario)
| # | Hypothesis held/refuted | What the system actually did | Runbook right/wrong | Surprise |
|---|---|---|---|---|
| 1 | <held / refuted> | <behavior> | <step X was stale> | <…> |
| 2 | <…> | <…> | <…> | <…> |

## 6. Fix list (the deliverable — every finding → an assigned action)
| Finding | Action item | Resilience pattern / runbook fix | Owner | Priority | Date |
|---|---|---|---|---|---|
| <no gateway timeout> | <add timeout + circuit breaker + fallback> | <circuit breaker> | <checkout team> | <P0> | <YYYY-MM-DD> |
| <stale runbook step> | <fix step 4 dashboard link> | <runbook> | <SRE> | <P1> | <YYYY-MM-DD> |

## 7. Continuous verification follow-up (so it doesn't regress)
- **Scenario(s) to automate:** <#> · **Wire into:** <CI/CD stage · schedule> · **automated abort guardrail:** <detail> (→ chaos-experiment-engineer)

## Seams (not this team)
- **A real incident during the GameDay / on-call / detection telemetry:** observability-sre (stop the GameDay, run the real response)
- **Throughput / latency / cost tuning:** performance-engineering
- **Functional correctness / regression:** qa-test-automation
- **Reading a refuted hypothesis into the resilience pattern:** resilience-architect

## Open questions / risks
- <list — especially any scenario downgraded to staging and why, and any tool claim to re-verify>

**Facilitator sign-off:** <name> · **Tool-capability retrieval date:** <YYYY-MM-DD> · **Fix list circulated to:** <owners>
