# Harvest Loss Is a Recoverable Yield Gap, Not Equipment Noise

**Status:** Pattern
**Domain:** Harvest operations / yield economics
**Applies to:** `precision-agriculture`

---

## Why this exists

Harvest losses — grain lost behind the combine header, at the cylinder/rotor, or at the sieves — are frequently treated as an unavoidable byproduct of harvest speed and conditions. They are a measurable, recoverable yield gap. A combine losing 1 bu/acre at 200 acres/day is leaving $56,000 of corn on the ground over a 200-day harvest season at $5.60/bu [unverified — training knowledge, prices vary]. Combine loss monitors are often read as background noise; a loss audit — actually counting grain behind the machine at multiple points — turns the number into a recoverable decision. The adjustment that recovers 0.5 bu/acre across the operation is more valuable, and free, than most input additions.

## How to apply

Build the harvest loss audit into pre-harvest and in-season protocols:

```
Harvest loss audit (per field, per crop):
  Pre-harvest check:
    Test header loss at 3 points across the field width
    Threshold: < 1 bu/acre corn acceptable; > 1.5 bu/acre → header adjustment before proceeding

  In-harvest loss protocol:
    After stopping the combine: count kernels in a 10 sq ft area behind the machine
    Count-to-bushels conversion: 2 kernels per sq ft ≈ 1 bu/acre loss [ESTIMATE]
    Record by field and by adjustment state

  Loss reduction levers (in cost order):
    1. Ground speed reduction (0.5–1 mph slower can cut rotor/cylinder loss 20–30%) [unverified]
    2. Header height and reel speed adjustment (header loss is almost always adjustable)
    3. Crop moisture — harvest at optimum moisture, not convenience; dry corn shatters
    4. Cylinder/rotor settings — match to the crop's threshability at current moisture

  ROI calculation:
    Loss recovered (bu/acre) × price ($/bu) × acres = $______
    vs. machine adjustment time or speed reduction cost = $______
    Net recovery: $______
```

**Do:**
- Conduct a loss audit at the start of each crop and after any significant moisture or variety change.
- Report header loss and machine loss separately — they respond to different adjustments.
- Include harvest loss in the per-acre economics model; it is a recoverable yield gap, not a yield ceiling.

**Don't:**
- Accept combine loss monitor readings as the sole loss measurement — they drift and require calibration; physical counts are the ground truth.
- Prioritize acres-per-day over loss rate when the math shows the loss rate is more expensive than the speed gain.

## Edge cases / when the rule does NOT apply

Specialty crops (soybeans in difficult lodging conditions, small grains with heavy disease) have loss patterns that require specific header technology rather than adjustment alone — the audit discipline still applies, but the action set is different. Corn silage harvest (all-in chopping) has different loss mechanics; the rule applies to grain harvest operations.

## See also

- [`../agents/farm-operations-analyst.md`](../agents/farm-operations-analyst.md) — owns the per-acre yield gap analysis and harvest loss ROI model.
- [`../agents/crop-agronomist.md`](../agents/crop-agronomist.md) — advises on optimal harvest timing and moisture targets for loss minimization.
- [`./manage-to-economic-optimum-not-maximum-yield.md`](./manage-to-economic-optimum-not-maximum-yield.md) — harvest loss recovery is one of the few cases where recovering yield directly equals recovering margin; the optimum IS the recoverable.

## Provenance

Harvest loss counting methodology and thresholds are from USDA and Cooperative Extension programs (Iowa State, Purdue); loss-to-bushel conversion is a standard field technique. All quantitative figures marked `[unverified]` or `[ESTIMATE]`.

---

_Last reviewed: 2026-06-05 by `claude`_
