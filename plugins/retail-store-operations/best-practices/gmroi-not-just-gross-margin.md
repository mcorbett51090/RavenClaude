# GMROI, not just gross margin

**Status:** Absolute rule
**Domain:** Category management, assortment planning, inventory investment
**Applies to:** `retail-store-operations`

---

## Why this exists

Gross margin percentage tells you what fraction of revenue is kept after the cost of goods.
It does not tell you how much capital is tied up in inventory earning that margin. A category
with an 80% gross margin that turns once a year returns 80 cents on the dollar of inventory
cost — a mediocre return. A category with a 40% gross margin that turns six times a year returns
$2.40 on the dollar — an excellent return. Using gross margin % alone systematically over-invests
in high-margin / slow-turning categories and under-invests in low-margin / fast-turning ones.

GMROI (Gross Margin Return on Inventory Investment) corrects this:

```
GMROI = Gross Margin $ ÷ Average Inventory at Cost
```

A GMROI below 1.0 means the category returns less in margin than the cost of the inventory
tied up — it is destroying capital regardless of its gross margin %.

## How to apply

**Do:**

- Calculate GMROI for every category you are evaluating for space reallocation or buying investment.
- Use average inventory **at cost** in the denominator — using retail value overstates the return.
- Classify categories: < 1.0 (capital-destroying), 1.0–2.0 (marginal), 2.0–3.5 (healthy),
  > 3.5 (star). Treat < 1.0 as a red flag requiring a plan: reduce inventory, accelerate turns,
  or exit.
- Use `scripts/retail_calc.py` `gmroi` mode to confirm arithmetic before presenting.

**Don't:**

- Recommend category expansion based on gross margin % alone.
- Accept "it has great margins" as a sufficient rationale for increased inventory investment.
- Report GMROI without the time period it covers — a seasonal snapshot differs from an annual one.

## Edge cases / when the rule does NOT apply

- **Traffic-driver / destination categories:** a category that drives store traffic can be
  justified at below-target GMROI if its traffic contribution is quantifiable and exceeds the
  GMROI shortfall. State the traffic assumption explicitly.
- **New SKU test periods:** a new SKU in its first 8–12 weeks may show low GMROI due to initial
  inventory build-up. Flag the test period and set a re-evaluation gate.

## See also

- [`./sell-through-tells-you-reorder-or-mark-down.md`](./sell-through-tells-you-reorder-or-mark-down.md)
- [`../knowledge/retail-store-operations-decision-trees.md`](../knowledge/retail-store-operations-decision-trees.md)
- [`../scripts/retail_calc.py`](../scripts/retail_calc.py)

## Provenance

Standard retail merchandising practice. GMROI as the primary inventory productivity metric is
codified in NRF (National Retail Federation) merchandising curriculum and is the standard
performance metric in open-to-buy planning across specialty, department store, and grocery formats.

---

_Last reviewed: 2026-06-08 by `claude`._
