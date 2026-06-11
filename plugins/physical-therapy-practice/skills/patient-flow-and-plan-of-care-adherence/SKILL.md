---
name: patient-flow-and-plan-of-care-adherence
description: "Reduce cancellations and lift plan-of-care adherence and visit utilization — measure the leak, segment cancellations by reason/slot/clinician, design interventions that keep episodes complete, and redesign the schedule template to demand and no-show behavior."
---

# Patient Flow & Plan-of-Care Adherence

**Purpose:** keep prescribed episodes of care complete — treating a missed visit as a broken episode
first and a revenue leak second — by measuring the leak, finding its driver, and intervening on both
the clinical and operational sides.

---

## Steps

### 1. Measure the leak by cohort

Use [`../../scripts/pt_calc.py`](../../scripts/pt_calc.py) for cancellation/no-show rate, visit
utilization, and plan-of-care adherence (visits delivered ÷ visits prescribed across the episode).
Frame adherence across the episode, not per day.

### 2. Segment cancellations before prescribing

| Segment by… | Reveals |
|---|---|
| Reason (illness, transport, cost, forgot, felt better) | Which intervention applies |
| Slot/time | Scheduling-friction or access patterns |
| Clinician | Engagement/relationship effects |
| Episode position (early vs. late) | Where dropout concentrates |

"Felt better" mid-episode is a clinical-engagement problem — the patient doesn't see why finishing
matters — not a reminder problem.

### 3. Intervene on the real driver

| Driver | Intervention |
|---|---|
| Forgot | Reminder cadence (text/call), confirmation |
| Scheduling friction | Easier rebooking, standing appointments |
| "Felt better" / low engagement | Plan-of-care framing: tie remaining visits to the functional goal |
| Access (transport/cost) | Telehealth where appropriate, payer/financial counseling |

### 4. Redesign the schedule template

Match slot mix (eval vs. follow-up) to demand, and use wave/controlled-overbook logic sized to
expected no-show behavior — not a flat grid that leaves holes when no-shows hit.

### 5. Watch it weekly

A weekly dashboard: cancellation/no-show rate, visit utilization, plan-of-care adherence,
arrival-to-treatment time — each with a trigger threshold.

---

## Output

A cancellation analysis, a plan-of-care-adherence diagnosis, and a schedule-template redesign. Route
recovered-visit P&L valuation to the practice lead.
