# Chargeable Weight Must Be Calculated Before Quoting Air

**Status:** Absolute rule
**Domain:** Freight-forwarding sales
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

An air freight quote built on the gross weight of a shipment will be wrong whenever the cargo is bulky or low-density — which is often. The chargeable weight is the higher of actual gross weight and volumetric weight (dimensions ÷ divisor), and quoting on actual weight alone for a volumetric shipment undercharges the customer or, worse, creates a bill that doesn't match the quote. The IATA standard divisor is 6,000 cm³/kg; some carriers and couriers use 5,000. Using the wrong divisor compounds the error. The calculation takes 60 seconds; the dispute takes a week.

## How to apply

Calculate chargeable weight before building any air quote:

```
Air Chargeable Weight Calculation
─────────────────────────────────────
Shipment: ________________
Pieces: ___

For each piece:
  Dimensions (L × W × H in cm):  ___ × ___ × ___ = ___ cm³
  Volumetric weight (IATA /6000): ___ cm³ ÷ 6,000 = ___ kg
  Gross weight:                   ___ kg
  Chargeable weight this piece:   MAX(___ kg, ___ kg) = ___ kg

Total chargeable weight:          ___ kg (sum of all pieces)
Confirm divisor with airline/forwarder:  [ ] IATA /6000  [ ] /5000  [ ] Other: ___

Quote basis:  Chargeable weight ___ kg × rate $___/kg = $___
```

Use `scripts/freight_calc.py air` to automate this calculation and avoid arithmetic errors.

**Do:**
- Calculate per piece, then total — do not apply a single average dimension to a multi-piece shipment with varying sizes.
- Confirm the divisor with the airline or the carrier tariff before quoting — a courier (DHL, FedEx, UPS) frequently uses /5,000; freight forwarders and IATA airlines use /6,000.
- Show the chargeable weight basis on the quote: "Chargeable weight: 320 kg (volumetric, 6,000 divisor)."

**Don't:**
- Quote on gross weight without checking whether volumetric weight is higher.
- Use a different divisor in the quote than the one the carrier will apply — the quote and the buy rate must use the same calculation basis.
- Estimate dimensions; obtain the actual carton/pallet dimensions from the shipper before quoting, or clearly state "pending shipper dims confirmation."

## Edge cases / when the rule does NOT apply

Ocean FCL shipments do not use chargeable weight; pricing is per container. Ocean LCL uses CBM (volume in cubic meters) versus a weight/measure ton (1 W/M = 1 CBM or 1,000 kg, whichever is greater) — a different calculation, see the `freight-pricing-mechanics` skill.

## See also

- [`../agents/freight-rate-quoter.md`](../agents/freight-rate-quoter.md) — uses this calculation as the first step in every air quote.
- [`./quote-all-in-never-base-only.md`](./quote-all-in-never-base-only.md) — the chargeable weight result feeds the all-in quote build.

## Provenance

Codifies CLAUDE.md §3 #4 (qualify before you quote) and §3 anti-pattern 2 (pricing before chargeable basis is settled). IATA volumetric weight calculation method: dimensions (L×W×H in cm) ÷ 6,000 = volumetric kg; standard across IATA Resolution 502 [unverified — confirm divisor with specific carrier tariff].

---

_Last reviewed: 2026-06-05 by `claude`_
