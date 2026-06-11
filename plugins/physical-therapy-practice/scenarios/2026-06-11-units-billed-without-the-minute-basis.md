---
scenario_id: 2026-06-11-units-billed-without-the-minute-basis
contributed_at: 2026-06-11
plugin: physical-therapy-practice
product: billing-units
product_version: "n/a"
scope: likely-general
tags: [8-minute-rule, timed-units, documentation, denials, audit]
confidence: medium
reviewed: false
---

## Problem

A clinic was billing four units per visit "because that's what a full visit is," and a payer audit
flagged the units as unsupported. The risk: timed CPT units follow documented total timed minutes
under the 8-minute rule, and units assigned by habit have no minute basis to defend them.

## Context

- Surface: timed-code unit assignment, disconnected from the documented minutes.
- Constraint: a unit without a documented timed-minute basis is a denial and an audit exposure.
- The clinicians recorded the visit but not the total timed minutes per timed service.

## Attempts

- Tried: **recomputed the supportable units from the documented minutes** via `pt_calc.py
  eight_minute_rule_units`. Outcome: several visits had only 35–40 documented timed minutes — 3 units,
  not 4 — so the habitual 4-unit billing was unsupported.
- Tried: **separated timed from untimed (service-based) codes** in the count. Outcome: an untimed code
  had been folded into the timed total, inflating units further.
- Tried: **moved minute capture to the point of care** so units derive from recorded minutes. Outcome:
  units now trace to documented minutes and survive review.

## Resolution

The fix was to **record total timed minutes at the point of care and derive units from the 8-minute
rule** — separating timed from untimed codes — not to bill a habitual unit count. The output was the
units review, the timed/untimed correction, and the point-of-care minute-capture change.

**Action for the next consultant hitting this pattern:** **no unit without the documented minute
basis behind it.** Recompute units from recorded minutes and keep untimed codes separate. See
`best-practices/the-eight-minute-rule-governs-units.md` and
`knowledge/billing-units-and-denials-reference.md`. Verify against current CMS/payer policy and a
certified coder.
