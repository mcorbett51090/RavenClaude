---
description: "Decide whether to pay down a specific tech-debt by sizing its carrying cost and payback against the roadmap — not all-or-nothing."
argument-hint: "[the debt in question and what it's costing you]"
---

# Decide tech-debt

You are running `/engineering-management:decide-tech-debt` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure the pain, don't feel it — lead-time drift, change-fail, rework, hotspots (§3 #4 #7).
2. Is it on a hotspot? — high churn × complexity is where paydown has leverage (§3 #7).
3. Size carrying cost + payback — run `engineering_management_calc.py tech-debt` (§3 #7).
4. Trade against the roadmap explicitly — short payback vs remaining life; prefer incremental over rewrite; reserve a capacity slice.

## Output
A tech-debt decision memo with a recommendation and capacity slice. See [`../skills/decide-tech-debt/SKILL.md`](../skills/decide-tech-debt/SKILL.md). Traverse Tree 3.

## Guardrails
- Apply the §3 house opinions before any method; tech-debt is a sized trade-off, not all-or-nothing.
- The architecture/design itself routes to `ravenclaude-core/architect`; security-relevant debt to `security-reviewer`.
- End with owner / date / expected change on each recommendation.
