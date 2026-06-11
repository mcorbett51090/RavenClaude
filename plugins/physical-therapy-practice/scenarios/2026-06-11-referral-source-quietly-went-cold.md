---
scenario_id: 2026-06-11-referral-source-quietly-went-cold
contributed_at: 2026-06-11
plugin: physical-therapy-practice
product: referral-pipeline
product_version: "n/a"
scope: likely-general
tags: [referral-management, conversion, speed-to-contact, growth]
confidence: medium
reviewed: false
---

## Problem

A clinic's new-patient volume slid for two months before anyone noticed, then scrambled to launch
marketing. The risk: most volume came from a handful of physician referrers, and one high-volume
source had quietly drifted away — a loss no general marketing campaign would efficiently replace.

## Context

- Surface: referrals treated as a passive inflow, not a managed pipeline.
- Constraint: referral volume is concentrated, so a single cold source can outweigh broad marketing.
- No one tracked referral volume by source over time, so the drift was invisible.

## Attempts

- Tried: **tracked referral volume and trend by source**. Outcome: one orthopedic group's referrals
  had fallen ~70% after a staffing change there — the whole decline traced to it.
- Tried: **measured referral → evaluation conversion** via `pt_calc.py referral_conversion_rate`.
  Outcome: a secondary leak too — slow speed-to-contact was losing newly-referred patients to faster
  competitors.
- Tried: **re-engaged the cold source and tightened speed-to-contact** (same-day call, outcome updates
  back to referrers). Outcome: the source partially recovered and conversion improved.

## Resolution

The fix was to **manage referrals as a pipeline — track volume by source, re-engage the cold one, and
fix speed-to-contact — and close the loop with outcome updates** — not to spray marketing. The output
was the referral-source analysis, the conversion fix, and the relationship plan.

**Action for the next consultant hitting this pattern:** **watch referral volume by source like a
sales pipeline; a cold major source beats any campaign for impact.** See
`best-practices/the-referral-relationship-is-the-pipeline.md` and
`knowledge/referral-and-revenue-cycle-reference.md`.
