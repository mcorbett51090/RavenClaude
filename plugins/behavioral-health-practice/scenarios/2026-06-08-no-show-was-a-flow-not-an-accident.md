---
scenario_id: 2026-06-08-no-show-was-a-flow-not-an-accident
contributed_at: 2026-06-08
plugin: behavioral-health-practice
product: no-show
product_version: "n/a"
scope: likely-general
tags: [no-show, access, revenue, reminder-program]
confidence: medium
reviewed: false
---

## Problem

A practice administrator blamed a thin month on 'patients who don't show up' and considered a punitive no-show fee. The risk: treating no-show as a per-patient character problem hides that it's a measurable flow with reminders, waitlist backfill, and recovery levers — and a punitive fee can suppress access without recovering the slot (§3 #1).

## Context

- Setting: outpatient behavioral health, in-person + some telehealth.
- Constraint: an empty slot is two losses — lost revenue and a patient who didn't get care; both respond to flow levers, not blame (§3 #1).
- The administrator reasoned from the aggregate 'they don't show' anecdote.

## Attempts

- Tried: **quantified the loss as a flow** (`behavioral_health_practice_calc.py no-show`). Outcome: lost slots × avg visit revenue made the monthly bleed concrete instead of anecdotal.
- Tried: **modeled a reminder-program recovery lift** against the baseline no-show rate. Outcome: a realistic lift recovered a material share of the lost revenue without any fee.
- Tried: **added waitlist + telehealth backfill** for the residual gap, routing the telehealth regulatory specifics to the licensed/legal authority (§3 #7). Outcome: more residual slots filled.

## Resolution

The fix was a **reminder + waitlist + telehealth-backfill flow with the recovery quantified** — not a punitive fee. The output was the lost-slots/revenue baseline, the modeled recovery, and the backfill plan, with no clinical or PHI content in the deliverable.

**Action for the next consultant hitting this pattern:** **manage no-show as a flow and quantify it before reaching for a fee.** Lost slots × revenue makes the bleed concrete; a reminder lift plus backfill recovers most of it. See Tree 1 and the `behavioral_health_practice_calc.py` `no-show` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
