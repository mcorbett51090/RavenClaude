# Early-alert signals must lead, not lag

**Status:** Pattern.

**Rule:** An early-alert system is only useful if it fires while intervention can still change the
outcome. Build it on **leading** signals (attendance, LMS engagement, midterm/gateway grades,
financial holds), not **lagging** ones (a failed semester, an end-of-year withdrawal).

## Why

The entire value of early alert is the word "early." A signal that arrives after the student has
already disengaged, failed the term, or left is a post-mortem, not an intervention trigger. Leading
signals appear while the student is still enrolled and still recoverable — a drop in LMS logins or an
early no-show streak precedes withdrawal by weeks. Designing the system around lagging signals feels
rigorous (they're unambiguous) but guarantees the alert fires too late to act on.

## What it looks like in practice

- The risk score is built from leading signals and tiered into an intervention ladder (watch /
  elevated / high).
- Midterm and gateway-course grades are used as recoverable academic signals, not end-of-term GPA.
- Financial holds and aid gaps are caught early, as solvable barriers, before they force a stop-out.

## Anti-pattern

An "early-alert" dashboard driven by term GPA and census-date non-return — accurate, unambiguous, and
useless for intervention because the loss has already happened. The signal set, not the dashboard, is
what makes early alert early.
