---
description: "Read the childcare enrollment funnel and waitlist end to end — inquiry to start by stage, waitlist by age band, tour follow-up cadence, and billing route — and work the waitlist before any tuition discount (subsidy specifics verify-at-use)."
argument-hint: "[funnel counts by stage + waitlist by age + open seats]"
---

You are running `/childcare-early-education:model-enrollment`. Use `enrollment-and-family-manager` + `childcare-center-lead` and the `enrollment-and-waitlist-management` + `tuition-and-subsidy-billing` skills.

> Advisory, not financial advice. Subsidy rules are `[verify-at-use, state-specific]`. No child/family PII — work in cohorts, stages, and counts.

## Steps
1. Capture the funnel counts by stage (inquiry -> tour -> application -> start) and the waitlist by age band and desired start.
2. Traverse the **enrollment / waitlist** tree in `knowledge/childcare-decision-trees.md`: name the leaking stage and check whether a convertible waitlist exists for the open age band.
3. Confirm the **tour follow-up cadence** is running (same-day, decision-window, waitlist-or-start ask) — the funnel most often leaks here.
4. For committed families, route the seat via the **tuition vs subsidy billing** tree (private / subsidy / blended), flagging every subsidy specific `[verify-at-use, state-specific]`.
5. Only recommend a tuition discount **after** the waitlist is worked and the funnel is converting; hand capacity/tuition-model calls to `childcare-center-lead`.
6. Emit using `templates/enrollment-funnel-tracker.md` + the Structured Output block.
