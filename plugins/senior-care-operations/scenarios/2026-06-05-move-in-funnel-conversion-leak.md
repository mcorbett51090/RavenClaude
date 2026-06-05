---
scenario_id: 2026-06-05-move-in-funnel-conversion-leak
contributed_at: 2026-06-05
plugin: senior-care-operations
product: sales-funnel
product_version: "n/a"
scope: likely-general
tags: [move-in, conversion, tour, inquiry, sales-funnel, lead-response]
confidence: medium
reviewed: false
---

## Problem

A community was generating plenty of inquiries but move-ins were flat, and the operator's instinct was to **buy more leads** (raise the marketing budget). The risk: pouring more inquiries into a funnel that leaks at a known stage just raises cost-per-move-in without raising move-ins — you pay more to lose more families at the same broken step. Nobody had instrumented *where* in inquiry → tour → move-in the funnel was actually leaking.

## Context

- Segment: assisted-living + memory-care, single building, independent operator, healthy inquiry volume.
- Constraint: the senior-living sales funnel has stage-by-stage benchmarks, and the leak has to be located before it can be fixed. Public 2025–2026 benchmark ranges: **inquiry-to-tour ~29%**, **tour-to-move-in ~29–34%** (down from ~34% in 2024; top performers hit 35–42%), and **overall inquiry-to-move-in ~12–15%**. Lead-response speed is the single biggest driver — only ~18–27% of families book a tour on the first touch, so without systematic follow-up/retargeting 70%+ of the best prospects are lost.
- Cost frame: cost-per-move-in via owned channels (SEO/organic) runs ~$1,200–$2,800, but referral-agency move-ins can exceed $7,000–$12,000 (common in memory care) — so the *channel mix* of any "buy more leads" plan matters as much as the volume.
- The operator was reasoning from top-of-funnel volume without measuring the two conversion steps.

## Attempts

- Tried: **instrumented the two-stage funnel** — inquiry → tour and tour → move-in — and compared each to the benchmark. Outcome: inquiry-to-tour was the leak (well below ~29%); tour-to-move-in was actually fine. So the problem was *getting families in the door*, not closing them once they toured.
- Tried: **measured lead-response time**, since it is the dominant inquiry-to-tour driver. Outcome: median first-response was hours (sometimes next-day) — far too slow; the highest-intent inquiries had already toured a competitor. The fix was a same-hour response SLA + a structured multi-touch follow-up/retargeting cadence, not more lead spend.
- Tried: **checked the channel/cost mix before authorizing budget**, so any incremental spend went to the lowest-CPMI owned channels rather than high-fee referral sources. Outcome: reallocated, not just increased, the budget.

## Resolution

The fix was a **lead-response SLA + follow-up cadence at the leaking inquiry-to-tour step**, plus a channel-mix reallocation — **not** a blanket lead-buy. Buying more inquiries would have multiplied the same ~29%-target leak and raised cost-per-move-in. The output was a dated funnel instrument (per-stage conversion vs benchmark, response-time distribution, CPMI by channel) with the fix targeted at the measured leak.

**Action for the next consultant hitting this pattern:** **instrument the funnel stage-by-stage before buying volume.** Measure inquiry→tour and tour→move-in against benchmark, find the leaking step, and fix *that* — response speed and follow-up cadence almost always beat raw lead volume, and a lead-buy into a leaking funnel just raises cost-per-move-in. See [`../knowledge/senior-care-decision-trees.md`](../knowledge/senior-care-decision-trees.md) "Why Occupancy Is Declining" (the referral/conversion branch) and the [`../scripts/senior_calc.py`](../scripts/senior_calc.py) `move-in-funnel` mode.

**Sources (retrieved 2026-06-05):**
- USR Engage — Senior Living Marketing Benchmarks 2026 (CPL, conversion, CPMI by care type): https://usrengage.com/senior-living-marketing-benchmarks-2026/
- Aline — lead scoring / tour-to-move-in conversion benchmark (29–34%, top performers 35–42%): https://alineops.com/blog/lead-scoring-improve-conversions/
- Senior Housing News — operators level up sales to beat declining conversions: https://seniorhousingnews.com/2024/02/12/senior-living-operators-level-up-sales-to-beat-alarming-trends-in-conversions/

Conversion and cost benchmarks are date- and market-dependent — treat as `[verify-at-use]` and validate against the community's own CRM funnel data before any deliverable (§3 #8).
