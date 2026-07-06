# Price the menu on time and demand

**Status:** Pattern
**Domain:** Pricing / utilization
**Applies to:** `salon-spa-operations`

> Operations rule. Local price data is `[verify-at-use]`. No client PII.

---

## Why this exists

The service menu is priced on two things the shop down the street can't see: **contribution per chair-hour** and **demand across the week**. Copying a competitor's price ignores your cost structure and your demand pattern. Chair-hours are perishable — an empty Tuesday morning is spoiled inventory — so pricing is also a utilization lever: demand-based pricing fills the off-peak and protects the peak.

## How to apply

- Rank every service by **contribution per chair-hour** (price minus product/back-bar and time cost), not by popularity or headcount.
- Reprice the low-contribution service up, or attach a margin add-on — unless it is a deliberate traffic driver, in which case measure the retail/rebook it drives downstream.
- Use **demand-based pricing** to fill the empty daypart and protect the peak slots.
- Revisit prices on any product-cost change; hold steady where contribution and demand are healthy.

**Do:** price on contribution per chair-hour and demand; fill the off-peak.
**Don't:** price by matching the competitor; leave a low-margin service unexamined.

## Edge cases / when the rule does NOT apply

A deliberate loss-leader (an intro service that reliably converts to a high-value rebook + retail) can stay under-priced as long as the downstream value is measured — not assumed.

## See also

- [`../skills/chair-and-room-utilization/SKILL.md`](../skills/chair-and-room-utilization/SKILL.md), [`../skills/retail-attach-and-service-mix/SKILL.md`](../skills/retail-attach-and-service-mix/SKILL.md)
- Decision tree: [`../knowledge/salon-spa-decision-trees.md`](../knowledge/salon-spa-decision-trees.md) (price the service menu)
- Template: [`../templates/service-menu-and-pricing.md`](../templates/service-menu-and-pricing.md)

## Provenance

Codifies the `salon-spa-operations-lead` house opinion and the menu-pricing decision tree. Benchmarks: [`../knowledge/salon-spa-reference-2026.md`](../knowledge/salon-spa-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
