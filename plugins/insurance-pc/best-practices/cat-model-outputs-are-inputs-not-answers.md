# Cat Model Outputs Are Inputs to the Pricing Decision, Not the Answer

**Status:** Pattern
**Domain:** Catastrophe risk / pricing
**Applies to:** `insurance-pc`

---

## Why this exists

Catastrophe models produce probabilistic loss estimates that are only as valid as the data fed into them and the model's ability to represent the specific exposures being modeled. Over-reliance on a single vendor cat model — treating the model's output as a definitive answer rather than a range estimate with material uncertainty — leads to underestimating cat load, underpricing in concentrated exposures, and false comfort at the portfolio level. The 2011 Thailand floods, the 2017 California wildfires, and the 2017 Harvey/Irma/Maria sequence all produced actual losses significantly above the modeled AAL for a meaningful share of the market, partly because models were not capturing secondary uncertainty correctly for those hazard types.

## How to apply

Use cat model outputs as one input in a multi-input pricing and risk-selection framework.

```
Cat Model Output — Appropriate Use Framework
──────────────────────────────────────────────────────
Step 1 — MODEL SELECTION
  Use at least two vendor models for the same peril/region where available
  (e.g., RMS and AIR for US wind); document which model was used and why
  if only one is available for a given peril.

Step 2 — UNCERTAINTY ACKNOWLEDGMENT
  Cat model outputs carry two forms of uncertainty:
  a) Primary uncertainty (the model's built-in sampling uncertainty)
  b) Secondary uncertainty (the model's inability to represent some exposures)
  For any peril with known secondary uncertainty (e.g., demand surge, coastal flood,
  wildland-urban interface fire), add a loading to the model output.
  Document the loading and its basis.

Step 3 — GROUND-TRUTHING
  Compare the model AAL to:
  - Historical loss experience for the book (if credible volume exists)
  - Industry modeled loss benchmarks for the same peril/region
  - Engineering reports on specific high-value risks

Step 4 — USE IN PRICING
  Cat load in the rate = modeled AAL + uncertainty loading + return-period loading
  (not model AAL alone; the model is the floor, not the all-in cost)

Step 5 — PORTFOLIO-LEVEL CHECK
  Report cat concentration at the portfolio level (PML at 100-year, 250-year)
  using both the modeled estimate and a judgment-loaded upper bound.
  Management decisions on portfolio limits use the upper-bound view.
```

**Do:**
- Disclose the model vendor, model version, and run date on any cat output used in a pricing or accumulation decision — model versions change, and results are not comparable across versions.
- Challenge the model outputs when recent industry losses suggest the model is underestimating; request a model-uncertainty supplemental analysis.
- Set portfolio cat limits (per-event PML) based on a range, not a point, from the cat model outputs.

**Don't:**
- Present cat model output as a precise number — it is a probabilistic estimate with wide confidence intervals, particularly at high return periods.
- Use a cat load derived from a model run on incomplete or outdated property data; the model is only as good as the TIV and location data fed in.
- Rely solely on vendor cat models for emerging perils (e.g., wildfire, flood in new geographies) where model calibration is thin; expert underwriting judgment is a necessary supplement.

## Edge cases / when the rule does NOT apply

- **Cat-light lines** (inland commercial property with no coastal or quake exposure, workers' comp) — cat model outputs are minimal inputs; the pricing is driven by attritional loss experience. The principle of model-as-input still applies for any stochastic loss analysis.
- **Parametric structures** where the trigger is explicitly tied to a model output — here the model IS the contract trigger and the precision concern is about basis risk, not about the model's estimate of the physical event.

## See also

- [`../agents/actuarial-pricing-analyst.md`](../agents/actuarial-pricing-analyst.md) — owns cat load selection and the uncertainty-loading framework.
- [`./isolate-the-catastrophe-load.md`](./isolate-the-catastrophe-load.md) — isolating the cat load in the combined ratio is the portfolio-level complement to this risk's pricing-level discipline.

## Provenance

Codifies the actuarial-pricing-analyst's catastrophe model discipline from the insurance-pc plugin's CLAUDE.md §3 #4 (isolate the catastrophe load) and §3 #8 (cite the source and date for every benchmark). The model-uncertainty framework reflects CAS research on cat model uncertainty and standard reinsurance market practice for PML reporting.

---

_Last reviewed: 2026-06-05 by `claude`_
