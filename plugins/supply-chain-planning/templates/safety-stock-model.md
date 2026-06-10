# Safety-Stock Model — [SKU / Product Family / Site]

> **Instructions:** complete one tab per SKU or one row per ABC/XYZ cell as appropriate. All
> inputs must be populated before a safety-stock figure is adopted in MRP. Delete instructional
> lines before publishing.

---

## 1. Segmentation

| Field | Value |
| --- | --- |
| SKU / family | [SKU code or family name] |
| ABC class (A/B/C) | [A / B / C] — based on [revenue / volume Pareto, date: YYYY-MM] |
| XYZ class (X/Y/Z) | [X / Y / Z] — CV = [σ/μ value] |
| Policy type | [Continuous review (s,Q) / Periodic review (R,S) / MTO / VMI] |
| Review date | [YYYY-MM-DD] |
| Reviewed by | [Name / role] |

---

## 2. Service-level target

| Field | Value |
| --- | --- |
| Target metric | [Cycle Service Level (CSL) / Fill Rate (FR)] |
| Target value | [X]% |
| z-score | [e.g. 1.65 for CSL 95%] |
| Approved by | [Name / role / date] |
| Basis for target | [Customer contract / margin / internal policy] |

**z-score reference (normal distribution, one-sided):**

| CSL / FR | 90% | 92% | 95% | 97% | 98% | 99% | 99.5% |
| --- | --- | --- | --- | --- | --- | --- | --- |
| z | 1.28 | 1.41 | 1.65 | 1.88 | 2.05 | 2.33 | 2.58 |

---

## 3. Demand inputs

| Input | Value | Source | Date |
| --- | --- | --- | --- |
| Mean demand per period (D̄) | [units / period] | [data source] | [YYYY-MM] |
| Demand std dev per period (σ_d) | [units] | [forecast error σ from demand-forecasting skill] | [YYYY-MM] |
| Demand CV (σ_d / D̄) | [value] | Calculated | |
| Planning period length | [week / month] | | |

---

## 4. Lead-time inputs

| Input | Value | Source | Date |
| --- | --- | --- | --- |
| Mean lead time (LT) in periods | [periods] | [supplier + transport + receiving] | [YYYY-MM] |
| Lead-time std dev (σ_LT) | [periods] | [supplier OTIF history] | [YYYY-MM] |
| σ_LT / LT ratio | [value] | Calculated | |
| Use combined formula? (σ_LT/LT > 0.2) | [Yes / No] | | |

---

## 5. Safety-stock calculation

**Formula used:** [Simple: SS = z × σ_d × √LT] **or** [Combined: SS = z × √(LT × σ_d² + D̄² × σ_LT²)]

| Parameter | Value |
| --- | --- |
| z | |
| σ_d | |
| LT (mean, periods) | |
| σ_LT | |
| D̄ | |
| **Safety stock (SS) — units** | **[calculated]** |

> Run `scripts/supply_calc.py` `safety_stock()` with the inputs above to verify.

---

## 6. Reorder point

```
ROP = D̄ × LT + SS = [D̄] × [LT] + [SS] = [ROP units]
```

| Field | Value |
| --- | --- |
| ROP (units) | [calculated] |
| ROP (days of supply) | [ROP / D̄_daily] |

---

## 7. Order quantity (EOQ)

| Input | Value | Source |
| --- | --- | --- |
| Annual demand (D) | [units/year] | |
| Ordering cost per order (S) | [$] | [purchasing / logistics cost] |
| Unit cost (C) | [$] | [COGS / purchase price] |
| Holding rate (h) | [%/year] | [finance — typically 20–30%] |
| H = C × h (annual holding cost per unit) | [$] | Calculated |
| **EOQ = √(2DS/H)** | **[units]** | Calculated |

> Run `scripts/supply_calc.py` `eoq()` to verify.

---

## 8. Working-capital tradeoff

| CSL | z | SS (units) | SS ($) | Annual carrying cost ($) | Incremental vs. 90% CSL |
| --- | --- | --- | --- | --- | --- |
| 90% | 1.28 | | | | baseline |
| 95% | 1.65 | | | | |
| 97% | 1.88 | | | | |
| 99% | 2.33 | | | | |

**Approved service level and rationale:**  
[State who approved, what contract or margin justified the choice, and the review date.]

---

## 9. Review history

| Date | Reviewer | Change | Reason |
| --- | --- | --- | --- |
| [YYYY-MM-DD] | [Name] | [Initial set] | [Reason] |

---

_Template version: 1.0 — supply-chain-planning plugin v0.1.0. Copy into `docs/inventory/[SKU or family]-safety-stock.md`._
