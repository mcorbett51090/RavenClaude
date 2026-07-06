# Price the membership on value and commitment

**Status:** Pattern
**Domain:** Pricing / tier architecture
**Applies to:** `fitness-studio-gym-operations`

> Advisory operations rule, not financial advice. Prices and churn/LTV benchmarks are `[verify-at-use]`. No member PII.

---

## Why this exists

A membership price is not a single number — it's a **tier architecture**, and each tier is a different churn and LTV profile. An unlimited-plus-contract member churns least and is worth most; a month-to-month member buys flexibility and churns more; a class-pack buyer has no recurring anchor and is really a win-back path. Pricing to match the competitor's sign ignores all of that. Price on the **value delivered and the commitment made**, and the LTV takes care of itself.

## How to apply

- Architect tiers by commitment: **unlimited + contract**, **month-to-month unlimited**, **class-pack/punch card** — and name the churn + LTV character of each.
- **Price the flexibility**: month-to-month should carry a premium over the committed contract, because it costs you churn.
- Check **ancillary headroom before defaulting to a dues increase** — often the better lever.
- Model each change against member LTV and expected churn (`[verify-at-use]`), not against a competitor's posted rate.

**Do:** make the committed tier the best per-visit value and price flexibility for what it costs you.
**Don't:** copy the studio down the street, or discount your way to a "full" roster of low-LTV members.

## Edge cases / when the rule does NOT apply

A launch or land-grab in a new market may run promotional pricing deliberately for a defined window — but with an exit plan back to value-based tiers, not as the permanent model.

## See also

- [`./retention-beats-acquisition-on-unit-economics.md`](./retention-beats-acquisition-on-unit-economics.md), [`./ancillary-revenue-is-the-margin.md`](./ancillary-revenue-is-the-margin.md)
- [`../skills/membership-growth-and-churn/SKILL.md`](../skills/membership-growth-and-churn/SKILL.md)

## Provenance

Codifies `fitness-studio-operations-lead` house opinion (#5) and the membership pricing/tier decision tree. Benchmarks: [`../knowledge/fitness-studio-reference-2026.md`](../knowledge/fitness-studio-reference-2026.md).

---

_Last reviewed: 2026-07-02 by `claude`_
