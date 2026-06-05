# Yield Map Cleaning Precedes Zone Delineation

**Status:** Absolute rule
**Domain:** Precision agriculture / precision data management
**Applies to:** `precision-agriculture`

---

## Why this exists

A yield map straight off the combine monitor is not a management map — it is a raw data file with combine-speed ramp errors, headland noise, overlap passes, and moisture outliers that can swing apparent yield by 30–60 bu/ac in the same field. If zone delineation, variable-rate prescriptions, or profitability analysis are run on uncleaned data, every downstream decision inherits the noise. The most common result: a "low-yield zone" that is actually a headland speed error gets assigned a build-up fertility rate it doesn't agronomically need. Cleaning the yield map to remove statistical outliers and operator error is not optional before management-zone analysis.

## How to apply

Run a four-step cleaning protocol on every year's yield data before using it for zone work or economic analysis:

```
Yield Map Cleaning Protocol — [Field] [Crop] [Season]
──────────────────────────────────────────────────────
Step 1 — Remove speed outliers
  Flag all points where combine speed < [minimum cut speed] or > [max travel speed]
  Threshold: typically < 2 mph (ramping) or > 6 mph (header raising)
  Points flagged: ___  (___% of total)
  Action: DELETE

Step 2 — Remove moisture outliers
  Flag all points where grain moisture is outside the plausible range for this crop/harvest date
  Typical corn range at harvest: 13–30%; flag outside this range
  Points flagged: ___
  Action: DELETE (moisture sensor lag creates yield errors)

Step 3 — Remove statistical outliers (per-pass or interpolated grid)
  Calculate field mean and standard deviation for each 1-ac grid or swath
  Flag points > mean ± 2.5 SD (or 3 SD if the field has known high/low zones)
  Points flagged: ___  (___% of total)
  Action: REVIEW — delete obvious errors; retain agronomically defensible extremes

Step 4 — Multi-year stack (for zone delineation)
  Minimum years recommended: 3–5
  Normalize each year to a common base (z-score or % of field mean)
  Identify zones that are consistently high / medium / low across ALL years
  Zones with inconsistent rank across years: [ ] Not stable — defer VR until more data
```

| Error type | Typical magnitude | Cleaning step |
|---|---|---|
| Speed-ramp at headland | ±30–60 bu/ac | Step 1 |
| Moisture-sensor lag | ±15–25 bu/ac | Step 2 |
| Statistical outlier (sensor spike) | ±10–40 bu/ac | Step 3 |
| Single-year weather anomaly (zone flip) | ±20 bu/ac | Step 4 (multi-year) |

**Do:**
- Clean data before importing it into any zone-delineation tool (SMS, Climate FieldView, John Deere Ops Center, Granular).
- Retain the raw file; the cleaned file is a derived product — if a question arises, the raw data is the record.
- Run at least 3 years of cleaned yield before committing to a variable-rate prescription; one year of clean data still reflects weather, not management zones.
- Document the cleaning parameters (speed threshold, moisture threshold, SD cutoff) so the analysis is reproducible.

**Don't:**
- Use the default export from the combine monitor as the zone map input — the manufacturer default cleaning thresholds are designed for broad-acre visualization, not management-zone analytics.
- Smooth or interpolate across headlands — headland yield is structurally different (turns, planter-overlap, row-end variability) and should be excluded from interior zone analysis.
- Let a single drought year define a permanent low-yield zone — drought often inverts the normal zone rank (sandy high-ground that underperforms in wet years can outperform in dry years).

## Edge cases / when the rule does NOT apply

Fields with less than 3 years of yield data should not use yield-monitor data as the sole zone-delineation input; EC mapping (soil electrical conductivity) or soil-type layers are more reliable for zone work on new or short-history fields. Livestock pastures and forage fields without precision yield monitoring do not have a data source to clean — use soil test and visual observation for zone management.

## See also
- [`../agents/farm-operations-analyst.md`](../agents/farm-operations-analyst.md) — owns yield analytics and zone performance reporting.
- [`../agents/crop-agronomist.md`](../agents/crop-agronomist.md) — uses cleaned zone data to set variable-rate fertility and seeding prescriptions.
- [`../knowledge/ag-kpi-glossary.md`](../knowledge/ag-kpi-glossary.md) — defines yield-monitor data quality and management-zone terms.

## Provenance

Codifies the precision-agriculture data management standard; cleaning protocols are recommended by the International Society of Precision Agriculture (ISPA) and are the de facto standard in commercial precision-ag software documentation [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
