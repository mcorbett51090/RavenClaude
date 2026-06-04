---
description: "Build a staffing model on acuity-weighted hours-per-resident-day, not a fixed ratio, so labor matches need. Reach for this on a labor question."
argument-hint: "[the situation, e.g. the metric/segment in question]"
---

# Staff to acuity-based PPD

You are running `/senior-care-operations:staff-to-acuity-based-ppd` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Weight the census by acuity — Acuity-weighted resident days (§3 #3).
2. Set care hours per resident day — Target PPD by acuity and shift.
3. Schedule to the model — Build the schedule to the acuity-based hours.
4. Cut agency reliance — Reduce premium agency labor against the model (§3 #6).

## Output
An acuity-weighted PPD staffing model, a schedule, and an agency-reliance reduction. See [`../skills/staff-to-acuity-ppd/SKILL.md`](../skills/staff-to-acuity-ppd/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method.
- No client PII; cite or mark every external figure.
