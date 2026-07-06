---
name: group-vs-fit-trip-operations
description: "Decide and run group vs FIT trips: FIT (individual custom) flexibility vs group-block economics (room block, deposit, cutoff date, attrition, tour-conductor benefit). Build the block before you sell against it, and manage the deposit/cutoff/attrition liabilities. Contract terms are verify-at-use per supplier."
---

# Group vs FIT Trip Operations

**FIT** (individual, custom) and **group** (a contracted block) are different economic instruments with different risk. Choose deliberately, then operate the one you chose.

## The loop

1. **Classify the trip.** Party size, price sensitivity, need for shared inclusions, and flexibility drive FIT vs group — traverse the group-vs-FIT tree in [`../../knowledge/travel-agency-decision-trees.md`](../../knowledge/travel-agency-decision-trees.md).
2. **FIT path — flexibility over leverage.** Book each element individually; each carries its own penalty schedule (see [`../itinerary-design-and-quoting/SKILL.md`](../itinerary-design-and-quoting/SKILL.md)). Best when travelers want custom pacing and there's no block economics to capture.
3. **Group path — build the block first.** Contract the room/seat block: deposit, **cutoff date** (when unsold rooms release), and **attrition** (the % you owe even if unsold). Understand the **tour-conductor (TC) / comp** benefit (e.g. one comp per N paid — `[verify-at-use]`). Build and hold the block *before* selling against it (§ best practice below).
4. **Manage the liabilities.** Track pickup vs the block, watch the cutoff, and reduce attrition exposure before the penalty date. Group payment cadence differs from FIT — deposits and name lists on a schedule.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Block pickup rate | rooms sold / rooms blocked | Low near cutoff -> attrition risk |
| Attrition exposure | unsold block × attrition penalty | The liability to manage down |
| TC / comp earned | comps earned vs threshold | A group's margin sweetener |
| Group deposit adherence | on-schedule deposits collected | Protects against traveler melt |

## Anti-patterns

- Selling a group before the block is contracted (overselling or attrition surprise).
- Ignoring the cutoff date until it passes.
- Running a group as N separate FIT bookings and losing the block benefit.

## See also

- [`../itinerary-design-and-quoting/SKILL.md`](../itinerary-design-and-quoting/SKILL.md), [`../service-recovery-and-disruption/SKILL.md`](../service-recovery-and-disruption/SKILL.md).
- Best practice: [`../../best-practices/build-the-group-block-before-you-sell-it.md`](../../best-practices/build-the-group-block-before-you-sell-it.md).
