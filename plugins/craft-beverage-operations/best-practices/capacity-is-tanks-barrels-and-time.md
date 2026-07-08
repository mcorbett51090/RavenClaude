# Capacity is tanks, barrels, and time

**Status:** Pattern
**Domain:** Production / capacity
**Applies to:** `craft-beverage-operations`

> Operations rule. No PII. Yield/turn benchmarks are `[verify-at-use]`.

---

## Why this exists

Producers reflexively read capacity as floor space and buy vessels to grow. But in craft beverage the binding constraint is often **time** — fermentation and aging lock working capital and vessel space for months or years. A vessel decision is a cash decision, and adding vessels to an aging product ties up capital in stock that won't sell for a long time.

## How to apply

- Read capacity as tanks/barrels × **turns per year** × aging time, against the demand plan.
- Confirm current vessels are fully turned before adding.
- Recognize that in aging products, more vessels = more working capital in aging stock — check the demand plan supports the tie-up.
- Model the payback on **absorbable** demand, not on a round production number.

**Do:** read turns and aging time; treat a vessel buy as a cash decision.
**Don't:** add vessels because the floor looks full; ignore the working-capital tie-up of aging.

## Edge cases / when the rule does NOT apply

For a fast-turning product (some beers, RTD formats) with genuine turned-away demand, space/throughput can be the real constraint — then adding capacity on absorbable demand is warranted.

## See also

- [`../skills/production-planning-and-cogs/SKILL.md`](../skills/production-planning-and-cogs/SKILL.md)
- Decision tree: [`../knowledge/craft-beverage-decision-trees.md`](../knowledge/craft-beverage-decision-trees.md) (add production capacity)

## Provenance

Codifies the `craft-beverage-operations-lead` house opinions and the add-capacity decision tree. Benchmarks: [`../knowledge/craft-beverage-reference-2026.md`](../knowledge/craft-beverage-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-04 by `claude`_
