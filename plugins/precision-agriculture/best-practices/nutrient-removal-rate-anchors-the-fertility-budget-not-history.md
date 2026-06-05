# Nutrient Removal Rate Anchors the Fertility Budget, Not History

**Status:** Absolute rule
**Domain:** Precision agriculture / fertility management
**Applies to:** `precision-agriculture`

---

## Why this exists

The most common fertility budgeting error is anchoring to last year's program. A grower who applies the same N-P-K rates season after season — regardless of yield, rotation, or soil test changes — is not managing fertility: they are managing inertia. Nutrient removal is determined by actual crop harvest; a 200-bu/ac corn crop removes roughly 0.67 lb N, 0.37 lb P₂O₅, and 0.27 lb K₂O per bushel. When yields vary by zone (as they always do), a flat-rate application over-applies in low-yield zones and under-applies in high-yield zones — both conditions cost margin. The fertility budget must start with a removal estimate tied to yield-goal by zone, adjusted by current soil-test levels, and priced at today's input cost.

## How to apply

Build the fertility budget in three steps: removal estimate, soil-test adjustment, economic test.

```
Fertility Budget Worksheet — [Field / Zone] [Season]
─────────────────────────────────────────────────────
Yield goal (bu/ac):      ___  (by zone if VR; field avg if flat-rate)
Crop:                    [ ] Corn  [ ] Soybean  [ ] Wheat  [ ] Other: ___

Step 1 — Removal estimate (from university removal coefficients)
  N removal:    ___ lb/bu × ___ bu/ac = ___ lb N/ac  (corn: ~0.67; soy: ~3.7 lb/bu)
  P₂O₅ removal: ___ lb/bu × ___ bu/ac = ___ lb P₂O₅/ac  (corn: ~0.37; soy: ~0.75)
  K₂O removal:  ___ lb/bu × ___ bu/ac = ___ lb K₂O/ac   (corn: ~0.27; soy: ~1.17)
  Source / date: ___ [extension removal table, e.g. IPNI / ISU / Purdue]

Step 2 — Soil-test adjustment
  Current soil-test P (ppm):  ___   Target range: ___–___ ppm
  Current soil-test K (ppm):  ___   Target range: ___–___ ppm
  Build / draw-down adjustment: +/- ___ lb P₂O₅/ac  ;  +/- ___ lb K₂O/ac
  N credit (legume / manure): ___ lb N/ac  (source: ___; sample date: ___)

Step 3 — Economic test (N example)
  Adjusted N rate:              ___ lb N/ac
  N product cost ($/lb N):      $___ (source / quote date: ___)
  Total N cost:                 $___ /ac
  Corn price assumption:        $/bu (source / date: ___)
  Marginal N response required to break even:
    = N cost per acre ÷ corn price = ___ bu/ac per lb N applied
  Agronomic response at this N rate vs. EONR: [ ] Within range  [ ] Above EONR — reduce
```

**Do:**
- Pull a new soil test every 2–4 years (or annually on variable-rate zones) — a test older than 4 years is not a soil test, it is archaeology.
- Use university-published removal coefficients (IPNI, ISU, Purdue, NRCS) dated within 5 years; mark older sources `[unverified]`.
- Apply variable-rate fertility when the zone yield data shows more than a 20 bu/ac spread across the field — the cost of a VR prescription is rarely more than the wasted nutrient on the under-performing zone.
- Update removal estimates at the end of every season using actual harvested bushels, not the yield goal.

**Don't:**
- Use last year's application as this year's plan without a soil-test and yield-removal reconciliation.
- Apply a flat N rate across a field with documented high- and low-yield management zones.
- Ignore manure or legume N credits — uncredited N is double-applied N and an unnecessary cost.

## Edge cases / when the rule does NOT apply

Organic systems using only biological N sources may not have a precise lb-N/ac number to work with; the removal framework still applies but is expressed in terms of residue management and cover-crop N fixation estimates. For specialty crops (vegetables, fruit, organic grains) with no published university removal coefficient, use tissue testing in-season as the primary fertility management tool.

## See also
- [`../agents/crop-agronomist.md`](../agents/crop-agronomist.md) — owns fertility decisions and interprets soil-test/tissue data.
- [`../agents/farm-operations-analyst.md`](../agents/farm-operations-analyst.md) — owns per-acre cost and input ROI; runs the economic test on the fertility budget.
- [`../knowledge/ag-economics.md`](../knowledge/ag-economics.md) — covers input ROI and cost-per-acre framework.

## Provenance

Codifies the university extension fertility management standard (Iowa State Extension, Purdue Extension, University of Illinois farmdoc, IPNI nutrient removal data); the economic optimum N rate (EONR) framework is the agronomic standard for corn N management [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
