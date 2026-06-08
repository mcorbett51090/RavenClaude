# Truck stock is inventory with a service level

**Status:** Pattern
**Domain:** Parts and inventory management
**Applies to:** `field-service-management`

---

## Why this exists

Truck stock is routinely managed as a cost-minimization problem: "what's the cheapest set of
parts we can put on a truck?" This framing produces inventory decisions that optimize for carrying
cost while ignoring the service-level cost of a stockout — the return visit, the SLA penalty, the
customer dissatisfaction, and the follow-on contract renewal risk.

The correct framing is: truck stock is a mobile warehouse with a service-level target. The
question is not "what's the cheapest stock?" but "what fill rate does our first-time-fix target
require, and what is the minimum inventory that delivers it?" Parts decisions are inventory
decisions — they have a carrying cost and a stockout cost, and optimizing for only one produces
the wrong answer.

## How to apply

- **State the fill-rate target before any add or remove decision.** "We need a 95% fill rate on
  universal-carry parts to support our premium SLA tier" is the constraint. Every inventory
  decision is evaluated against it.
- **Model both sides of the tradeoff.** For every part being considered for removal: calculate
  the monthly carrying cost saved and the first-time-fix fill-rate impact. Only remove if the
  fill-rate impact is within tolerance.
- **Use the payback framework for add decisions.** For a part causing first-time-fix misses:
  payback period = (monthly miss cost) ÷ (monthly carrying cost). Parts with payback < 3 months
  are strong universal-carry candidates.

**Do:**

- Set an explicit fill-rate target by SLA tier (e.g., 95% for premium, 90% for standard).
- Calculate `truck_stock_fill_rate()` from actual usage and stockout data before redesigning
  truck stock.
- Tier the parts list: universal-carry, tech-specialty, and special-order. Apply different
  reorder logic to each tier.

**Don't:**

- Remove parts from truck stock solely to reduce carrying cost without modeling fill-rate impact.
- Add parts to truck stock without checking usage frequency and payback period.
- Set reorder points by feel rather than usage rate, lead time, and desired fill rate.
- Treat all trucks identically if technicians serve different equipment types or SLA tiers.

## Edge cases / when the rule does NOT apply

For very low-frequency, high-cost parts (e.g., a major compressor on a chiller), the carrying
cost makes universal-carry impractical even for premium SLA — the right answer is a reliable
same-day supplier and a pre-dispatch pull process, not stock on the truck. The fill-rate
target is still the constraint; the mechanism changes from truck stock to pre-pull logistics.

## See also

- [`./first-time-fix-is-the-master-metric.md`](./first-time-fix-is-the-master-metric.md)
- [`../knowledge/fsm-decision-trees.md`](../knowledge/fsm-decision-trees.md) (stock-the-part-or-not tree)
- [`../skills/truck-stock-and-parts/SKILL.md`](../skills/truck-stock-and-parts/SKILL.md)
- [`../scripts/fsm_calc.py`](../scripts/fsm_calc.py) — `truck_stock_fill_rate()`

## Provenance

Applies inventory management theory (EOQ, reorder-point, service-level optimization) to the
field-service context. The framing of truck stock as a mobile warehouse with a service-level
target is standard in field-service management literature and is operationalized by platforms
like ServiceTitan and IFS in their parts-management modules. `[verify-at-use]`

---

_Last reviewed: 2026-06-08 by `claude`._
