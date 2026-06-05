---
scenario_id: 2026-06-05-shoot-day-overtime-spiral
contributed_at: 2026-06-05
plugin: film-video-production
product: scheduling
product_version: "n/a"
scope: likely-general
tags: [overtime, turnaround, shoot-day, fringe, schedule, meal-penalty]
confidence: medium
reviewed: false
---

## Problem

A branded-content shoot scheduled for a "10-hour day" was tracking 13-hour actual days by day two, and the line producer was watching the labor line balloon. The 1st AD's instinct was "we'll make it up by pushing harder tomorrow" — start earlier, run longer. The producer wanted to know, before approving another long day, what the overtime spiral was actually costing and whether pushing tomorrow would make it worse, not better.

## Context

- Segment: branded-content / commercial, ~35-person crew, 3-day shoot, fixed client bid.
- Constraint: the schedule was built to a calendar ("3 days") rather than to a defensible one-liner of pages/setups per day (the section 3 #2 violation). Day one's scene count was simply too heavy for a 10-hour day, so the day ran to 13 hours — and the wrap-late pushed the next day's call in toward a short turnaround.
- The bid had a thin contingency and no explicit overtime line — overtime was being absorbed silently.

## Attempts

- Tried: priced the actual day with the loaded build-up rather than eyeballing it. Using [`../scripts/production_calc.py`](../scripts/production_calc.py) `shoot-day-cost` on a representative slice (crew base for the contracted day + projected worked hours + the agreement's OT thresholds + the fringe load), the "extra 3 hours" turned out to cost far more than 3/10ths of a day — overtime runs 1.5x past the contracted day and 2x past the double-time threshold, and the fringe/burden rides on top of the premium. IATSE-style contracts commonly pay time-and-a-half past 8 worked hours and double-time past 12 [verify-at-use — agreement-specific], and payroll burden (FICA + union P&H + workers' comp) commonly adds ~22–34% on top of gross wages [verify-at-use]. Outcome: the "make it up tomorrow" plan was quantified as *adding* cost, not recovering it.
- Tried: checked the turnaround. The late wrap pushed the next call inside the rest-period window; a short turnaround can trigger a forced-call penalty, so pushing tomorrow earlier would have stacked a turnaround premium on top of more overtime. Outcome: ruled out the "start earlier" fix.
- Tried (the move that worked): re-cut the one-liner. Re-sequenced setups by location to kill a company move, dropped two non-essential setups to the b-roll/pickup list, and held the call time to protect turnaround — trading a small scope cut for a return to a real 10–11-hour day. The producer surfaced the overtime exposure to the client as a change-order conversation rather than eating it.

## Resolution

The spiral was a **schedule-to-the-calendar** problem (section 3 #2), not a "crew working slowly" problem: an unrealistic day forced overtime, the late wrap threatened turnaround, and pushing harder would have compounded both. Pricing the day with the loaded overtime+fringe build-up made the cost legible, and re-cutting the one-liner (plus protecting turnaround) stopped the bleed.

**Action for the next producer hitting this pattern:** when days are running long, do **not** approve "push harder tomorrow" before pricing it. Run the loaded shoot-day cost — overtime is 1.5x/2x *plus* fringe on the premium, so an "extra 3 hours" is not 30% more, it can be ~40%+ more than the contracted-day spend. Then check turnaround before moving the next call. The durable fix is almost always re-cutting the one-liner to a realistic day (section 3 #2), not running the crew longer. Cross-reference the overtime/turnaround best-practice rules in [`../best-practices/`](../best-practices/) and the [`../skills/schedule-the-shoot/SKILL.md`](../skills/schedule-the-shoot/SKILL.md) playbook.

**Sources for the rate framing cited (retrieved 2026-06-05):** IATSE overtime/meal/turnaround structure — Media Services, *Production Meal Penalties & IATSE's Updated Rules* (https://www.mediaservices.com/blog/production-meal-penalties-iatses-new-rules/) and CMS Productions, *IATSE Rates Guide 2025-26* (https://cmsproductions.com/blog/iatse-commercial-rates/); payroll-burden range — CMS Productions, *Understanding IATSE Fringe Rates* (https://cmsproductions.com/blog/understanding-iatse-fringe-rates/) and Wrapbook, *How to Budget SAG-AFTRA Payroll* (https://www.wrapbook.com/blog/how-to-budget-sag-aftra-payroll). Thresholds, multipliers, and rates are agreement- and local-specific — validate against the project's deal memos and governing agreement before any deliverable (section 3 #8).
