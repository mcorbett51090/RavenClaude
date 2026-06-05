---
scenario_id: 2026-06-05-error-budget-burn-freeze-policy
contributed_at: 2026-06-05
plugin: observability-sre
product: generic
product_version: "n/a"
scope: likely-general
tags: [error-budget, slo, freeze-policy, mttr, postmortem, ship-vs-freeze]
confidence: medium
reviewed: false
---

## Problem

A team had SLOs and an error budget on its core API but kept shipping features straight through two budget-exhausting incident weeks because "the roadmap can't slip." Reliability work was perpetually deprioritized, MTTR was climbing (each incident took longer because the last one's fixes were never done), and the SREs and product engineers were openly at war over whether to slow down. The SLO existed but changed no behavior — a vanity number.

## Constraints context

- 99.9% monthly availability SLO → ~43 minutes of monthly error budget; two incidents had burned ~110 minutes (budget blown 2.5x).
- An "error budget policy" *document* existed but had never been agreed by product leadership — so when it said "freeze on exhaustion," product simply overrode it each time.
- No clean ship-vs-freeze decision rule the on-call or the EM could point to in the moment; the argument re-litigated every incident.
- Action items from prior postmortems existed but had no owners, no dates, and no enforcement — so the same contributing factor recurred.

## Attempts

- Tried: the SREs unilaterally calling a freeze after the second incident. It held for a day, then product leadership overrode it because the policy had no prior buy-in — a freeze nobody pre-agreed isn't a policy, it's a turf fight. Outcome: worse trust, same shipping.
- Tried: tightening the SLO target (99.9 → 99.95%) to "force" more reliability investment. Made the budget *smaller* and exhausted faster, escalating the same fight — the problem was never the target, it was that exhaustion triggered no agreed action.
- Tried (the move that worked): wrote the **error-budget policy before re-touching the target**, and got it signed by engineering *and* product leadership in advance. The policy is a small, unambiguous decision rule: budget remaining → ship freely, take risk; budget < 25% → reliability work is prioritized alongside features; budget exhausted → **feature freeze** (only reliability + sev fixes ship) until the budget recovers over a rolling window. Paired it with a postmortem discipline where every action item gets an owner + a date + a tracked ticket, and freeze-exit is gated on the high-severity items being done.

## Resolution

**The error-budget policy is the decision rule, and it has to be written and pre-agreed *before* the SLO matters — not invoked for the first time mid-incident.** The sequence:

1. **Write the policy before (or with) the SLO, and get it signed by product, not just SRE.** A budget policy invoked for the first time during an incident gets overridden; one pre-agreed by the people who own the roadmap is binding. This is the "error-budget-policy-is-written-before-the-slo" rule in practice.
2. **Make it a mechanical rule, not a judgment call.** Budget remaining → ship; budget low → split focus; budget exhausted → freeze features (reliability + sev fixes only). The on-call and the EM point at the rule, not at each other.
3. **Tie freeze-exit to postmortem action items with owners and dates.** A freeze that ends on a calendar date instead of on the fixes being done just resets the clock. Gate exit on the high-severity items closing — this is what actually pulled MTTR down (the recurring contributing factor finally got fixed).
4. **Don't tighten the target to force investment.** A smaller budget exhausts faster and escalates the fight; the target should reflect what users need, and the *policy* is what converts exhaustion into action.

Once the policy was pre-signed, the next exhaustion triggered a freeze without an argument, the backlog of postmortem fixes finally shipped during it, and MTTR fell over the following two months because incidents stopped recurring from un-actioned factors.

**Action for the next consultant:** if a team has SLOs but keeps shipping through exhaustion, the missing piece is almost never the target — it's a **pre-agreed, product-signed error-budget policy** plus postmortem action items that have owners and dates. Write the policy first; the ship-vs-freeze fight disappears because the rule already decided it.

Cross-reference: [`../knowledge/observability-sre-decision-trees.md`](../knowledge/observability-sre-decision-trees.md) `## Decision Tree: SLO target — tighten, loosen, or hold?` and `## Decision Tree: Postmortem action item — fix, mitigate, or accept?`, plus the new [`sli-slo-design-decision-tree.md`](../knowledge/sli-slo-design-decision-tree.md). Field-note complement to best-practices `error-budget-is-the-decision-rule.md`, `error-budget-policy-is-written-before-the-slo.md`, and `postmortems-are-blameless.md`. This is `sre-reliability-engineer`'s lane; incident execution when the budget blows is `incident-commander`'s; the deploy gate that consumes the burn signal is `devops-cicd/release-engineer`'s.

**Sources for the cited pattern:** Google SRE Workbook, "Implementing SLOs — error budget policy" — https://sre.google/workbook/error-budget-policy/ and "Implementing SLOs" — https://sre.google/workbook/implementing-slos/ (retrieved 2026-06-05). Budget minutes and MTTR figures are illustrative for this engagement; validate against the team's own data before a deliverable.
