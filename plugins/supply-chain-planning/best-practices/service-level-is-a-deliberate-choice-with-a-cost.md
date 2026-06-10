# Service level is a deliberate choice with a cost

**Status:** Pattern
**Domain:** Inventory policy / service-level setting
**Applies to:** `supply-chain-planning`

---

## Why this exists

"As high as possible" is not a service-level target. Neither is "100%". Every increment of service
level above a reasonable baseline costs real inventory-carrying capital, and the marginal cost
increases steeply as you approach 100%. A supply-chain team that sets service-level targets
without showing the working-capital cost of each increment is making an invisible choice — and
usually an irrational one.

The math is non-linear: moving from 95% to 99% cycle service level roughly doubles the z-score
(1.65 → 2.33) and therefore doubles the safety stock for the same demand variability and lead time.
Moving from 99% to 99.9% adds another 50% on top of that. At very high service levels, the
carrying cost per unit of service-level increment can exceed the gross margin per unit sold.

The right service level is the intersection of:
- The customer contract or SLA (what was promised).
- The margin of the product (is this item worth 99.9% coverage?).
- The carrying cost of the inventory required (what does it cost to achieve that level?).
- The obsolescence and spoilage risk (for short shelf-life or fast-obsolescence items).

## How to apply

1. Identify the service-level metric: **Cycle Service Level (CSL)** — probability of no stockout
   per replenishment cycle — vs. **Fill Rate (FR / Type-2 service level)** — fraction of demand
   met from stock. For most operational purposes, fill rate is more intuitive and customer-facing.
2. Map the chosen level to a z-score (normal distribution).
3. Calculate the safety-stock investment at the proposed level and at ±2% — show the table to
   the decision-maker.
4. Document who approved the service-level target and what contract or margin justified it.
5. Review annually or when the product margin, cost, or customer contract changes.

**z-score / safety-stock sensitivity (orientation):**

| Fill rate target | z (approx.) | SS relative to 90% baseline |
| --- | --- | --- |
| 90% | 1.28 | 1× |
| 95% | 1.65 | 1.3× |
| 97% | 1.88 | 1.5× |
| 99% | 2.33 | 1.8× |
| 99.5% | 2.58 | 2.0× |

> Note: the ratios above assume demand and lead time are the same across service levels; they are
> illustrative. Run `scripts/supply_calc.py` with your actual inputs.

**Do:**

- Present the working-capital tradeoff table to the approver — not just the service-level target
  in isolation.
- Set differentiated targets by ABC class: A/X items can justify 97–99%; C/Z items may warrant
  95% or below (or MTO).
- Document the approval: "95% fill rate approved by VP Operations, 2026-06-01, basis: customer
  contract section 4.2."
- Review the targets when demand volatility, unit costs, or customer contracts change.

**Don't:**

- Default to "99%" because it sounds good.
- Apply the same fill-rate target to a $5 commodity and a $500 slow-moving spare part.
- Set a service-level target without quantifying the safety-stock investment it requires.
- Treat the service-level target as permanent — it is a business decision, not a physical constant.

## Edge cases / when the rule does NOT apply

For life-safety or regulatory-mandated items (medical devices, certain spare parts in critical
infrastructure), the service-level target may be set by regulation or contract at near-100%
regardless of cost. Even in this case, document the requirement source, calculate the cost, and
confirm it is funded.

## See also

- [`./safety-stock-covers-variability-not-the-average.md`](./safety-stock-covers-variability-not-the-average.md) — the formula that converts service level to safety stock.
- [`./segment-abc-xyz-before-you-set-policy.md`](./segment-abc-xyz-before-you-set-policy.md) — differentiated targets per segment.
- [`../templates/safety-stock-model.md`](../templates/safety-stock-model.md) — working-capital tradeoff table.
- [`../scripts/supply_calc.py`](../scripts/supply_calc.py) — `safety_stock()` function.

## Provenance

APICS/ASCM CPIM body of knowledge; Silver, Pyke & Thomas _Inventory and Production Management
in Supply Chains_ (4th ed.); Simchi-Levi, Kaminsky & Simchi-Levi _Designing and Managing the
Supply Chain_ (3rd ed.). The non-linear cost-of-service-level relationship is standard in
inventory theory.

---

_Last reviewed: 2026-06-08 by `claude`._
