# Planting Population Is an Economic Decision, Not a Seed Company Recommendation

**Status:** Pattern
**Domain:** Crop agronomy / input economics
**Applies to:** `precision-agriculture`

---

## Why this exists

Seed company population recommendations are built to maximize agronomic yield in a broad range of conditions — they are not built to maximize the grower's return. Seed is a significant input cost ($90–$130/bag corn, $50–$70/bag soybeans [unverified — training knowledge]), and the optimal population from a return standpoint is often below the agronomic maximum. The response curve for corn typically flattens around 32,000–34,000 seeds/acre in high-productivity environments — pushing to 36,000+ rarely recovers the extra seed cost [unverified — training knowledge]. Variable-rate population by zone, calibrated to the zone's productivity potential, captures the benefit of higher populations where they pay and recovers the seed cost in lower-yield zones.

## How to apply

Build the population-response economic model before setting the prescription:

```
Population response analysis (per zone or field):
  Seed cost per bag:        $______
  Seeds per bag:            80,000 (typical corn) [unverified]
  Cost per 1,000 seeds:     $______

  Response curve test (from university data or on-farm trials):
    Population A (low):     ______ seeds/acre → yield: _______ bu/acre
    Population B (medium):  ______ seeds/acre → yield: _______ bu/acre
    Population C (high):    ______ seeds/acre → yield: _______ bu/acre

  Economic optimum test:
    Marginal seed cost per 1,000-seed increase: $______/acre
    Marginal yield response per 1,000-seed increase: ______ bu/acre × corn price = $______/acre
    Optimum: highest population where marginal return exceeds marginal cost

  VR population by zone:
    High-yield zone:  ______ seeds/acre (above-average response expected)
    Mid-yield zone:   ______ seeds/acre (flat rate or moderate increase)
    Low-yield zone:   ______ seeds/acre (below-average — recover seed cost)
```

**Do:**
- Use on-farm population trials (replicated strips) when possible — the response curve is field- and hybrid-specific.
- Update the population prescription annually; seed price and corn price both affect the optimum.
- Report the seed cost and expected yield response side by side on every VR population prescription — the economics, not just the agronomy, must be visible.

**Don't:**
- Apply a seed company's maximum recommended population uniformly across all zones without the response-curve economics.
- Reduce population below the agronomic minimum for canopy cover (which affects weed competition, standability, and disease) in the name of cost savings — the optimum has a floor.

## Edge cases / when the rule does NOT apply

Seed corn production (detasseling programs) has a separate population structure driven by production contract specifications, not commercial population response curves. Organic production may require higher populations to manage weed competition as a service function of the canopy.

## See also

- [`../agents/crop-agronomist.md`](../agents/crop-agronomist.md) — owns the response-curve interpretation and hybrid-specific population guidance.
- [`../agents/farm-operations-analyst.md`](../agents/farm-operations-analyst.md) — owns the input ROI model and the economic optimum calculation.
- [`./manage-to-economic-optimum-not-maximum-yield.md`](./manage-to-economic-optimum-not-maximum-yield.md) — the parent rule; planting population is one of the highest-cost input decisions where optimum vs. maximum matters most.

## Provenance

Economic optimum population analysis is standard in Cooperative Extension agronomic guidance (Iowa State, Purdue, University of Illinois); the concept of VR population management is well established in precision-ag literature.

---

_Last reviewed: 2026-06-05 by `claude`_
