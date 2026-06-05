# Variable-Rate Application Requires Zone Map Validation Before Planting

**Status:** Absolute rule
**Domain:** Precision agronomy / variable-rate technology
**Applies to:** `precision-agriculture`

---

## Why this exists

Variable-rate application (VRA) for seed, fertilizer, or crop protection depends on the accuracy of the underlying zone map. A zone map built on a single year of yield data, uncorrected soil sampling, or poorly georeferenced imagery will direct inputs to the wrong zones — systematically over-applying in high-yield zones and under-applying in the zones that most need treatment. The cost of a wrong VRA map is not visible until harvest, at which point it is too late to recover the lost yield or the wasted inputs. Validating the zone map against multiple data layers before planting is the diagnostic step that makes VRA agronomically and economically defensible.

## How to apply

Run the zone map validation checklist before committing any VRA prescription:

```
Zone map validation checklist:
  Data layers used to build the zone map:
  [ ] Yield data — minimum 3 years of same-crop yield (single-year yield maps are noisy)
  [ ] Soil EC (electrical conductivity) — georeferenced to the same grid as yield data
  [ ] Soil sampling — grid or zone-based, current (within 2 crop years)
  [ ] Topography / slope — available from DEM or LiDAR for drainage-driven variability
  [ ] Historical aerial/satellite imagery — NDVI or similar for consistent variability patterns

  Validation test:
  [ ] Do zone boundaries align with at least 2 independent data layers? (one is noise; two is signal)
  [ ] Are zone areas large enough for equipment turn-around (minimum 2–3 acres per zone)?
  [ ] Have any zones shifted substantially from the prior year's map? Flag and investigate before applying.
  [ ] Is the prescription file format compatible with the application equipment controller?

  If zone map fails validation → revert to flat-rate application while rebuilding the map.
```

**Do:**
- Treat zone map validation as an annual pre-season step, not a one-time setup.
- Ground-truth at least 3–5 zone boundaries per field by walking the boundary and confirming the soil/yield transition is visible.
- Archive all validation data with the VRA prescription; if the prescription is questioned post-harvest, the audit trail is essential.

**Don't:**
- Apply a VRA prescription built on a single data layer — yield alone, EC alone, or imagery alone is insufficient.
- Use zone maps without checking prescription file compatibility with the applicator controller; mismatched files apply the wrong rates silently.

## Edge cases / when the rule does NOT apply

Fields smaller than 15 acres with highly uniform soils may not justify the overhead of multi-layer zone mapping; a uniform flat-rate prescription based on soil testing is the correct choice. For precision irrigation (VRI), the validation applies to the zones driving irrigation scheduling, not the nutrient-application zones.

## See also

- [`../agents/crop-agronomist.md`](../agents/crop-agronomist.md) — owns the zone map review and prescription validation.
- [`../agents/farm-operations-analyst.md`](../agents/farm-operations-analyst.md) — owns the per-zone input ROI model that the prescription must satisfy.
- [`./read-yield-by-management-zone-not-field-average.md`](./read-yield-by-management-zone-not-field-average.md) — the parent rule; VRA execution is what acts on the zone analysis that rule requires.

## Provenance

Multi-data-layer zone validation is standard precision-ag consulting practice; single-year yield map risk is documented in precision-agriculture extension literature (Purdue, Iowa State, USDA-ARS).

---

_Last reviewed: 2026-06-05 by `claude`_
