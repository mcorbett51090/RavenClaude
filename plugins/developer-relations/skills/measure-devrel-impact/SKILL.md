---
name: measure-devrel-impact
description: Build a DevRel scorecard anchored in developer success — TTFHW, activation rate, retention, content engagement, and the qualitative product-feedback loop — and run the vanity-metric screen that demotes raw follower/star/view counts. Reach for this when the user asks "what should our DevRel KPIs be?" or "are our DevRel metrics any good?". Used by `devrel-strategist` (primary) and `developer-advocate`.
---

# Skill: measure-devrel-impact

> **Invoked by:** `devrel-strategist` (primary) for the team scorecard; `developer-advocate` for measuring a single piece of content's impact.
>
> **When to invoke:** "what should our DevRel KPIs be?"; "are these metrics measuring anything?"; "prove DevRel's impact"; replacing a vanity-metric dashboard.
>
> **Output:** an activation/retention-anchored scorecard + a vanity-vs-actionable audit + the qualitative feedback loop wired to PM/eng. Reference: [`../../knowledge/devrel-metrics.md`](../../knowledge/devrel-metrics.md).

## Procedure

1. **Tie every metric to a funnel stage and a goal.** A metric with no decision attached is decoration. Map the candidate scorecard onto the AAARRP funnel ([`design-developer-funnel`](../design-developer-funnel/SKILL.md)).
2. **Run the vanity-metric screen.** For each metric, ask: *does it measure the developer's success or our reach?* Followers, GitHub stars, page views, impressions, and likes are **reach** — leading indicators at best, traps at worst. Demote each to "leading" or cut it; never let one be a headline KPI.
3. **Anchor the headline metrics in developer success:**
   - **TTFHW** — time to first hello-world (the activation lever).
   - **Activation rate** — % of acquired developers who reach first hello-world.
   - **Retention** — week-2 / week-4 still-active developers.
   - **Content engagement** — completion / runs-the-sample, not raw views.
   - **Qualitative feedback throughput** — friction items routed to PM/eng per cycle.
4. **Define each metric's formula** (numerator / denominator / window) so it's reproducible — see the definitions in [`../../knowledge/devrel-metrics.md`](../../knowledge/devrel-metrics.md).
5. **Wire the qualitative loop.** Quantitative metrics tell you *that* developers leak; qualitative feedback tells you *why*. Make the DX-feedback artifact a standing input to PM/eng, not an anecdote ([`../../best-practices/close-the-product-feedback-loop.md`](../../best-practices/close-the-product-feedback-loop.md)).
6. **Report the scorecard** with each metric labeled headline / leading / cut, and the one north-star the team will be judged on.

## Worked example

> User: "Our DevRel dashboard is Twitter followers, GitHub stars, and blog views. Is that good?"

- Vanity screen: all three are **reach** metrics — they go up with effort and say nothing about whether developers succeed. None survives as a headline KPI.
- Replacement scorecard: north-star = **activation rate** (signup → first hello-world); supporting headline = **TTFHW** and **week-4 retention**; content measured by **sample-app runs / completion**, not views.
- Demote (keep as leading only): stars/followers/views — fine as awareness leading indicators, never as the number the team is judged on.
- Qualitative loop: stand up a monthly DX-feedback digest to PM/eng from community + sample-building friction.

## Guardrails
- A vanity metric is never a headline KPI — demote it to "leading" or cut it (see [`../../best-practices/close-the-product-feedback-loop.md`](../../best-practices/close-the-product-feedback-loop.md)).
- Every metric needs a formula (numerator/denominator/window) and a decision it informs — no decoration metrics.
- Don't report quantitative metrics without the qualitative loop that explains them; "activation dropped" with no "why" can't be acted on.
