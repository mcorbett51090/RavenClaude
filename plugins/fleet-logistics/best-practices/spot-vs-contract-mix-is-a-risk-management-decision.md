# Spot vs. Contract Mix Is a Risk Management Decision

**Status:** Pattern
**Domain:** Fleet economics / revenue management
**Applies to:** `fleet-logistics`

---

## Why this exists

Every truckload carrier allocates capacity between contract freight (committed volume, negotiated rate, predictable) and spot freight (market-rate, variable volume, higher volatility). The split is not a preference — it is a risk management decision that determines how exposed the fleet is to freight-cycle downturns. A 100% spot book maximizes rate capture in a hot market and collapses in a soft one; a 100% contract book provides stability but caps upside and can lock in below-market rates for 12 months. The "right" mix depends on the fleet's cost structure, debt service, driver pay model, and risk appetite — and it should be explicit, not accidental.

## How to apply

Build the mix analysis with explicit risk scenarios:

```
Contract / spot mix analysis:
  Fleet capacity: ______ trucks × available days = ______ truck-days/period

  Target contract allocation:      ______% of capacity
  Target spot allocation:          ______% of capacity

  Contract book:
    Average contracted rate/mile:  $______
    Committed volume (loads/week): ______
    Revenue at full commitment:    $______/period

  Spot exposure:
    Current spot rate index (DAT or similar, dated): $______/mile
    Rate range (trailing 90-day low / high):         $_____ / $_____
    Revenue at low / high spot:    $_____ / $_____

  Downside scenario (spot rate at 90-day low, 20% contract shortfall):
    Total revenue:    $______
    Total cost (CPM × miles): $______
    OR:               ______%  (>100% = loss)
```

Decision rule: if the downside scenario produces an OR > 100%, the contract allocation is too low or the cost base is too high.

**Do:**
- Reassess the mix at every contract renewal season (typically October–November for January freight) using the current freight cycle position.
- Maintain enough contract coverage to cover fixed costs (depreciation, insurance, base driver pay) in a soft spot market.
- Track DAT or Truckstop rate indices weekly during spot-heavy periods to know where the market is relative to contract rates.

**Don't:**
- Let the mix drift to 100% spot during a hot market without modeling the downside; the freight cycle always turns.
- Accept contract rates below variable CPM to fill trucks in a soft market — the truck loses money on every mile and the contract locks in the loss.

## Edge cases / when the rule does NOT apply

Dedicated contract carriers by definition run 100% contract; the risk management question shifts to contract structure (rate escalators, volume minimums, fuel indexing) rather than mix. Brokers and 3PLs have a different exposure model — their risk is spread/margin management rather than asset coverage.

## See also

- [`../agents/fleet-engagement-lead.md`](../agents/fleet-engagement-lead.md) — owns the freight-cycle read and mix recommendation.
- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — owns the downside scenario model and OR projection.
- [`./the-operating-ratio-is-the-survival-metric.md`](./the-operating-ratio-is-the-survival-metric.md) — the downside OR test is the survival check; the two rules connect directly.

## Provenance

Standard carrier yield-management and risk-management practice; contract/spot mix as a risk lever is a core topic in carrier strategy consulting and is covered in ATA and DAT market analysis publications.

---

_Last reviewed: 2026-06-05 by `claude`_
