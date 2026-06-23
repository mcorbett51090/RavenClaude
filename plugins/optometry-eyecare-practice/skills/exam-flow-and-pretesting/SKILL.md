---
name: exam-flow-and-pretesting
description: "Engineer the exam lane: pretesting/workup done by a tech before the doctor enters, a workup-to-doctor handoff that protects chair time, and a tech-to-doctor ratio that lets one doctor run multiple lanes. Protect the scarcest resource — the doctor's chair."
---

# Exam Flow & Pretesting

The doctor's chair time is the scarcest resource in the building. Exam-flow design exists to protect it.

## The flow

```
check-in -> pretest/workup (tech) -> doctor exam (lane) -> exam-exit handoff -> optical / checkout
```

1. **Pretest off the doctor's chair.** Tech-run workup (autorefraction, tonometry, retinal imaging per protocol) completed before the doctor enters is what lets one doctor cover multiple lanes. Workup in the doctor's chair is wasted chair time.
2. **Tune the tech-to-doctor ratio.** If the doctor is doing workup, the constraint is delegation, not capacity. The ratio is the throughput dial.
3. **Match exam length to exam type.** Feeds the schedule template — see [`../schedule-and-recall-management/SKILL.md`](../schedule-and-recall-management/SKILL.md).
4. **Design the exam-exit handoff.** This is where optical capture is won — a warm handoff to the optician, in workflow. See [`../optical-capture-and-dispensary/SKILL.md`](../optical-capture-and-dispensary/SKILL.md).

> Clinical workup content (which tests, in what order, for which exam type) is protocol- and license-driven — `[verify-at-use]`; this skill addresses the *flow*, not the clinical decision.

## Metrics

| Metric | Reads |
|---|---|
| Lane utilization | doctor minutes used / available |
| Pretest completion before doctor | % of patients fully worked up before the lane |
| Cycle time per exam type | check-in to checkout |

## Anti-patterns

- Pretesting in the doctor's chair.
- A schedule template blind to exam type.
- Letting the exam-exit handoff fall to chance (leaks optical capture).

## See also

- [`../schedule-and-recall-management/SKILL.md`](../schedule-and-recall-management/SKILL.md), [`../optical-capture-and-dispensary/SKILL.md`](../optical-capture-and-dispensary/SKILL.md).
- Best practice: [`../../best-practices/recall-drives-the-schedule.md`](../../best-practices/recall-drives-the-schedule.md).
