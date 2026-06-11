---
scenario_id: 2026-06-11-early-alert-fired-too-late
contributed_at: 2026-06-11
plugin: higher-education-administration
product: early-alert
product_version: "n/a"
scope: likely-general
tags: [early-alert, leading-signals, retention, ferpa]
confidence: medium
reviewed: false
---

## Problem

An institution had an "early-alert" dashboard, yet advisors said it never helped them save a student.
The risk: the dashboard was driven by term GPA and census-date non-return — accurate but lagging
signals that fire after the student is already gone.

## Context

- Surface: a retention early-alert system built on the cleanest available data.
- Constraint: the value of early alert is entirely in firing while intervention can still change the
  outcome.
- The team had also stood the dashboard up without scoping access to legitimate educational interest.

## Attempts

- Tried: **replaced the signal set with leading signals** (attendance/early no-shows, LMS engagement
  drop, midterm/gateway grades, financial holds) and scored them via `higher_ed_calc.py
  early_alert_score`. Outcome: alerts now fired weeks earlier, while students were still recoverable.
- Tried: **built the tiered intervention ladder** (watch / elevated / high) with owners. Outcome:
  advisors had a defined action per tier instead of a list they couldn't act on.
- Tried: **scoped the data flow to legitimate educational interest** (FERPA). Outcome: the risk data
  reached the advisors who needed it and no one who didn't.

## Resolution

The fix was to **rebuild early alert on leading signals with a tiered intervention ladder, scoped
FERPA-aware** — not to refine the lagging dashboard. The output was the leading-signal risk score, the
intervention ladder, and the access map.

**Action for the next consultant hitting this pattern:** **check whether the signals lead or lag
before trusting an early-alert system.** A dashboard on term GPA is a post-mortem. See
`best-practices/early-alert-signals-must-lead-not-lag.md`,
`best-practices/ferpa-is-a-design-constraint-not-an-afterthought.md`, and
`knowledge/retention-and-student-success-reference.md`.
