---
name: schedule-and-recall-management
description: "Build the eye-care schedule off recall: set recall/recare intervals by exam type, template exam-length to exam-type, and read capacity as lanes x exam length x fill rate. Recall, not walk-ins, is the primary schedule-filler."
---

# Schedule & Recall Management

The schedule is an output of the **recall engine**, not a calendar you hope fills.

## The loop

1. **Set the recall interval by exam type.** Routine refraction, contact-lens recheck, and medical follow-up (diabetic, glaucoma) carry different intervals. See the recall-cadence tree in [`../../knowledge/eyecare-practice-decision-trees.md`](../../knowledge/eyecare-practice-decision-trees.md). Intervals are clinical-protocol driven — treat the reference values as `[verify-at-use]`.
2. **Template the day to exam type.** Map slot length to exam type so a comprehensive new-patient exam doesn't get a refraction-sized slot. A mismatched template either idles lanes or runs the doctor behind.
3. **Read capacity honestly.** Capacity = lanes x (slots per lane) x fill rate. A half-full schedule is a *recall* problem, not a *capacity* problem — don't add a lane to fix a fill-rate gap.
4. **Pretest off the doctor's chair.** Tech-run workup before the doctor enters is what lets one doctor cover multiple lanes — see [`../exam-flow-and-pretesting/SKILL.md`](../exam-flow-and-pretesting/SKILL.md).

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Recall reactivation rate | % of due patients rebooked | The schedule's leading indicator |
| Schedule fill rate | booked / available slots | Low fill -> work recall before adding capacity |
| Lane utilization | doctor minutes used / available | High behind-schedule -> pretesting/template issue |

## Anti-patterns

- Filling the schedule with walk-ins while the recall list ages.
- One slot length for every exam type.
- Adding a lane or a tech before confirming the schedule is actually full.

## See also

- [`../exam-flow-and-pretesting/SKILL.md`](../exam-flow-and-pretesting/SKILL.md), [`../../templates/recall-campaign-plan.md`](../../templates/recall-campaign-plan.md).
- Best practice: [`../../best-practices/recall-drives-the-schedule.md`](../../best-practices/recall-drives-the-schedule.md).
