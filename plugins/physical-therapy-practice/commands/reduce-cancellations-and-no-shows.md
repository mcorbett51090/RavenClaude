---
description: "Reduce cancellations and no-shows — measure the rate, segment by reason/slot/clinician/episode-position, prescribe interventions on the real driver, and redesign the schedule template to demand and no-show behavior."
---

# /reduce-cancellations-and-no-shows

Spawn `scheduling-and-patient-flow-analyst` to diagnose and reduce missed visits while protecting
plan-of-care adherence.

## What it does

1. Measures cancellation/no-show rate, visit utilization, and plan-of-care adherence via [`../scripts/pt_calc.py`](../scripts/pt_calc.py).
2. Segments cancellations by reason, slot, clinician, and episode position.
3. Prescribes the matching intervention (reminders, scheduling friction, plan-of-care framing, access).
4. Redesigns the schedule template (slot mix, wave/overbook for expected no-shows).

## Usage

```
/reduce-cancellations-and-no-shows
```

Then share your cancellation data (by reason/slot if available). The agent applies
[`patient-flow-and-plan-of-care-adherence`](../skills/patient-flow-and-plan-of-care-adherence/SKILL.md).

## Good inputs

- Cancellation/no-show counts with reasons and time slots.
- Visits prescribed vs. delivered per episode (for the adherence view).
