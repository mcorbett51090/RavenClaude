---
scenario_id: 2026-06-08-platform-had-no-slos
contributed_at: 2026-06-08
plugin: platform-engineering-idp
product: platform-slo
product_version: "n/a"
scope: likely-general
tags: [platform-slo, error-budget, reliability, self-service]
confidence: medium
reviewed: false
---

## Problem

A platform team pushed teams onto the golden path while the paved provisioning action failed intermittently and had no SLO. The risk: a platform treated as best-effort infrastructure rather than a service can't honor a self-service promise, and the flakiness quietly drives teams back to workarounds (§3 #6).

## Context

- Maturity: org mandating the golden path for new services.
- Constraint: the platform is production for its developer-customers — it needs SLOs and an error budget like any service (§3 #6).
- The team treated reliability as ad-hoc.

## Attempts

- Tried: **defined platform SLIs** — paved-path success rate, provisioning p95 latency, pipeline reliability (§3 #6). Outcome: provisioning success sat well below a credible self-service promise.
- Tried: **set SLO targets against a dated source and computed the error budget** (1 − target × window). Outcome: the budget was already overspent — explaining the silent adoption cap (§3 #6 #8).
- Tried: **gated platform feature work on the budget.** Outcome: a freeze on new features until provisioning was back in budget — the same discipline as a user-facing service.

## Resolution

The fix was to **run the platform on SLOs with an error budget that gates change**, fix provisioning before pushing more teams onto the path, and only then resume feature work — **not** to keep mandating an unreliable road. The output was the SLO set, the error-budget state, and the change-gate decision.

**Action for the next consultant hitting this pattern:** **give the platform SLOs and an error budget before you recommend or mandate its golden path.** An unreliable paved action silently caps adoption. Gate platform change on the budget, exactly as for any service. See Tree 3 and the `set-platform-slos` skill.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
