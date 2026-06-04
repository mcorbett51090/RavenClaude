# Worked quote examples (FCL, LCL, air)

> On-demand resource for the `freight-pricing-mechanics` skill. **Every number below is illustrative** — replace with your live buy rates and tariff. The point is the *structure* and the `freight_calc.py` workflow, not the figures.

## A. Ocean FCL — 1 × 40HC, Shanghai → Rotterdam, FCA Shanghai

The box is the unit. Buy rate from carrier is all-in-ish; you add origin handling + your margin.

| Charge | Basis | Amount (USD) |
|---|---|---|
| Ocean base freight (incl. BAF/LSS) | per 40HC | 1,800 |
| Origin THC | per 40HC | 210 |
| Documentation | per B/L | 45 |
| ENS filing | per B/L | 30 |
| **Buy subtotal** | | **2,085** |

Apply 12% markup (on-cost):
```
python3 scripts/freight_calc.py quote --base 1800 \
  --surcharge OTHC=210 --surcharge DOC=45 --surcharge ENS=30 --margin 12%
```
→ Sell ≈ **2,335**, margin **250 (≈10.7% on sell)**. Validity: 14 days. Excludes: destination THC + import (buyer's under FCA), duty/VAT, insurance.

## B. Ocean LCL — 8 cartons, Ningbo → Felixstowe

Settle the basis first. Cartons: 8 × (120 × 100 × 110 cm), total gross 800 kg.
```
python3 scripts/freight_calc.py ocean --pieces 8 --dims 120x100x110 --weight 800
```
- Volume per carton = 1.20 × 1.00 × 1.10 = 1.32 CBM → 8 × 1.32 = **10.56 CBM**.
- Weight = 800 kg = **0.80 tonnes**.
- W/M = max(10.56, 0.80) = **10.56 revenue tons** → it's a **volume** shipment; price per CBM.

Then quote per-W/M rate × 10.56 + CFS handling + doc, apply margin. (LCL minimum 1 W/M floor applies if tiny.)

## C. Air — 4 pieces, Frankfurt → Chicago, chargeable weight

4 pieces × (120 × 80 × 100 cm), actual gross 350 kg.
```
python3 scripts/freight_calc.py air --pieces 4 --dims 120x80x100 --weight 350
```
- Volumetric per piece = (120×80×100)/6000 = 160 kg → 4 × 160 = **640 kg** volumetric.
- Actual = 350 kg. **Chargeable = max(640, 350) = 640 kg** — it's a **volume** (low-density) shipment.
- Price 640 kg at the rate for the +500 break, add FSC + SSC (per kg) + AWB + screening, apply margin.
- **Check the break:** if the +500 and +1000 breaks differ, confirm 640 kg at +500 beats weighting up to 1000 kg at +1000.

**Lesson across all three:** the basis (per-box / per-W-M / per-chargeable-kg) is decided *before* the rate, and the surcharge stack + validity + Incoterm scope make it a real quote.
