# Supply-Chain Planning — Decision Trees + 2026 Capability Map

> Canonical knowledge bank for `supply-chain-planning`. **Traverse the relevant Mermaid tree
> top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
> Volatile product/version facts in the capability map carry a retrieval date and a `[verify-at-use]`
> rider.

---

## Decision Tree: Forecast-method selection

```mermaid
flowchart TD
  A[Is demand history available?] -->|No history, new product| B[NPI approach: analogue product + market-sizing ramp + judgement overlay]
  A -->|Yes, history available| C{Is demand intermittent?<br/>CV > 0.5 AND demand frequency < 50%?}
  C -->|Yes, sparse / intermittent| D[Croston or TSB method<br/>Never apply SES to intermittent demand]
  C -->|No, demand is continuous| E{Is there a discernible trend?}
  E -->|Yes, upward or downward| F{Is there seasonality?}
  E -->|No trend, stable| G{Is there seasonality?}
  F -->|Yes, trend + season| H[Holt-Winters triple exponential smoothing]
  F -->|No season| I[Holt double exponential smoothing]
  G -->|Yes, seasonal| J[Holt-Winters or seasonal decomposition + SES]
  G -->|No, stable flat| K{Is causal data available?<br/>price, promotion, macro}
  K -->|Yes, causal drivers available| L[Regression or causal model<br/>measure accuracy vs. statistical baseline]
  K -->|No causal data| M[Simple exponential smoothing SES]
  D --> N[Measure MAPE and bias on holdout period]
  H --> N
  I --> N
  J --> N
  L --> N
  M --> N
  B --> O[Define review cadence as actuals accumulate]
```

**Leaf rule:** always measure MAPE **and** bias on a holdout period before releasing any forecast.
Choose the simplest method that fits the demand character — complexity is only justified by a
measurable accuracy improvement. Clean demand history (strip promotions, stockouts, one-offs) before
fitting any model.

---

## Decision Tree: Inventory-policy selection

```mermaid
flowchart TD
  A[Segment first: ABC × XYZ] --> B{What is the ABC class?}
  B -->|A — high value/volume| C{What is the XYZ class?}
  B -->|B — medium| D{What is the XYZ class?}
  B -->|C — low value/volume| E{What is the XYZ class?}
  C -->|X — stable, CV ≤ 0.5| F[Continuous review s,Q<br/>Tight safety stock, high CSL, frequent review]
  C -->|Y — variable, CV 0.5–1.0| G[Safety stock + periodic or continuous review<br/>CSL 95–98%]
  C -->|Z — erratic, CV > 1.0| H[VMI / consignment OR make-to-order<br/>Minimal speculative stock]
  D -->|X| I[Periodic review R,S<br/>Moderate safety stock]
  D -->|Y| J[Periodic review<br/>Managed safety stock, review cycle ≤ monthly]
  D -->|Z| K[Periodic review, minimal SS<br/>Consider MTO or stock-out tolerance]
  E -->|X| L[Min-max or periodic review<br/>Low safety stock, low review frequency]
  E -->|Y| M[Periodic review, low safety stock]
  E -->|Z| N[Make-to-order or accept planned stock-outs<br/>No speculative stock]
  F --> O[Calculate SS = z × σ_d × √LT]
  G --> O
  H --> P[Negotiate VMI terms with supplier OR switch to MTO]
  I --> O
  J --> O
  K --> Q[Set stock-out tolerance; define allocation priority]
  L --> O
  M --> O
  N --> P
```

**Leaf rule:** segment before you set policy. An A/X SKU (high value, stable demand) and a C/Z SKU
(low value, erratic demand) need opposite policies — the first needs tight continuous-review safety
stock, the second needs make-to-order or a deliberate stock-out tolerance. Never apply a uniform
days-of-supply target across all SKUs.

---

## Decision Tree: Make-vs-buy / supply-network positioning

```mermaid
flowchart TD
  A[Is this a core competency or differentiated capability?] -->|Yes, strategic | B[Lean toward make<br/>Protect the capability]
  A -->|No, commodity or standard| C{What is the supply-concentration risk?}
  C -->|Single-source, few alternatives| D{Is the lead time acceptable for the business?}
  C -->|Multiple qualified sources| E{Cost comparison: make vs. buy fully loaded?}
  D -->|Lead time too long| F[Dual-source or near-shore to reduce lead time risk<br/>Even if cost is higher]
  D -->|Lead time acceptable| G[Buy — but manage supply risk actively]
  E -->|Make is cheaper after overhead| H{Does internal capacity exist or can be built?}
  E -->|Buy is cheaper| I[Buy — source competitively]
  H -->|Yes, capacity available| J[Make — invest in the capability]
  H -->|No, capacity constrained| K[Buy or toll-manufacture until volume justifies investment]
  B --> L[Where to hold stock?]
  J --> L
  G --> L
  I --> L
  K --> L
  L --> M{Customer-specific or configure-to-order?}
  M -->|Yes, high customization| N[Hold as late as possible: raw / semi-finished<br/>Postponement strategy]
  M -->|No, standard finished product| O{Demand volatility high?}
  O -->|High CV, unpredictable| P[Centralize stock: risk pooling reduces total safety stock]
  O -->|Low CV, stable and predictable| Q[Decentralize: hold near demand for service-level efficiency]
```

**Leaf rule:** make vs. buy is a strategic decision — cost alone is not the answer. Supply
concentration risk, lead-time impact on responsiveness, and core-competency protection all
outweigh a narrowly cheaper buy option. The positioning of inventory (where in the network to
hold it) is separate from the make-vs-buy decision and is driven by demand volatility and
customization depth.

---

## 2026 capability map — supply-chain planning software (dated, re-verify at use)

_Retrieved 2026-06-08. Product positioning, module coverage, and pricing are volatile — re-confirm
at use. This is orientation, not a procurement recommendation. `[verify-at-use]` marks particularly
volatile facts._

| Category | Platform | Positioning (2026) | Notes |
| --- | --- | --- | --- |
| **Enterprise APS / IBP** | **SAP IBP** (Integrated Business Planning) | Market-leading for SAP-centric orgs; strong S&OP, demand sensing, inventory optimization. `[verify-at-use]` | Requires SAP HANA; expensive; strong if ERP is S/4HANA. |
| **Enterprise APS / IBP** | **Kinaxis RapidResponse** | Concurrent planning, real-time scenario analysis, strong in automotive/hi-tech. `[verify-at-use]` | Premium tier; particularly strong for volatility and supply-risk response. |
| **Enterprise APS / IBP** | **o9 Solutions** | Integrated demand, supply, and financial planning; strong IBP and scenario tooling. `[verify-at-use]` | Strong in CPG and manufacturing; growing rapidly as of 2026. |
| **Enterprise APS / IBP** | **Blue Yonder (formerly JDA)** | Demand planning, supply planning, TMS/WMS breadth. `[verify-at-use]` | Broad suite; now part of Panasonic Holdings. |
| **Mid-market / cloud** | **Anaplan** | Connected planning (finance + supply); strong for multi-stakeholder S&OP. `[verify-at-use]` | Often used for the financial layer of IBP alongside a dedicated APS. |
| **Mid-market / cloud** | **Streamline / Netstock / Intuiflow** | SMB and mid-market demand + inventory planning. `[verify-at-use]` | Lower total cost; good for companies outgrowing spreadsheets. |
| **Spreadsheets + Python** | Excel / Google Sheets + Python (pandas, statsmodels) | Common baseline; appropriate for < 1,000 SKUs or when a dedicated APS isn't justified. | No real-time integration; manual data wrangling; scalability ceiling is real. |

> Provenance: analyst commentary (Gartner Supply Chain Planning Magic Quadrant, IDC) + vendor
> websites, retrieved 2026-06-08. Market-share figures, module-level capabilities, and pricing are
> volatile — re-verify at use. No invented products.

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — team constitution & seams.
- [`../best-practices/README.md`](../best-practices/README.md) — the named, citable rules.
- [`../scripts/supply_calc.py`](../scripts/supply_calc.py) — EOQ, safety stock, ROP, fill rate,
  MAPE/bias calculator.
- Neighbour decision trees: `procurement-sourcing`, `freight-forwarding-sales`, `fleet-logistics`,
  `applied-statistics`, `data-platform`.

_Last reviewed: 2026-06-08 by `claude`._
