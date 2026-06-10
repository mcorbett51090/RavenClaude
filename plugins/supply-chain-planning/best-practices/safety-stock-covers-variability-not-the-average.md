# Safety stock covers variability, not the average demand

**Status:** Absolute rule
**Domain:** Inventory policy and safety stock
**Applies to:** `supply-chain-planning`

---

## Why this exists

Safety stock and cycle stock serve different purposes and are sized differently:

- **Cycle stock** covers expected (average) demand during the replenishment lead time.
  `Cycle stock = D̄ × LT`. This is what you would need if demand and lead time were perfectly
  predictable.
- **Safety stock** covers the **unexpected** — demand above forecast, lead time longer than
  expected, forecast error. `SS = z × σ_demand × √(lead_time)`.

Sizing safety stock against average demand (e.g., "30 days of average sales") conflates the two.
It will over-stock if demand is stable and lead times are short; it will under-stock if demand is
volatile or lead times variable — precisely the case where the buffer is most needed.

The correct formula is grounded in the distribution of variability:

- `z` — the z-score corresponding to the chosen cycle service level (e.g., z = 1.65 for 95% CSL).
- `σ_demand` — the standard deviation of demand (from forecast error, not raw demand).
- `LT` — the mean lead time in planning periods.
- When lead-time variability is significant (`σ_LT / LT > 0.2`): use the combined formula
  `SS = z × √(LT × σ_d² + D̄² × σ_LT²)`.

## How to apply

1. Separate cycle stock from safety stock in every calculation — they serve different functions
   and are funded from different working-capital buckets.
2. Source `σ_demand` from the forecast error distribution (holdout period), not from raw demand
   standard deviation. Forecast error is what safety stock is protecting against.
3. Source `σ_LT` from supplier on-time-delivery history, not from a guess.
4. Document every input. A safety-stock number without a z, σ_demand, and LT is a guess.

**Do:**

- Use `SS = z × σ_demand × √LT` as the baseline formula.
- Use the combined formula when lead-time variability is material.
- Input forecast-error σ (not raw demand σ) as `σ_demand`.
- Document the service level, z-score, and the date the inputs were last refreshed.

**Don't:**

- Set safety stock as a fixed number of days of average demand.
- Use rule-of-thumb days-of-supply without checking whether they approximate the formula result.
- Conflate safety stock and cycle stock in MRP parameters.
- Set safety stock once and never review it as demand volatility or lead times change.

## Edge cases / when the rule does NOT apply

For highly intermittent demand (C/Z class, AX5 / sporadic category), the normal-distribution
formula may overstate safety stock. In those cases: consider make-to-order (no speculative stock),
a target min-stock of 1 unit, or a parametric approach tailored to intermittent demand (e.g.,
Poisson-based). Document the departure from the standard formula.

## See also

- [`./service-level-is-a-deliberate-choice-with-a-cost.md`](./service-level-is-a-deliberate-choice-with-a-cost.md) — z-score selection.
- [`./segment-abc-xyz-before-you-set-policy.md`](./segment-abc-xyz-before-you-set-policy.md) — segmentation before sizing.
- [`../skills/inventory-policy-and-safety-stock/SKILL.md`](../skills/inventory-policy-and-safety-stock/SKILL.md) — full calculation workflow.
- [`../scripts/supply_calc.py`](../scripts/supply_calc.py) — `safety_stock()` function.

## Provenance

APICS/ASCM CPIM and CSCP body of knowledge; Hadley & Whitin (1963); Silver, Pyke & Thomas
_Inventory and Production Management in Supply Chains_ (4th ed.). The formula is standard across
the practitioner literature.

---

_Last reviewed: 2026-06-08 by `claude`._
