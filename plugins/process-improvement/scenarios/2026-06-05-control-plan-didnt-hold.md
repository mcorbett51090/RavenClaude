---
scenario_id: 2026-06-05-control-plan-didnt-hold
contributed_at: 2026-06-05
plugin: process-improvement
product: control-plan
scope: likely-general
tags: [control-plan, sustain, regression, owner, standard-work]
confidence: medium
reviewed: false
---

## Problem

A warehouse pick-error DMAIC had cut the error rate by more than half in the pilot — a celebrated win. Eight months later the error rate had **drifted back to the original level**, and the team was about to re-run the *same* analysis on the *same* problem. The ask: "why didn't the fix stick, and how do we stop re-discovering it?"

## Context

- Sector: distribution / fulfillment; pick error was a customer-facing quality metric with a chargeback cost.
- Constraint: the original team had disbanded at project close; no one currently "owned" the improved process.
- The Improve phase had produced a real, effective countermeasure (a scan-verify step), but the Control phase had been thin — a slide deck, not a system.

## Attempts

- Tried: audited the original **control plan** against the four required elements (control chart + reaction plan + standard work + named owner). Found: the control chart had been built but stopped being maintained after month two; the standard work existed as a one-page doc but wasn't in onboarding; **the owner was listed as a role ("Shift Lead"), not a named person.** Outcome: diagnosed the regression as a Control-phase failure, not an Improve-phase failure. `[ESTIMATE]` timeline, illustrative.
- Tried: traced *why* the scan-verify step decayed. New hires were never trained on it (not in standard work / onboarding); when a "Shift Lead" rotated, no individual felt accountable for the chart or the reaction plan. Outcome: the orphaned-owner pattern — the single most common cause of gain regression.
- Tried (the move that worked): rebuilt the control plan with a **named individual owner**, folded the standard work into onboarding, restarted the control chart with a written reaction plan (what to do when a signal fires), and set a quarterly control-plan review. Outcome: the error rate held at the improved level through the next two quarters; no re-analysis needed.

## Resolution

The fix didn't fail — the **control plan** did. An improvement without a maintained control chart, a reaction plan, standard work *embedded in onboarding*, and a **named** owner is a temporary deviation from the old process; regression is the default. "A fix without a control plan didn't happen."

**Action for the next Black Belt hitting this pattern:** when a prior gain has regressed, do **not** re-run the analysis first — audit the control plan against the four elements, and check the **owner is a named person, not a role** (an orphaned plan is the most common regression cause). Cross-reference [`../best-practices/a-fix-without-a-control-plan-didnt-happen.md`](../best-practices/a-fix-without-a-control-plan-didnt-happen.md) and [`../best-practices/control-plan-owner-must-be-a-named-person-not-a-role.md`](../best-practices/control-plan-owner-must-be-a-named-person-not-a-role.md), and use the [`../templates/control-plan.md`](../templates/control-plan.md) template. Control is a *phase*, not a closeout slide (CLAUDE.md §3 #6).

**Sources for facts cited:** the four control-plan elements and the named-owner rule are this plugin's best-practices (linked above), grounded in standard DMAIC Control-phase practice. Figures are illustrative `[ESTIMATE]`; validate against the operation's actual error-rate history.
