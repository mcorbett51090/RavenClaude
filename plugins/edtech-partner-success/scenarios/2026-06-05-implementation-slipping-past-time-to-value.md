---
scenario_id: 2026-06-05-implementation-slipping-past-time-to-value
contributed_at: 2026-06-05
plugin: edtech-partner-success
product: onboarding
product_version: "n/a"
scope: likely-general
tags: [onboarding, time-to-value, rostering, train-the-trainer, go-live, dead-zone]
confidence: medium
reviewed: false
---

## Problem

A new K-12 partner's 90-day implementation was slipping. Week 6 of the technical-onboarding arc had arrived with rostering still not validated and no teacher had reached first meaningful use. The risk: the district was about to blow past its first-value window, and in EdTech a partner that doesn't see value early frequently never re-launches — the tool sits dormant into the next budget review.

## Context

- Segment: K-12, district rolling out across ~30 schools, single PSM-led implementation, train-the-trainer model (the only model that scales in K-12 — direct vendor-to-teacher training does not).
- Constraint: the broad SaaS time-to-value benchmark is fast — best-in-class first value within **~7 days for B2B**, and as much as **~91% of new users drop off within ~14 days** if they don't see value (Userpilot / Amplitude / Precursive). K-12 is slower (it runs on the school calendar, not a signup flow), so the operative discipline is **instrument first-value from day one and protect the go-live date from calendar dead zones** — not hit a literal 7-day clock.
- The slip had two compounding causes: a rostering sync that "succeeded" but hadn't populated correctly, and a go-live date that had drifted toward a calendar dead zone (the first two weeks of school / a testing window), where any launch lands on no one.

## Attempts

- Tried: the **calendar-dead-zone go-live check** as the highest-leverage pre-flight — confirm the go-live date is NOT inside a dead zone before anything else. Outcome: caught that the drifting date was about to land in a suppression window; re-anchored the go-live to a live week so the launch would actually reach teachers.
- Tried: the **rostering pre-flight** ("sync ran successfully" ≠ data is correct) before declaring the implementation on-track. Outcome: found the populated-but-wrong roster; coordinated the fix with the partner's admin (PSM coordinates, doesn't own the fix) before re-running anything downstream.
- Tried: **depth before breadth in stage 1** — re-scoped week 6-8 to get 2-3 champion buildings to genuine first meaningful use rather than pushing feature breadth across all 30 schools. Outcome: a real Day-30 first-value signal from the champion buildings, which then seeded the next cascade wave — instead of a shallow, district-wide non-adoption.

## Resolution

The implementation was pulled back onto its arc **because the go-live was protected from the dead zone and first-value was instrumented from day one** — so the slip was visible and fixable at week 6 rather than discovered as silent non-adoption at the Day-90 review. The order that worked: dead-zone go-live check → rostering pre-flight → depth-before-breadth re-scope → measured Day-30 first-value from champion buildings → cascade outward.

**Action for the next PSM hitting this pattern:** **the calendar-dead-zone go-live check is the single highest-leverage pre-flight; run it first.** Then rostering pre-flight before calling the implementation on-track, and re-scope to depth-before-breadth in stage 1 (get a few buildings to real first value — do NOT push feature breadth). Instrument first-value from day one so a slip is *visible*, not discovered at Day-90. The [`../scripts/psm_calc.py`](../scripts/psm_calc.py) `ttv` mode flags whether the projected first-value date lands inside a configured dead-zone window.

**Sources (retrieved 2026-06-05):**
- Userpilot — Time-to-Value benchmark report (best-in-class ~7d B2B; ideal ~1.5d): https://userpilot.com/blog/time-to-value-benchmark-report-2024/
- Precursive — what is TTV in SaaS onboarding (B2B first-value ~7d): https://www.precursive.com/post/what-is-time-to-value-ttv-in-saas-onboarding
- Internal: [`../knowledge/district-implementation-failure-modes.md`](../knowledge/district-implementation-failure-modes.md), [`../knowledge/k12-adoption-arc-fall-spring-summer.md`](../knowledge/k12-adoption-arc-fall-spring-summer.md), [`../skills/implementation-90-day-arc/SKILL.md`](../skills/implementation-90-day-arc/SKILL.md)

TTV benchmarks are generic-SaaS public figures, not K-12-calibrated — treat as `[verify-at-use]`; the K-12 first-value clock runs on the school calendar, not a signup flow (CLAUDE.md §3 cite-or-mark rule).
