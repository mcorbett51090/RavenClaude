---
scenario_id: 2026-06-05-roadmap-thrash-no-prioritization-rigor
contributed_at: 2026-06-05
plugin: product-management
product: prioritization
product_version: "n/a"
scope: likely-general
tags: [prioritization, rice, wsjf, roadmap-thrash, hippo]
confidence: medium
reviewed: false
---

## Problem

A B2B SaaS team's roadmap was re-sequenced almost every sprint — whoever escalated loudest (a big customer's CSM, the loudest sales rep, an exec's pet idea) bumped to the top, and committed work was abandoned half-built. The cost wasn't a single bad call; it was **thrash**: started-then-dropped work, eroded engineering trust, and a roadmap nobody believed. The team asked for "a prioritization framework" — but the real ask was a *defensible, arguable* ranking that survived the next escalation.

## Context

- Segment: B2B SaaS, ~30-person product+eng org, quarterly planning cadence, no instrumented reach data on most features.
- Constraint: the items being ranked were **not comparable in type** — a few were time-critical (a contractual deadline, a compliance date), most were value-for-effort growth bets. Forcing them onto one scale was part of why prior attempts felt arbitrary.
- The org had tried "just use RICE" once and abandoned it because the time-critical items scored low and got buried, which discredited the whole exercise.

## Attempts

- Tried: **method-fit before method.** Split the backlog into two tracks — the handful of *time-sensitive* items (a deadline / a window closing) went to **WSJF** (cost of delay ÷ job size — `(Business Value + Time Criticality + Risk Reduction/Opportunity Enablement) ÷ Job Size`, modified-Fibonacci inputs), and the larger value-for-effort pile went to **RICE** (`(Reach × Impact × Confidence) ÷ Effort`). Outcome: the time-critical items stopped being buried by a framework that didn't model urgency, which had been the credibility killer.
- Tried: **score individually, then reveal together.** Each participant scored before the meeting; divergences >2× on any single factor were flagged as "needs information, not negotiation." Outcome: the debate moved from "I feel strongly" to "we disagree on reach by 4× — let's instrument it," which is the actual value of the exercise.
- Tried: **a forced-items list, kept separate.** Contractual/compliance commitments were pulled out of the scored ranking entirely rather than allowed to pollute it. Outcome: the scored list stayed honest, and the non-negotiables were visible as non-negotiables.

## Resolution

Thrash dropped because re-sequencing now required *arguing against a published score with stated assumptions*, not just escalating. The framework's value was never the decimal — it was making reach/impact/confidence/effort (or cost-of-delay) **explicit and arguable**, so the next escalation had to engage the evidence. The output was a ranked list with assumptions published alongside, plus a separate forced-items track.

**Action for the next PM hitting this pattern:** **pick the method that fits the decision, don't default to one.** Time-sensitivity dominant → WSJF/cost-of-delay; many items on value-for-effort → RICE; basic-vs-delighter satisfaction question → Kano; one big strategic bet → skip the spreadsheet and argue it on strategy + opportunity size. Traverse [`../knowledge/prioritization-method-selection-decision-tree.md`](../knowledge/prioritization-method-selection-decision-tree.md) before scoring. The [`../scripts/pm_calc.py`](../scripts/pm_calc.py) `rice` and `wsjf` modes do the arithmetic so the meeting argues the inputs, not the math.

**Sources (retrieved 2026-06-05):**
- Intercom — RICE: simple prioritization for product managers (formula + factor scales): https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
- Scaled Agile Framework — WSJF (cost-of-delay ÷ job size, the three CoD inputs): https://framework.scaledagile.com/wsjf
- ProductPlan — RICE Scoring Model: https://www.productplan.com/glossary/rice-scoring-model

Framework figures (impact 3x/2x/1x/0.5x/0.25x; confidence 100/80/50%; Fibonacci 1-2-3-5-8-13-20) are the published Intercom/SAFe scales — treat the *application* to a specific backlog as `[verify-at-use]` and calibrate to the team's data.
