# Precision-ag decision tree — adopt a precision-tech tool vs. defer (ROI gate)

**Last reviewed:** 2026-06-05 · **Confidence:** medium (ERS/extension precision-ag ROI ranges + field-economics methodology, web-verified this date). ROI percentages, water/yield deltas, and equipment costs are operation-, region-, and vendor-dependent — they carry inline `[verify-at-use]` / `[ESTIMATE]` markers and must be validated against the operation's actual costs and a measured check before any deliverable (CLAUDE.md §3 #8).

> Canonical decision tree for the `farm-operations-analyst` (the economics) with a market assist from `ag-market-analyst` (input-cost trends). Traverse top-to-bottom **before** recommending a precision-tech purchase — VR planter control, soil-moisture sensors, an imagery/NDVI subscription, a yield-monitor upgrade. The order encodes the house discipline: **prove the problem and the cheap levers before the capital purchase** (CLAUDE.md §3 #1 — economic optimum; §3 #4 — per-acre by field). The capital purchase sits at the bottom on purpose. This is decision-support for the operator, not a guarantee of return (CLAUDE.md §2).

---

## When this applies

A grower or ag-retailer is weighing a precision-ag purchase or subscription and someone has proposed "buy the VR controller / the sensors / the imagery." Common triggers: an equipment-dealer pitch, a renewal, an input-cost spike that "must" justify a tech fix, or a neighbor's adoption. Use this before committing capital — the saving has to be measured per acre, against this operation's costs, with a check.

## The tree

```mermaid
flowchart TD
    START[Precision-tech purchase proposed] --> Q0{Is there a measured, per-acre-by-field problem this tool addresses?}
    Q0 -->|NO - no documented variability / cost gap / yield gap| NOPROB[Not a tech problem yet - quantify the per-acre-by-field gap first - skill: build-per-acre-economics]
    Q0 -->|YES - documented variability or cost/yield gap| Q1{Have the cheap, no-capital levers been used first?}
    Q1 -->|NO - flat rate not yet at economic optimum, no scouting/threshold discipline| CHEAP[Capture the cheap levers first - economic-optimum rate, scout-and-threshold, timing - skills: optimize-input-economics / time-the-operations]
    Q1 -->|YES - cheap levers exhausted| Q2{Is the field variability real and validated, not noise?}
    Q2 -->|NO - yield maps uncleaned, zones unvalidated| VALIDATE[Clean yield maps and validate zones before any VR/sensor spend - knowledge: yield-map-cleaning-precedes-zone-delineation]
    Q2 -->|YES - validated variability| Q3{Does the projected per-acre saving x acres cover the amortized tool cost at THIS operation's costs?}
    Q3 -->|NO - saving too small at your costs| DEFER[Defer - the saving does not clear the capital at your scale and cost; re-check if cost/scale changes]
    Q3 -->|YES - saving clears the capital| Q4{Can the lift be MEASURED, not assumed (check strip / control / ground-truth)?}
    Q4 -->|NO| MEASURE[Build the measurement in first - uniform check strip / control plot / ground-truth - so next season the ROI is a number]
    Q4 -->|YES| ADOPT[Adopt - and instrument the check so the realized ROI is measured against a control, not assumed - scripts/ag_calc.py]
```

## Rationale per leaf (cheap → expensive)

- **Not a tech problem yet (quantify first)** — a precision tool that addresses no *measured* per-acre-by-field gap is a solution shopping for a problem. Build the per-acre economics first (§3 #4); see [`../skills/build-per-acre-economics/SKILL.md`](../skills/build-per-acre-economics/SKILL.md).
- **Capture the cheap levers first** — setting the flat rate at the economic optimum, scout-and-threshold crop protection, and operation timing are no-capital levers that often close much of the gap before any purchase (§3 #1, #3, #6). See [`../skills/optimize-input-economics/SKILL.md`](../skills/optimize-input-economics/SKILL.md).
- **Validate the variability** — VR and sensors pay only when the zones are real. Clean yield maps before delineating zones (uncleaned maps manufacture phantom variability); see [`yield-map-cleaning-precedes-zone-delineation`](../best-practices/yield-map-cleaning-precedes-zone-delineation.md).
- **The ROI test (the load-bearing gate)** — projected per-acre saving × acres must cover the amortized tool cost **at this operation's costs**, not a vendor's reference customer. Published precision-ag ROI sits in modest bands — e.g. precision-planting ROI commonly cited **~8–15%** [verify-at-use], imagery/remote-sensing **~2–10% yield lift + ~5–20% water savings** [verify-at-use], soil-moisture-sensor scheduling **~29% water + ~16% pumping-hour reduction** in one study [verify-at-use] — so a small per-acre saving on a small acreage rarely clears the capital.
- **Measure, don't assume** — build a uniform check strip (VR), a control (sensors/imagery), or a ground-truth step (imagery) so next season's ROI is a measured number, not a hope. Adopting without a control means you never learn whether it paid.

## The economic test (the arithmetic)

A precision tool is justified when, **at this operation's costs and scale**:

```
annual saving = per-acre saving x acres covered
amortized cost = tool capital / useful-life-years + annual subscription/maintenance
adopt on cost only if  annual saving > amortized cost  AND the lift is measurable
```

[`../scripts/ag_calc.py`](../scripts/ag_calc.py) frames the cost side: `vrt-roi` computes the VR-vs-uniform return-to-seed delta net of prescription cost; `input-cost` builds the per-acre stack the saving is measured against; `breakeven` checks the field is above water before adding tech.

## Gotchas

- **Vendor ROI assumes the vendor's volume/variability, not yours** — re-run the saving on *your* acres and costs (`[verify-at-use]`).
- **A yield-maximizer framing kills the ROI** — VR and sensors pay by moving inputs to the economic optimum (pulling them from low-response ground), not by adding inputs everywhere (§3 #1).
- **No check = no learning** — adopting without a control strip / ground-truth means the realized ROI is forever an assumption.
- **Imagery is a scout-trigger, not a spray-trigger** — see the [`../scenarios/2026-06-05-imagery-scouting-false-alarm.md`](../scenarios/2026-06-05-imagery-scouting-false-alarm.md) scenario (§3 #6).

## Escalation & guardrails

- A capital-financing / lease-vs-own structure → [`farm-operations-analyst`](../agents/farm-operations-analyst.md); input-cost-trend context → [`ag-market-analyst`](../agents/ag-market-analyst.md).
- Anything touching grower PII / FMS-platform data → out of scope; the team is PII-neutral and not an FMS/telematics platform (CLAUDE.md §2).
- Every figure entering a deliverable carries a source URL + retrieval date or an `[unverified — training knowledge]` / `[ESTIMATE]` mark (CLAUDE.md §3 #8).

## Sources (retrieved 2026-06-05)

- Farmonaut — _Remote Sensing Precision Agriculture: 2025 AI Playbook_ (precision-ag ROI ranges; UAV ground-truthing): https://farmonaut.com/precision-farming/remote-sensing-precision-agriculture-2025-ai-playbook
- Iowa State Integrated Crop Management — _Variable Rate Seeding — Is It Right For You?_: https://crops.extension.iastate.edu/post/variable-rate-seeding-it-right-you
- Michigan State University Extension — _Utilizing Soil Moisture Sensors for Efficient Irrigation Management_: https://www.canr.msu.edu/resources/utilizing-soil-moisture-sensors-for-efficient-irrigation-management
- farmdoc (U. of Illinois) — _Variable vs. Uniform Seeding Rates for Corn_: https://farmdoc.illinois.edu/field-crop-production/uncategorized/variable-vs-uniform-seeding-rates-for-corn.html
