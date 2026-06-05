# Basis Is the Local Price Gap That the Grower Controls

**Status:** Pattern
**Domain:** Grain marketing / price risk
**Applies to:** `precision-agriculture`

---

## Why this exists

Commodity price risk is frequently discussed as if it is entirely the CBOT or CME futures price — the number on the ticker. The price a grower actually receives is futures minus basis (local cash price = futures + basis, where basis is typically negative for most grain locations). Basis is determined by local supply/demand, transportation costs, and elevator margins — and it varies significantly by location, season, and year. A grower who is skilled at managing futures price but ignores basis frequently leaves $0.20–$0.50/bu on the table [unverified — training knowledge] relative to a grower who tracks and selects the right basis window. Basis management is the margin lever closest to the grower's control because it is entirely local.

## How to apply

Build basis tracking into the marketing plan:

```
Basis management framework:
  Track:
    Daily cash bid (local elevator / ADM / Bunge / other): $______/bu
    Nearby CBOT futures price:                            $______/bu
    Basis (cash − futures):                               $______/bu (negative = under futures)

  Historical basis analysis (same elevator, same delivery window):
    Prior 3-year average basis for this delivery month: $______/bu
    Weakest basis in the period (worst-case):           $______/bu
    Strongest basis in the period (best-case):          $______/bu

  Decision rule:
    If current basis is stronger than 3-year average → sell basis now / store for futures later
    If current basis is weaker than 3-year average → hold basis / price futures first, basis later

  Basis contract tools:
    HTA (Hedge-to-Arrive): locks futures, floats basis — use when futures are strong, basis is weak
    Basis contract: locks basis, floats futures — use when basis is strong, futures are uncertain
    Cash sale: locks both — use when both are favorable simultaneously
```

**Do:**
- Track basis for each elevator used, not just one — basis varies by buyer within the same county.
- Build a 3-year historical basis chart for each delivery month before making any marketing decision; basis patterns are seasonal and repeatable.
- Align basis management with storage and cash-flow planning — storing for basis improvement has a carry cost that must be netted.

**Don't:**
- Market grain on futures price alone without accounting for basis — the all-in price is what matters.
- Assume that a better futures price always means a better net price; a weak basis can more than offset a futures rally.

## Edge cases / when the rule does NOT apply

Contract-priced production (seed contracts, specialty crops with fixed forward prices) does not have a basis variable — the contract locks both components. Organic grain markets often have different basis structures than conventional; the same tracking discipline applies but the reference benchmarks differ.

## See also

- [`../agents/ag-market-analyst.md`](../agents/ag-market-analyst.md) — owns the price, basis, and marketing-plan analysis.
- [`../agents/farm-operations-analyst.md`](../agents/farm-operations-analyst.md) — models the storage carry cost that affects basis decision timing.
- [`./weather-and-price-are-the-risk-hedge-the-controllable-plan-t.md`](./weather-and-price-are-the-risk-hedge-the-controllable-plan-t.md) — basis management is the controllable component of price risk; the parent rule frames the larger hedge-the-controllable philosophy.

## Provenance

Basis management is standard grain marketing practice; the HTA/basis-contract framing is well established in CME Group and Cooperative Extension grain-marketing education.

---

_Last reviewed: 2026-06-05 by `claude`_
