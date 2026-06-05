---
scenario_id: 2026-06-05-contingency-burn-before-wrap
contributed_at: 2026-06-05
plugin: film-video-production
product: finance
product_version: "n/a"
scope: likely-general
tags: [contingency, cost-report, burn-rate, weather-day, forecast, overage]
confidence: medium
reviewed: false
---

## Problem

Halfway through a documentary-style shoot, the production-finance analyst had drawn a chunk of the contingency to cover a weather day and an equipment-rental overrun. The producer's read was "we still have contingency left, we're fine." The analyst's instinct said otherwise but couldn't articulate the risk — was the remaining buffer actually enough to reach wrap?

## Context

- Segment: documentary / unscripted, ~18 shoot-days, lean budget, a real 10%-of-BTL+post contingency line [verify-at-use — industry convention].
- Constraint: contingency was being tracked as a *balance* ("how much is left") rather than a *rate* ("how fast are we spending it relative to days remaining"). A positive balance at day 9 can still mean insolvency at day 18 if the burn rate outpaces the days.
- The weather day and the rental overrun weren't one-offs — the shoot was weather-exposed for several more days, so the burn was likely to continue.

## Attempts

- Tried: stopped reading the contingency as a balance and computed the **burn rate**. Using [`../scripts/production_calc.py`](../scripts/production_calc.py) `contingency` (base, rate, drawn-to-date, days-elapsed, days-total), the tool projected the total draw at the current per-shoot-day burn — and showed the reserve exhausting *before* wrap, with shoot-days still ahead. Outcome: turned "we still have some left" into "at this rate we run out on day ~15 of 18."
- Tried: classified the overage before deciding how to cover it. The weather day was genuine risk (legitimately a contingency draw); the rental overrun was partly rate creep against the budget (a deal-memo/PO problem to audit, not necessarily a contingency event). Outcome: recovered some headroom by re-forecasting the rental line rather than absorbing it as contingency.
- Tried (the move that worked): re-forecast at the half-way point and surfaced the projected shortfall to the EP/financier *with shoot-days still ahead*, with options (tighten the remaining schedule, reduce a scope element, or request additional funding) — instead of discovering the shortfall at wrap when no options remain.

## Resolution

The risk was invisible because contingency was tracked as a **balance, not a burn rate** (section 3 #4 — contingency is managed, not hoped). Projecting the burn against days-remaining exposed an exhaustion-before-wrap that a positive balance had hidden, and surfacing it early kept real options open.

**Action for the next analyst hitting this pattern:** never report the contingency as just a remaining balance — report the **burn rate and the projected exhaustion day** against shoot-days remaining. A positive buffer at the midpoint is not safety if the burn outpaces the calendar. Classify each draw (genuine risk → contingency; rate creep → audit the deal memo/PO) before absorbing it, and re-forecast and escalate *with days still ahead*, because the value of the early warning is the options it preserves. Cross-reference the contingency and cost-tracking best-practice rules in [`../best-practices/`](../best-practices/), the "Budget Overage — Classify Before Cutting" tree in [`../knowledge/production-decision-trees.md`](../knowledge/production-decision-trees.md), and the [`../skills/track-cost-vs-bid/SKILL.md`](../skills/track-cost-vs-bid/SKILL.md) playbook.

**Sources for the contingency framing cited (retrieved 2026-06-05):** contingency convention (10% of BTL+post, held against overages, financier/bond-expected) — Beverly Boy, *What Is Contingency Percentage in Film Budget?* (https://beverlyboy.com/filmmaking/what-is-contingency-percentage-in-film-budget/); ELEMENT CPAs, *Film Production Budgeting Mistakes That Cost Millions* (https://elementcpas.com/film-production-budgeting-mistakes-that-cost-millions/). The contingency rate and base are project-specific — validate against the actual bid and financier requirements before any deliverable (section 3 #4, #8).
