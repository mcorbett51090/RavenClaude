---
name: freight-pricing-mechanics
description: "Veteran reference for building an accurate all-in freight quote — air chargeable weight (IATA 1:6000 volumetric vs actual), ocean CBM and weight/measure ton, the full ocean + air surcharge stack (BAF, CAF, THC, LSS, GRI, PSS, ISPS, AMS/ENS, DDC), margin methods (on-cost vs on-sell), and validity/volatility handling. Consulted by freight-rate-quoter."
---

# Freight Pricing Mechanics Skill

**Purpose:** give `freight-rate-quoter` (and any agent building a number) the exact math and the complete charge stack so a quote is all-in, correctly based, and margin-explicit. Pair the math here with the runnable `scripts/freight_calc.py`.

## When to use
- Building or auditing any ocean / air / road quote.
- Settling the **chargeable basis** before pricing.
- Assembling the surcharge stack so nothing is missed.
- Choosing and stating a margin method, and setting validity on a volatile lane.

## 1. Chargeable weight — air

Air freight is charged on the **greater** of actual gross weight and **volumetric (dimensional) weight**.

- **IATA volumetric weight (kg)** = (L × W × H in **cm**) ÷ **6000**, summed across all pieces.
- The 6000 divisor encodes the IATA ratio **1 m³ ≈ 167 kg** (1,000,000 cm³ ÷ 6000 ≈ 166.67).
- **Chargeable weight = max(actual gross, volumetric).** Then apply the per-kg rate at the right break.
- **Divisor caveats:** some carriers and most **express couriers** use **5000** (≈ 200 kg/m³), which charges bulky cargo more. Always confirm the divisor for the carrier — it materially changes the number. `freight_calc.py air --divisor 5000` handles it.
- **Rate breaks:** air tariffs step down at weight breaks (often N, +45, +100, +300, +500, +1000 kg). Always check whether "weighting up" to the next break (paying for more kg at the lower rate) is cheaper — a classic quoting optimization.

## 2. Chargeable basis — ocean

- **FCL (Full Container Load):** priced **per container** by type — 20'GP, 40'GP, **40'HC** (high-cube), 45'HC, reefer, open-top, flat-rack. The box is the unit; weight matters only for overweight/axle and some inland rules.
- **LCL (Less than Container Load):** priced **per weight/measure (W/M) revenue ton**, where **1 W/M = the greater of 1,000 kg (1 metric tonne) or 1 CBM**.
  - **CBM** = L × W × H in **metres** (1 CBM = 1 m³). For a carton in cm: (L×W×H) ÷ 1,000,000.
  - So LCL chargeable units = max(total CBM, total weight in tonnes). `freight_calc.py ocean` computes both and returns the billing basis.
  - LCL also carries minimums (often a 1 W/M floor) and origin/destination handling (CFS) charges.
- **TEU/FEU** are capacity units (20'/40'-equivalent), used for vessel/space planning and some surcharges — not the customer billing unit for FCL (that's per box).

## 3. The surcharge stack (name them all)

A base ocean/air rate is **not** a quote. Build the all-in by stacking the applicable charges. Common ocean lines:

| Code | Name | What it covers |
|---|---|---|
| **BAF** | Bunker Adjustment Factor | Fuel-price volatility. Sometimes folded into an all-in rate. |
| **LSS** | Low-Sulphur Surcharge | IMO low-sulphur fuel compliance (can overlap/replace part of BAF). |
| **CAF** | Currency Adjustment Factor | FX volatility, usually a % of base (commonly ~2–8%). |
| **THC** | Terminal Handling Charge | Port/terminal handling — **origin THC (OTHC)** and **destination THC (DTHC)** are separate. |
| **GRI** | General Rate Increase | Carrier-announced base-rate increase, effective a set date. |
| **PSS** | Peak Season Surcharge | Demand peaks (e.g., pre-holiday, pre-CNY). |
| **ISPS** | Security (ISPS Code) | Port-security charge. |
| **AMS / ENS / ICS2 / ISF** | Advance manifest filings | US AMS + ISF(10+2), EU ENS / ICS2 — pre-arrival data filings. |
| **DDC** | Destination Delivery Charge | (Mainly US) destination handling. |
| **Doc / Telex / Seaway** | Documentation | B/L issuance, telex release, amendments. |
| **Customs / clearance** | Brokerage | Export and/or import clearance if in scope. |
| **Haulage / drayage** | Inland | Pre-/on-carriage trucking or rail. |
| **Accessorials** | Variable | Demurrage, detention, waiting time, gen-set (reefer), OOG, hazmat/DG, fumigation, VGM. |

Air adds: **fuel surcharge (FSC)** and **security surcharge (SSC)** per kg, plus screening, AWB fee, and airport handling. Which lines apply, and **who pays them**, is set by the **Incoterm** — see the `incoterms-2020` skill.

## 4. Margin — say which method

Two methods, different results — always state which:

- **Margin on cost (markup):** `sell = buy × (1 + m)`. A 12% markup on a 1,000 buy → 1,120 sell; the *gross margin* is only 120/1,120 ≈ **10.7%**.
- **Margin on sell (gross margin):** `sell = buy ÷ (1 − m)`. A 12% gross margin on a 1,000 buy → 1,000 ÷ 0.88 ≈ **1,136** sell.
- Always report **buy, sell, margin absolute, and margin %** — and the method. `freight_calc.py quote --margin 12%` defaults to on-cost markup; pass `--margin-on-sell` for gross-margin.
- **Per-shipment vs blended:** a thin margin on the freight can be backed by accessorials, customs, and value-added services — quote the components, know the blended margin.

## 5. Validity & volatility
- Every quote carries a **"valid until"** date. Ocean spot rates move fast; air follows capacity.
- On volatile lanes, mark **GRI / PSS / BAF as subject-to-change**, or quote a shorter validity, or use a floating-surcharge clause that passes through the published change.
- **All-in vs subject-to:** an "all-in" rate (base + BAF + CAF + LSS folded) gives the customer certainty but transfers volatility risk to you — price that risk in or keep validity short.

## Recommended resources (read on demand)
- `resources/surcharge-glossary.md` — every code expanded with who-typically-pays and overlap notes.
- `resources/worked-examples.md` — three fully worked quotes (FCL, LCL, air) end-to-end with `freight_calc.py` commands.

## Hand-offs
- Who pays which surcharge under the deal's Incoterm → `incoterms-2020` skill / `trade-lane-compliance-advisor`.
- Packaging multiple priced lanes into a bid → `rfq-tender-response` skill / `rfq-tender-strategist`.
