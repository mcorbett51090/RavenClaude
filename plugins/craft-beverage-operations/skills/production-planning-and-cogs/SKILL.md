---
name: production-planning-and-cogs
description: "Cost a craft-beverage unit and plan production against real capacity: decompose COGS per unit (raw material, yield loss, packaging, overhead absorption), read tank/barrel/time capacity and turns, and plan batches against the demand-by-channel plan. You can't price what you can't cost."
---

# Production Planning & COGS

COGS per unit is the number that hides in a craft-beverage business — in yield loss, in packaging that's larger than owners expect, and in overhead absorbed across too few units. This skill nails the true unit cost and plans production against the capacity that actually constrains it: tanks, barrels, and time.

## The loop

1. **Decompose COGS per unit.** Raw material (juice/grain/spirit), **yield loss** (a real cost, not an afterthought), packaging (glass/can/keg, label, closure, case), and overhead absorption. Compute per finished unit — you can't price or choose a channel without it. Ranges are `[verify-at-use]`.
2. **Read capacity as tanks, barrels, and time.** Fermentation and aging lock working capital and vessel space; the constraint is often time, not floor space. Read turns per vessel per year against the demand plan.
3. **Plan batches to the demand-by-channel plan.** DTC and wholesale demand pull different volumes at different margins; plan production and allocation to them, not to a round number.
4. **Watch packaging as a cost and a channel gate.** Format decides both COGS and which channels you can serve (kegs for on-premise, cans for retail, bottles for club).
5. **Feed the channel-mix decision.** Hand the true unit cost to the channel-mix analysis; DTC vs wholesale margin is meaningless without it.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| COGS per finished unit | material + yield loss + packaging + overhead | The number that hides; `[verify-at-use]` on ranges |
| Yield / loss rate | finished units / theoretical | A direct cost lever |
| Packaging cost per unit | glass/can/keg + label + closure + case | Often larger than expected |
| Vessel turns per year | batches per tank/barrel / year | The capacity denominator |
| Aging/fermentation time | days to finished | Locks working capital |

## Anti-patterns

- Pricing or choosing a channel before COGS per unit is known.
- Treating yield loss as an afterthought rather than a cost line.
- Reading capacity as floor space when the real constraint is time.
- Planning to a round production number instead of the demand-by-channel plan.

## See also

- [`../three-tier-and-self-distribution-economics/SKILL.md`](../three-tier-and-self-distribution-economics/SKILL.md) — channel margin needs the unit cost.
- Best practices: [`../../best-practices/cogs-per-unit-is-the-number-that-hides.md`](../../best-practices/cogs-per-unit-is-the-number-that-hides.md), [`../../best-practices/capacity-is-tanks-barrels-and-time.md`](../../best-practices/capacity-is-tanks-barrels-and-time.md).
- Command: [`/model-channel-mix`](../../commands/model-channel-mix.md).
