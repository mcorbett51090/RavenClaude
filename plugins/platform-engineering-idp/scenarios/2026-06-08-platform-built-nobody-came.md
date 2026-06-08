---
scenario_id: 2026-06-08-platform-built-nobody-came
contributed_at: 2026-06-08
plugin: platform-engineering-idp
product: golden-path
product_version: "n/a"
scope: likely-general
tags: [adoption, golden-path, friction, product-thinking]
confidence: medium
reviewed: false
---

## Problem

A platform team shipped a rich self-service portal and reported it as 'done', but most teams still hand-rolled their own pipelines. The risk: a platform measured by features shipped rather than adoption can be net-negative — it adds maintenance and cognitive load while teams route around it (§3 #1 #7).

## Context

- Maturity: mid-size eng org, ~40 teams, voluntary platform.
- Constraint: a golden path only wins if it is the EASIEST option; a paved road harder than the workaround breeds shadow tooling (§3 #2).
- The team reasoned from feature count, not adoption.

## Attempts

- Tried: **measured adoption as teams-on-path ÷ total** (`platform_engineering_idp_calc.py adoption`). Outcome: ~20% on-path — the platform was a minority option, so feature count was misleading (§3 #7).
- Tried: **timed time-to-first-deploy on the paved path vs the hand-rolled workaround.** Outcome: the paved path took longer because it bottomed out in a provisioning ticket — not self-service at all (§3 #4).
- Tried: **segmented the 80% un-adopted teams by why.** Outcome: a single provisioning hand-off explained most of the gap.

## Resolution

The fix was to **pave that one hand-off into a self-service action with a guardrail** and re-pitch the path as the lowest-friction option — **not** to add more features or mandate it. Adoption is the scoreboard; the gap backlog was the work. The output was the adoption ratio, the friction decomposition, and the prioritized paving backlog.

**Action for the next consultant hitting this pattern:** **measure adoption and make the paved path the easy path before shipping more features.** A feature nobody adopts is negative value; the un-adopted teams are the backlog. Decompose the friction (every ticket is debt) and pave the binding hand-off. See Tree 1 and the `adoption` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
