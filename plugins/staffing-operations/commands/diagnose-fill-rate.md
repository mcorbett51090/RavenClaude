---
description: "Diagnose a fill-rate move in the order that prevents the wrong fix — pin the denominator, check the seasonal boundary, split supply from order-quality, pair with time-to-fill including the credentialing clock, and only then look at recruiters."
argument-hint: "[the move and segment, e.g. 'allied fill fell 71% to 62% last quarter']"
---

# Diagnose a fill-rate move

You are running `/staffing-operations:diagnose-fill-rate` for `$ARGUMENTS`. Run the diagnosis the way the `staffing-operations-analyst` does — in the order that prevents the expensive wrong-first-pick (treating an order-quality problem as a recruiter problem).

## Steps (traverse top-to-bottom; do not skip)
1. **Pin the denominator** — which fill-rate formula, same in both periods? A denominator shift can fake a decline ([`../skills/fill-rate-diagnostics/SKILL.md`](../skills/fill-rate-diagnostics/SKILL.md)).
2. **Check the seasonal boundary** (§3 #5) — re-cut YoY same-period if it crosses one.
3. **Split supply vs. order-quality** (§3 #6) — submittals-per-workable-order down (supply) vs. workable orders uncompetitive/aged (order-quality).
4. **Pair with time-to-fill** (§3 #2) — classify high-fill/slow vs. low-fill/fast.
5. **Include the credentialing clock** (§3 #7) — measure to start, not accept.
6. **Only now** examine recruiter execution, normalized for reqs-per-recruiter (§3 #4).

Traverse the **`## Decision Tree: Fill rate has declined`** in [`../knowledge/staffing-decision-trees.md`](../knowledge/staffing-decision-trees.md).

## Output
Rank the **two likeliest causes** with the evidence behind each and the data that would confirm. Use [`../templates/recruiting-funnel-analysis.md`](../templates/recruiting-funnel-analysis.md) if the leak is funnel-stage-specific.

## Guardrails
- Resist a single-cause story — fill moves are usually two things at once.
- Don't reach the recruiter-execution step before ruling out supply, order-quality, seasonality, and credentialing.
