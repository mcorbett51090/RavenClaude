---
scenario_id: 2026-06-11-stable-headcount-hid-a-cohort-cliff
contributed_at: 2026-06-11
plugin: higher-education-administration
product: student-success
product_version: "n/a"
scope: likely-general
tags: [retention, cohort, persistence, first-year-cliff, data-definitions]
confidence: medium
reviewed: false
---

## Problem

Total enrollment had been flat for three years, so leadership assumed retention was fine. The risk:
new students were masking the loss of returning ones, and a point-in-time headcount can hold steady
while each entering cohort hemorrhages.

## Context

- Surface: a board report citing stable total headcount as evidence of health.
- Constraint: retention is a cohort phenomenon; only entering-cohort persistence shows the real story.
- Two offices also reported slightly different "enrollment" — a definitions problem underneath.

## Attempts

- Tried: **pinned the data definitions first** (census date, headcount vs. FTE, cohort rules) so the
  numbers reconciled. Outcome: a single source of truth and comparable cohorts.
- Tried: **reframed retention by entering cohort** via `higher_ed_calc.py retention_rate`. Outcome:
  year-1→year-2 persistence had fallen to 74% even as total headcount held — a real cliff, hidden.
- Tried: **segmented the year-1→year-2 drop** by entering characteristics. Outcome: the loss
  concentrated in first-gen and high-financial-need students — a targetable driver.

## Resolution

The fix was to **report retention by entering cohort, not headcount, after settling the definitions —
then target the first-year cliff in the highest-attrition segment**. The output was the reconciled
definitions, the cohort persistence analysis, and the segmented driver.

**Action for the next consultant hitting this pattern:** **never read stable total enrollment as
healthy retention.** Settle the definitions, then frame by entering cohort and look at the year-1→year-2
transition. See `best-practices/measure-cohorts-not-snapshots.md`,
`best-practices/define-the-metric-before-you-report-it.md`, and
`knowledge/retention-and-student-success-reference.md`.
