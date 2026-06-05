# Free-shipping threshold should be set above current average order value

**Status:** Pattern
**Domain:** DTC merchandising and AOV
**Applies to:** `ecommerce-dtc`

---

## Why this exists

Free shipping is one of the most powerful AOV levers in DTC because customers actively add items to qualify for it. But the threshold placement determines whether it moves behavior or just subsidizes existing orders. Setting the threshold at or below current AOV means the brand is paying for shipping on orders that would have converted anyway — it becomes a margin cost with no revenue upside. Setting the threshold 15–25% above current AOV puts the qualifying bar in the "within reach" range where customers add an item to qualify, raising the average transaction value and covering the shipping subsidy with the incremental margin.

## How to apply

Calculate the free-shipping threshold as a function of current AOV, then measure threshold-qualification rate and attach rate after implementation.

```
Threshold-setting formula:
  Current AOV: $48
  Target threshold: AOV × 1.20 to 1.25 = $58–$60

  Check: what is the modal "add one item" increment?
  If common add-on item = $12–$18, threshold of $58 puts the typical buyer $10–$22 away
  — close enough to trigger an add, not so far it reads as unattainable.

Post-implementation metrics to track:
  Threshold attach rate: % of orders that hit the threshold (target: 30–50% of eligible sessions)
  AOV uplift: new AOV vs. pre-threshold baseline
  Shipping subsidy cost: total free-shipping orders × avg shipping cost
  Net margin impact: AOV uplift × gross margin % — shipping subsidy per order
```

**Do:**
- Set the threshold at 20–25% above current AOV as the starting point.
- Display the "X more to free shipping" progress indicator in the cart on every device.
- Review and recalibrate the threshold every 6 months as AOV evolves.

**Don't:**
- Set the threshold below current AOV — this subsidizes existing behavior.
- Set the threshold so high (e.g., 2× AOV) that it reads as unattainable and fails to drive add-ons.
- Use a flat threshold across all channels and geographies without checking per-channel AOV distribution.

## Edge cases / when the rule does NOT apply

Subscription-first products where the first order is highly incentivized (deep discount, trial pack) often have a first-order AOV far below the steady-state AOV; apply the threshold to the subscription or refill order, not the acquisition order. Luxury price-point brands where free shipping is a baseline customer expectation in the category (e.g., fine jewelry) may not gain attach-rate lift from threshold framing — treat it as a CPA component instead.

## See also

- [`../agents/merchandising-specialist.md`](../agents/merchandising-specialist.md) — owns AOV strategy and cart-page mechanics.
- [`./aov-and-frequency-are-levers-you-design-not-constants.md`](./aov-and-frequency-are-levers-you-design-not-constants.md) — the parent rule on treating AOV as a designed outcome.

## Provenance

Codifies a standard DTC AOV-optimization principle. The free-shipping threshold set at or below AOV is the dominant misconfiguration seen in operator-submitted store audits; the 20–25% above-AOV heuristic is the industry-conventional starting point for "within reach" threshold design.

---

_Last reviewed: 2026-06-05 by `claude`_
