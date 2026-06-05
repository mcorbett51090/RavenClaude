# Hybrid Variety Selection Is a Field-Specific Risk Decision, Not a Catalog Ranking

**Status:** Pattern
**Domain:** Crop agronomy / input selection
**Applies to:** `precision-agriculture`

---

## Why this exists

Seed company yield rankings and company trial data are produced under managed, high-productivity conditions that favor high-yielding, disease-susceptible hybrids. The field a grower is choosing for has its own disease history, drainage limitations, soil pH variability, and stress patterns. A hybrid that ranks first in the trial book may be third in a field with gray leaf spot history or poor drainage in one corner. Choosing hybrids on catalog yield rank without filtering for the field's specific risk environment consistently underperforms selections made on stress tolerance and local trial data.

## How to apply

Build the hybrid selection checklist before placing the seed order:

```
Hybrid selection decision framework (per field or zone):
  Field risk inventory:
  [ ] Disease history: gray leaf spot, northern corn leaf blight, SDS, SCN, white mold?
  [ ] Drainage class: well-drained / moderately well-drained / poorly drained?
  [ ] Soil pH range: ______ (flag fields with pH < 6.0 or > 7.2)
  [ ] Root lodging history (prior 3 years)?
  [ ] Herbicide carryover risk (prior ALS or acetochlor programs)?

  Data sources for hybrid evaluation (in priority order):
  1. Independent university trial data (closest location, similar soil type)
  2. Local co-op trial data (multiple years preferred over single-year rankings)
  3. Seed company trial data (acceptable, but filter for comparable trial conditions)
  4. Catalog yield rank alone: not sufficient

  Selection filters (must pass before placing order):
    For GLS-risk fields:         Select hybrids with GLS rating ≥ 7/9 [unverified scale]
    For wet/drainage-risk:       Select hybrids with standability and SDS tolerance ratings
    For high-yield environments: Maximize yield potential, tolerate single-ear-flex hybrids

  Spread risk by placing ≥ 2 hybrids per farm, with different stress packages.
```

**Do:**
- Use at least 2 years of local trial data before anchoring on a hybrid; single-year trial data is noisy.
- Split acres between a proven performer and a new entrant — do not bet the operation on an unproven hybrid in year one.
- Document the selection rationale and the field risk factors so the decision can be evaluated post-harvest.

**Don't:**
- Choose hybrids based solely on catalog yield rank without filtering for the field's specific stress environment.
- Buy all seed from one supplier as a convenience decision; multi-supplier sourcing also reduces supply disruption risk.

## Edge cases / when the rule does NOT apply

Contract production (seed corn, specialty) often requires the contractor's specified variety — there is no selection decision. Certified organic seed sourcing may limit the hybrid pool to organically treated or OP varieties; the selection discipline still applies within the available pool.

## See also

- [`../agents/crop-agronomist.md`](../agents/crop-agronomist.md) — owns the hybrid selection process and disease-rating interpretation.
- [`../agents/farm-operations-analyst.md`](../agents/farm-operations-analyst.md) — models the yield-risk tradeoff of high-yield vs. stress-tolerant hybrid choices on a per-field basis.
- [`./read-yield-by-management-zone-not-field-average.md`](./read-yield-by-management-zone-not-field-average.md) — the field's zone yield history is the best filter for hybrid stress-environment selection.

## Provenance

Field-specific hybrid selection methodology is standard in agronomic consulting and university extension hybrid-testing programs; the stress-tolerance filtering approach is documented in Cooperative Extension corn and soybean hybrid-selection guides.

---

_Last reviewed: 2026-06-05 by `claude`_
