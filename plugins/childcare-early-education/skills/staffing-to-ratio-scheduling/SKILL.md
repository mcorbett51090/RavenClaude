---
name: staffing-to-ratio-scheduling
description: "Schedule staff to the required ratio at a cost the tuition covers: model labor as a step function that jumps a whole teacher at each ratio boundary, cover open/close and breaks in ratio, and read the ratio-driven labor cost per room against its revenue. State-specific ratios verify-at-use."
---

# Staffing to Ratio Scheduling

Staffing to ratio is where **compliance and the cost model meet**. Labor is the dominant cost in a center, and it does not slide smoothly — it **steps up a whole teacher** each time a room crosses a ratio boundary. Ratios are state-specific and `[verify-at-use]`.

## The loop

1. **Model labor as a step function.** For each age group, the required ratio sets how many children one teacher covers. Adding the child that crosses the boundary adds a whole teacher's cost, not a fraction — see the staff-a-room-to-ratio tree in [`../../knowledge/childcare-decision-trees.md`](../../knowledge/childcare-decision-trees.md).
2. **Cover the whole day in ratio.** Ratio must hold at open, at close, and through breaks and nap transitions — the schedule, not just the roster, must never dip below ratio. Openers/closers and float coverage are part of the model.
3. **Only count ratio-countable staff.** Qualified, verified adults count toward ratio; others don't — coordinate with [`../ratios-and-licensing-compliance/SKILL.md`](../ratios-and-licensing-compliance/SKILL.md) so the schedule's headcount is the *compliant* headcount.
4. **Read cost per room against revenue.** Compute the ratio-driven labor cost of each room and compare it to the room's tuition revenue at current enrollment. A partly-filled room can be underwater because the teacher is fixed while the tuition scales with enrolled children.
5. **Fill toward the next boundary, deliberately.** A room just over a boundary (one extra child forcing a second teacher) is the least efficient state — fill it toward full or don't cross the boundary. That capacity-and-margin call is `childcare-center-lead`'s.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Ratio-driven labor cost / room | teachers required × cost | The step function, per room |
| Revenue per enrolled child / room | tuition ÷ enrolled | Compare to the labor step |
| Enrollment vs ratio boundary | children to next teacher | Just-over-boundary = least efficient |
| Coverage-in-ratio all day | open/close/breaks held | Schedule, not roster |

## Anti-patterns

- Averaging labor cost instead of modeling the whole-teacher step.
- Scheduling to ratio at midday but dropping below it at open/close or breaks.
- Counting non-ratio-countable adults to hit a number.
- Running a room one child over a boundary indefinitely.

## See also

- [`../ratios-and-licensing-compliance/SKILL.md`](../ratios-and-licensing-compliance/SKILL.md), [`../../templates/ratio-staffing-plan.md`](../../templates/ratio-staffing-plan.md).
- Best practices: [`../../best-practices/staff-to-ratio-is-the-cost-model.md`](../../best-practices/staff-to-ratio-is-the-cost-model.md), [`../../best-practices/ratios-are-a-floor-not-a-target.md`](../../best-practices/ratios-are-a-floor-not-a-target.md).
