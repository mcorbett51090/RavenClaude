---
name: class-schedule-and-instructor-utilization
description: "Build and read a fitness class grid: fill rate by slot and class type, the per-class break-even headcount from instructor pay plus room cost, instructor utilization, and the no-show/waitlist mechanics that reclaim held seats. Fill and instructor-pay benchmarks are verify-at-use."
---

# Class Schedule & Instructor Utilization

Every class hour is a unit of inventory with a fixed cost. **Fill is the whole game**: a half-empty class burns the same instructor pay and room as a full one.

## The per-class unit economics

```
class break-even headcount  =  (instructor pay + allocated room cost) / contribution per attendee
class fill rate             =  attended / capacity
```

Know the break-even headcount for **every slot** before you defend it on the grid. A slot that never reaches break-even is a subsidy, not a schedule.

## Reading the grid

| Signal | Read | Move |
|---|---|---|
| Slot fill < break-even, persistently | Wrong time or wrong class | Cut, merge, or re-time to demand |
| Waitlist forming repeatedly | Under-supplied demand | Add a parallel/adjacent slot |
| High booked, low attended | No-show leak | No-show/late-cancel window + auto-promote waitlist |
| One instructor's classes over-fill | Draw effect | Protect their prime slots; study why |

## Instructor pay models

| Model | Risk sits with | Best when |
|---|---|---|
| Flat per class | Studio (empty classes still cost full) | Predictable, high-fill grid |
| Per head | Instructor (shares empty-class risk) | Variable fill, growth phase |
| Base + per head | Shared | Most boutique studios — floor + upside |

Match the model to fill economics and contribution margin. All pay/fill norms are `[verify-at-use]`.

## Metrics

| Metric | Target logic | Note |
|---|---|---|
| Average class fill rate | Above break-even with headroom | The grid's health number |
| Instructor utilization | Paid hours that hit break-even fill | Not just hours taught |
| No-show rate | Low enough that "full" means full | Policy-controllable |
| Sub-coverage reliability | Near-zero cancelled classes | Cancelled class = churn risk |

## Anti-patterns

- Defending a slot on history ("it's always been Tuesday 6pm") instead of fill.
- Flat-per-class pay on a variable-fill grid (overpays empties, undersells packed).
- Reporting booked instead of attended.

## See also

- Traverse the **schedule the class grid on fill** and **instructor pay model** trees in [`../../knowledge/fitness-studio-decision-trees.md`](../../knowledge/fitness-studio-decision-trees.md).
- Benchmarks (dated, verify-at-use): [`../../knowledge/fitness-studio-reference-2026.md`](../../knowledge/fitness-studio-reference-2026.md).
- Sibling skills: [`../membership-growth-and-churn/SKILL.md`](../membership-growth-and-churn/SKILL.md), [`../member-onboarding-and-retention/SKILL.md`](../member-onboarding-and-retention/SKILL.md).
- Best practice: [`../../best-practices/schedule-the-grid-on-demand-not-habit.md`](../../best-practices/schedule-the-grid-on-demand-not-habit.md).
