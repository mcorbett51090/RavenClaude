---
name: decide-tech-debt
description: "Decide whether to pay down a specific tech-debt by sizing its carrying cost and payback against the roadmap — not all-or-nothing. Reach for this before a 'we must stop and refactor' or 'we never have time' reflex."
---

# Skill: Decide tech-debt

Tech-debt is a business decision with a carrying cost, not a moral failing (§3 #7).

## Step 1 — Measure the pain, don't feel it
Lead-time drift, change-fail, rework, and hotspots — separate *felt* pain from *measured* pain (§3 #4 #7). "The codebase is bad" is not a finding.

## Step 2 — Is it on a hotspot?
High churn × high complexity is where paydown has leverage. Stable code, even ugly, is low priority (§3 #7).

## Step 3 — Size carrying cost + payback
Run `engineering_management_calc.py tech-debt` to compute the carrying cost per period and the payback periods of paying it down (§3 #7).

## Step 4 — Trade against the roadmap explicitly
Pay down when payback is short relative to the code's remaining life; prefer incremental (strangler-fig) over a rewrite (the highest-risk, longest-payback option). Reserve a standing capacity slice rather than a one-off crusade.

## Output
A tech-debt decision memo: measured pain, hotspot status, sized carrying cost + payback, and a recommendation with a capacity slice. Use [`../../templates/tech-debt-decision-memo.md`](../../templates/tech-debt-decision-memo.md). Traverse Tree 3. The architecture itself routes to `ravenclaude-core/architect`.
