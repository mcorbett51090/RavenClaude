# Use the carrier-specific volumetric divisor for air — not only the IATA default

**Status:** Absolute rule
**Domain:** Air freight quoting / chargeable weight
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

The IATA standard volumetric divisor for air freight is 1:6000 (one chargeable kilogram per 6,000 cm³). But carriers, integrators, and forwarder tariffs routinely apply different divisors — 1:5000 is common for general cargo via many NVOCC / consolidation products, and express integrators use 1:5000 (DHL Express, FedEx, UPS) with their own product-specific rules. Quoting the wrong divisor understates or overstates chargeable weight by up to 20%, which on a large shipment is a significant pricing error. When the error favours the carrier (the forwarder used 6000 but the carrier bills at 5000), the forwarder absorbs the margin gap from their own pocket.

## How to apply

Before calculating chargeable weight on any air quote:

1. **Identify the carrier / product** being used for the shipment.
2. **Confirm the applicable divisor** from the carrier's published tariff or the GSSA/agent's rate confirmation.
3. **Apply the confirmed divisor**, not the IATA default.

**Divisor reference (common — always verify against current carrier tariff):**

| Carrier / channel | Common divisor | Notes |
|---|---|---|
| IATA general air cargo standard | 6,000 cm³/kg | The published IATA standard |
| DHL Express | 5,000 cm³/kg | Express product |
| FedEx International Priority | 5,000 cm³/kg | Express product |
| UPS Worldwide Express | 5,000 cm³/kg | Express product |
| Forwarder LCL air consolidation | 5,000 or 6,000 — confirm | Depends on the consolidator's tariff |
| Charter / project air | Confirm per-quote | Often 1:1 gross weight only |

> These are indicative. **Always confirm from the carrier's current rate confirmation or tariff.** Divisors can change.

**Chargeable weight formula (reminder):**

```
Volumetric weight (kg) = (Length cm × Width cm × Height cm) ÷ Divisor
Chargeable weight = MAX(Gross weight kg, Volumetric weight kg)
```

**Worked example — divisor impact:**

| Shipment | Gross weight | L×W×H (cm) | Vol. weight @ 6000 | Vol. weight @ 5000 | Chargeable @ 6000 | Chargeable @ 5000 |
|---|---|---|---|---|---|---|
| Large, light carton | 50 kg | 120×100×80 | 160 kg | 192 kg | **160 kg** | **192 kg** |

A 32 kg difference on one carton. On a 20-carton shipment that is 640 kg — at USD 3.50/kg that is USD 2,240 underquoted if the wrong divisor is used.

**Do:**
- Confirm the divisor from the carrier rate confirmation, not from memory.
- Document the divisor used in the quote alongside the chargeable weight calculation: `"Volumetric weight calculated at 1:5000 per [CARRIER] tariff dated [DATE]."`
- Use `scripts/freight_calc.py air --divisor 5000` (or `--divisor 6000`) to parameterise the calculation; do not hard-code the default.

**Don't:**
- Default to 6000 for all air quotes without checking whether the carrier bills at 5000.
- Assume the divisor is the same across an integrator's product portfolio — express products often differ from their standard air products.
- Round the chargeable weight down to the customer's benefit without flagging that the carrier will bill the rounded-up figure; the customer should see the carrier billing basis.

## Edge cases / when the rule does NOT apply

For internal budget estimates where exact carrier is not yet selected, the IATA 1:6000 default is an acceptable starting assumption — mark it `[budget estimate — confirm divisor when carrier selected]`. For road freight, the dimensional weight rule does not apply; road is billed on gross weight or ldm (loading metres) depending on carrier.

## See also
- [`../agents/freight-rate-quoter.md`](../agents/freight-rate-quoter.md) — all-in air quote methodology
- [`../skills/freight-pricing-mechanics/SKILL.md`](../skills/freight-pricing-mechanics/SKILL.md) — chargeable weight worked examples (air and ocean)

## Provenance

Codifies `freight-rate-quoter`'s chargeable-weight discipline and anti-pattern check (§4: "Pricing before the chargeable basis is settled"). IATA Resolution 017f governs the 6000 default; carrier-specific deviations are documented in each airline's conditions of carriage.

---

_Last reviewed: 2026-06-05 by `claude`_
