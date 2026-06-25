---
name: optimize-class-schedule
description: "Optimize the class schedule on capacity: build a per-slot utilization grid (attendance / capacity), read waitlists, and make prune/grow/move calls against a target fill band with instructor cost-per-class accounted for."
---

# Optimize Class Schedule

The schedule is a P&L, not a calendar. Optimize it on **utilization per slot**, with cost on the table.

## Build the utilization grid
One row per **slot** = day × time × format. For each:

```
Fill rate = avg attendance / capacity
Revenue per class  ≈ avg attendance × revenue-attributable-per-visit
Instructor cost per class = pay for that slot (per the pay model)
Margin per class = revenue per class − instructor cost − marginal room cost
```

## Read it against a target fill band

| Fill rate | Read | Action |
|---|---|---|
| Chronically below band (e.g. < ~60% `[verify-at-use]`) | Underutilized; burning instructor + room | Move time, merge, change format, or cut |
| In band (~60-85% `[verify-at-use]`) | Healthy | Hold |
| Chronically waitlisted / at cap | Unmet demand | Add a slot, upsize the room, or add capacity |

## Rules
- **Slot-level, not daily totals.** A strong evening hides a dead mid-morning; optimize the slot.
- **Cost is on the table.** An empty class still pays the instructor and the rent — put margin-per-class against the slot before defending it.
- **Waitlist depth is a demand signal.** A consistently deep waitlist is members one bad week from leaving for a studio with room.
- **Check retention before cutting.** A low-utilization slot can be an *anchor class* a member's whole week is built around — clear a cut with `member-retention-analyst` first.

## Anti-patterns
- A schedule doc with no utilization/fill-rate view (the hook flags this).
- Defending a slot on sentiment with no margin number.
- Cutting an anchor class on a thin month's data.

Output via [`../../templates/class-schedule-and-pay-plan.md`](../../templates/class-schedule-and-pay-plan.md). Traverse the capacity tree in [`../../knowledge/fitness-studio-operations-decision-trees.md`](../../knowledge/fitness-studio-operations-decision-trees.md) first. Pair with [`../design-instructor-pay-model/SKILL.md`](../design-instructor-pay-model/SKILL.md) for the cost side.
