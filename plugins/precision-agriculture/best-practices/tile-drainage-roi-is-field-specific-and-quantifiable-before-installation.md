# Tile Drainage ROI Is Field-Specific and Quantifiable Before Installation

**Status:** Pattern
**Domain:** Field infrastructure / capital investment
**Applies to:** `precision-agriculture`

---

## Why this exists

Tile drainage investment decisions are often made on agronomic intuition ("that field is wet") rather than on a quantified ROI model. Tile installation costs $500–$1,500/acre depending on depth, spacing, and topography [unverified — training knowledge], and the investment amortizes over 30–50 years. Whether the investment is justified depends entirely on the yield penalty from poor drainage (historically measurable from the field's own yield maps), the number of workable field days gained in wet springs, and the rental or owned cost of the ground. A properly modeled tile drainage ROI frequently shows 8–15% annual returns on wet soils [unverified — training knowledge] — a compelling capital case — but the same model shows negative returns on marginally wet soils that don't have a sustained yield penalty.

## How to apply

Build the tile drainage ROI model before committing capital:

```
Tile drainage ROI model (per acre, annualized):
  Installation cost:                  $______/acre (get at least 2 contractor bids)
  Useful life assumption:             40 years
  Annual capital cost:                installation cost / useful life = $______/acre/year

  Yield response (from field yield history):
    Average yield on tiled comparable zone: ______ bu/acre
    Average yield on untiled wet zone:      ______ bu/acre
    Yield gap (drainage penalty):           ______ bu/acre

  Annual revenue gain:
    Yield gap × expected price:             $______/acre/year

  Additional benefits (field-specific):
    Workable days gained (spring planting timing value): $______/acre/year [ESTIMATE]
    Input efficiency gain (fertilizer placement):        $______/acre/year [ESTIMATE]

  Total annual benefit:                   $______/acre/year
  Annual cost:                            capital cost + maintenance = $______/acre/year
  Annual net:                             benefit − cost = $______/acre/year
  Simple payback:                         installation cost / annual net = ______ years
```

**Do:**
- Use the field's own yield-map history to estimate the drainage penalty — it is the most reliable data source.
- Get contractor bids that include depth and spacing specifications, then validate spacing against the soil type and drainage outlet capacity.
- Include the tile drainage investment in the per-field economics model so future rent decisions reflect the improved productivity.

**Don't:**
- Approve tile installation on rented ground without a long-term lease (minimum equal to the payback period) — drainage investment on annual or short-term leases benefits the landlord, not the operator.
- Assume every wet field benefits equally — fields with inadequate outlet (no ditch, no easement) or shallow bedrock have limited drainage potential regardless of tile spacing.

## Edge cases / when the rule does NOT apply

Irrigation drainage systems in semi-arid environments have different installation logic than Midwest drainage management; the ROI model structure applies, but the agronomic context differs. Surface drainage (terraces, field grading) is evaluated similarly but has different cost structures and agronomic interactions with tile.

## See also

- [`../agents/farm-operations-analyst.md`](../agents/farm-operations-analyst.md) — owns the capital investment ROI model and payback analysis.
- [`../agents/crop-agronomist.md`](../agents/crop-agronomist.md) — advises on drainage requirements by soil type and productivity potential.
- [`./cost-and-margin-are-per-acre-by-field-never-whole-farm-only.md`](./cost-and-margin-are-per-acre-by-field-never-whole-farm-only.md) — tile drainage changes a field's economics permanently; the field-level analysis is where the decision lives.

## Provenance

Tile drainage ROI methodology is documented in Cooperative Extension farm management publications (Iowa State, Purdue, University of Minnesota); cost ranges and yield response estimates are marked `[unverified — training knowledge]`.

---

_Last reviewed: 2026-06-05 by `claude`_
