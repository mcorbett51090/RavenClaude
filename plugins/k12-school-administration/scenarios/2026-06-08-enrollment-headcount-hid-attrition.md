---
scenario_id: 2026-06-08-enrollment-headcount-hid-attrition
contributed_at: 2026-06-08
plugin: k12-school-administration
product: enrollment
product_version: "n/a"
scope: likely-general
tags: [enrollment, retention, ada, funding]
confidence: medium
reviewed: false
---

## Problem

A business manager reported census-day enrollment 'on target' and budgeted on it, then ran short of funds. The risk: a census-day headcount is a snapshot; mid-year attrition and a soft ADA rate erode the funded base after the count, so a target headcount can still under-fund the year (§3 #1 #2).

## Context

- Organization: public elementary on an ADA-influenced funding model.
- Constraint: funding = enrollment × per-pupil × ADA; attrition and attendance both reduce it after census day (§3 #2).
- The manager reasoned from the single census number.

## Attempts

- Tried: **modeled funding as enrollment × per-pupil × ADA** (`k12_school_administration_calc.py enrollment-funding`). Outcome: a soft ADA rate cut realized funding well below the census-day budget.
- Tried: **read enrollment as a retention flow.** Outcome: mid-year attrition had shrunk the funded base after the count (§3 #1).
- Tried: **valued each attendance point.** Outcome: small ADA gains were worth real dollars — a clear recovery lever (§3 #2).

## Resolution

The fix was a **retention + attendance-recovery plan and a funded-base (not census-day) budget**, recognizing ADA and attrition as funding levers. The output was the enrollment-to-funding model, the per-attendance-point value, and the recovery plan.

**Action for the next consultant hitting this pattern:** **budget on the funded base, not the census-day headcount.** Mid-year attrition and ADA erode funding after the count; manage enrollment as a retention flow and recover attendance. See Tree 1 and the `k12_school_administration_calc.py` `enrollment-funding` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
