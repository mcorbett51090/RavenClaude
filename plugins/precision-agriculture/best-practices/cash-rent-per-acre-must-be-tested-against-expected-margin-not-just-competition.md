# Cash Rent Per Acre Must Be Tested Against Expected Margin, Not Just Competition

**Status:** Absolute rule
**Domain:** Farm economics / land tenancy
**Applies to:** `precision-agriculture`

---

## Why this exists

Cash rent decisions are frequently made by watching what the neighbor paid. That is a competitive benchmark, not an economics test. A field with below-average productivity, poor drainage, or high input requirements may have a competitive market rent of $220/acre while its expected margin is $30/acre. A field at $240/acre with high yield potential and low input cost may yield $120/acre of margin. Paying competitive rent without modeling field-specific economics leads to systematically renting unprofitable ground while missing profitable ground — a common pattern in grain-belt expansion that shows up as margin compression at the portfolio level.

## How to apply

Build the rent-justified economics model for every major land decision:

```
Maximum rent model (per field, per crop year):
  Expected yield:               ______ bu/acre (3-year average of field or comparable fields)
  Expected price:               $______/bu (forward contract or market estimate, dated)
  Expected gross revenue:       _______ bu × $_____ = $______/acre

  Variable costs (non-land):
    Seed:                       $______/acre
    Fertilizer:                 $______/acre
    Crop protection:            $______/acre
    Crop insurance:             $______/acre
    Custom work / fuel:         $______/acre
    Total variable:             $______/acre

  Fixed costs (non-land):
    Equipment depreciation:     $______/acre
    Interest on working capital:$______/acre
    Management:                 $______/acre
    Total fixed (non-land):     $______/acre

  Margin before rent:           gross revenue − total non-land cost = $______/acre
  Target return on land:        $______/acre (minimum acceptable)
  Maximum justified rent:       margin before rent − target return = $______/acre

  Decision: bid at or below maximum justified rent.
  If market rent > maximum justified rent → pass on the field or renegotiate.
```

**Do:**
- Run the model with three price scenarios (base, high, low) — the rent must be survivable at the low price scenario, not just the base.
- Update the model annually at lease renewal; corn price and input cost moves affect the maximum justified rent significantly.
- Include the field's specific yield history in the expected yield input — a landlord's claimed average is not a substitute for actual records.

**Don't:**
- Bid competitive rent on a below-average-productivity field to "keep the ground" without first checking whether it is margin-positive.
- Anchor on the per-acre rent number without converting to a per-bushel equivalent; $220/acre on a 160 bu/acre field is $1.375/bu — on a 130 bu/acre field it is $1.69/bu.

## Edge cases / when the rule does NOT apply

Strategic land tenancy (maintaining a relationship with a landlord who controls multiple parcels, some profitable) may justify renting marginal ground at above-economics rates as a portfolio decision — but this should be an explicit, documented trade-off, not an unexamined habit. Cash-rent decisions for irrigated or specialty-crop ground have much higher revenue potential; the model structure is the same but the input values differ substantially.

## See also

- [`../agents/farm-operations-analyst.md`](../agents/farm-operations-analyst.md) — owns the per-acre economics model and the maximum justified rent calculation.
- [`../agents/agronomy-engagement-lead.md`](../agents/agronomy-engagement-lead.md) — frames rent decisions in the context of the full operation's margin analysis.
- [`./cost-and-margin-are-per-acre-by-field-never-whole-farm-only.md`](./cost-and-margin-are-per-acre-by-field-never-whole-farm-only.md) — the parent rule; rent decisions are the highest-stakes per-field economics call.

## Provenance

Maximum justified rent models are standard in farm management economics; the framework is published by Cooperative Extension farm management programs (Iowa State, Purdue, University of Illinois) and is used by farm management consultants for annual cash rent analysis.

---

_Last reviewed: 2026-06-05 by `claude`_
