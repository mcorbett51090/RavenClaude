---
description: "Set a defensible inventory policy: segment SKUs with ABC/XYZ, select the replenishment method per segment, calculate safety stock from the service level and variability inputs, calculate reorder point and EOQ, and quantify the working-capital tradeoff."
---

# Inventory Policy and Safety Stock

**Purpose:** produce a calibrated, segmented inventory policy with safety-stock levels that are
grounded in service-level targets and measured demand and lead-time variability — not rules-of-thumb.

---

## Steps

### 1. Segment the portfolio (ABC/XYZ)

Before setting any policy, segment. A single policy for all SKUs destroys value.

**ABC by revenue/volume share (Pareto):**

| Class | Cumulative share | Typical SKU count |
|---|---|---|
| A | Top ~70% of revenue | ~10–20% of SKUs |
| B | Next ~20% | ~30% of SKUs |
| C | Bottom ~10% | ~50–60% of SKUs |

**XYZ by demand variability (CV = σ/μ):**

| Class | CV range | Character |
|---|---|---|
| X | CV ≤ 0.5 | Stable, predictable |
| Y | 0.5 < CV ≤ 1.0 | Variable but forecastable |
| Z | CV > 1.0 | Highly variable or intermittent |

**9-cell policy matrix (example defaults — review per business context):**

| | X (stable) | Y (variable) | Z (erratic) |
|---|---|---|---|
| **A (high value)** | Continuous review, tight SS, high CSL | Safety stock + frequent review | VMI or consignment; MTO if feasible |
| **B (medium)** | Periodic review, moderate SS | Periodic review, managed SS | Periodic review, minimal SS |
| **C (low value)** | Min-max, low SS | Periodic review, low SS | MTO or stock-out tolerance |

### 2. Traverse the inventory-policy selection tree

Before choosing a replenishment mechanism, traverse `## Decision Tree: Inventory-policy selection`
in [`../../knowledge/supply-chain-planning-decision-trees.md`](../../knowledge/supply-chain-planning-decision-trees.md).

### 3. Set service-level targets

- Choose between **Cycle Service Level (CSL)** — probability of no stockout per cycle — and
  **Fill Rate (FR / Type-2)** — fraction of demand met from stock.
- CSL maps to z-score (normal distribution): CSL 90% → z = 1.28; 95% → z = 1.65; 99% → z = 2.33.
- Document: who set the target, what customer contract or margin it is based on, and when it
  was last reviewed.

### 4. Calculate safety stock

Use [`../../scripts/supply_calc.py`](../../scripts/supply_calc.py) `safety_stock()`.

**Simple formula (demand variability only):**

```
SS = z × σ_demand × √(lead_time)
```

Where `σ_demand` = standard deviation of demand per period; `lead_time` = mean lead time in
periods.

**Combined formula (demand + lead-time variability):**

```
SS = z × √(LT × σ_d² + D̄² × σ_LT²)
```

Where `σ_LT` = standard deviation of lead time; `D̄` = mean demand per period.

Use the combined formula when `σ_LT / LT > 0.2` (lead-time variability materially contributes).

**Inputs to document:**
- z (from chosen CSL)
- σ_demand (from demand-forecasting skill — use forecast error σ, not raw demand σ)
- LT (mean lead time in periods, including supplier + transport + receiving)
- σ_LT (lead-time standard deviation — from supplier on-time-delivery history)

### 5. Calculate reorder point (ROP)

```
ROP = D̄ × LT + SS
```

For continuous-review systems (s, Q) — when on-hand inventory drops to ROP, place an order of
size Q (= EOQ or fixed lot size).

### 6. Calculate EOQ

Use [`../../scripts/supply_calc.py`](../../scripts/supply_calc.py) `eoq()`.

```
EOQ = √(2 × D × S / H)
```

Where `D` = annual demand units; `S` = ordering cost per order ($); `H` = annual holding cost per
unit ($).

Holding cost H = unit cost × holding rate (typically 20–30% annually, including capital, storage,
obsolescence, and insurance).

### 7. Quantify the working-capital tradeoff

For each service-level increment, compute the incremental safety-stock investment:

```
SS_investment = SS_units × unit_cost
Carrying_cost = SS_investment × holding_rate
```

Present as a table: CSL → SS units → SS investment ($) → annual carrying cost ($). The business
approves the tradeoff, not the supply-chain team alone.

## Anti-patterns

- A safety-stock figure with no z or σ_demand basis (a guess in days-of-supply clothing).
- A single service-level target for the full SKU portfolio.
- Safety-stock sized as average demand × days-of-supply (confuses safety stock with cycle stock).
- EOQ with holding rate assumed at 0% or pulled from a generic benchmark.
- Reorder point without adding safety stock.

## Output

An inventory policy document: ABC/XYZ segmentation, policy per cell, service-level targets (with
approval), safety-stock calculations (all inputs shown), ROP per SKU, EOQ, and the working-capital
tradeoff table. Use the `inventory-optimization-engineer` agent for the full guided workflow.
