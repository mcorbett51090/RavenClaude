---
scenario_id: 2026-06-05-capacity-factor-underperformance
contributed_at: 2026-06-05
plugin: renewable-energy
product: operations
product_version: "n/a"
scope: likely-general
tags: [capacity-factor, degradation, availability, p90, underperformance]
confidence: medium
reviewed: false
---

## Problem

An operating solar asset's measured **capacity factor** came in below the pro-forma, and the owner/lender flagged "underperformance." The reflex was to blame module degradation. The risk: conflating distinct effects — availability (downtime) vs. degradation (permanent yield loss) vs. resource variability (a low-irradiance year vs. a P50/P90 miss) — and "fixing" the wrong one (CLAUDE.md §3 #5 — degradation and O&M are first-class; §3 #6 — production is P50/P90, not a single number).

## Context

- Segment: operating utility-scale PV, year 2–3, financed on a P50 production estimate.
- Constraint: a capacity-factor shortfall has **at least three independent causes that look identical in the topline number** — (a) **availability** loss (inverter/tracker downtime, grid curtailment), a recoverable O&M problem; (b) **degradation** (a first-year LID step of ~2–3% then ~0.5–0.7%/yr [verify-at-use]), permanent but predictable; (c) **resource variability** — a genuinely low-irradiance year, where the asset is fine and the *single-number* P50 expectation was the error (it should have been read against P90). Capacity factor and availability are **different metrics** and must be reported separately.
- The owner was reading one blended number and reaching for a module-replacement narrative.

## Attempts

- Tried: **decomposed** the shortfall — measured availability (uptime) separately from energy yield, and compared actual irradiance to the resource assumption. Outcome: most of the gap was availability (tracker downtime + a curtailment month), not degradation.
- Tried: checked the measured degradation against the warranty/expected curve (first-year step + linear rate) to confirm it was within band, not accelerated. Outcome: degradation was on-curve — not the culprit.
- Tried: re-read the production expectation as **P50 vs P90** — the "miss" was partly a normal low-resource year that a P90-sized expectation would have absorbed. Outcome: reframed lender conversation from "asset underperforming" to "P50 year-to-year variance, availability recoverable."

## Resolution

The shortfall was **mostly recoverable availability loss plus normal resource variance — not degradation**, found by decomposing the blended capacity factor into availability, degradation, and resource components and reading the expectation against P90 rather than P50. The fix was an O&M response (tracker/inverter uptime) and a corrected reporting frame, not a module replacement. The output was a dated performance read separating the three causes with each metric reported on its own (CLAUDE.md §3 #5, #6).

**Action for the next consultant hitting this pattern:** **decompose a capacity-factor shortfall into availability vs. degradation vs. resource variability before naming a cause — they look identical in the topline and point to opposite fixes.** Report capacity factor and availability separately; check degradation against the expected curve before assuming it; read production against P90, not a single P50. The asset-performance lane is owned by [`energy-finance-analyst`](../agents/energy-finance-analyst.md); the [`../scripts/renewables_calc.py`](../scripts/renewables_calc.py) `capacity-factor` mode converts measured energy to a CF for the comparison.

**Sources (retrieved 2026-06-05):**
- LBNL / Berkeley Lab — *Utility-Scale Solar, 2025 Edition* (capacity-factor benchmarks, ~24% average): https://emp.lbl.gov/sites/default/files/2025-10/Utility%20Scale%20Solar%202025%20Edition%20Slides.pdf
- NREL — *Photovoltaic Degradation Rates* (first-year step + ~0.5–0.7%/yr linear): https://docs.nrel.gov/docs/fy20osti/77257.pdf
- NREL ATB — *Utility-Scale PV* (degradation assumption in capacity-factor modeling): https://atb.nrel.gov/electricity/2024/utility-scale_pv

Capacity-factor benchmarks and degradation rates are site-, technology-, and year-specific — treat every figure as `[verify-at-use]` and ground in the asset's own metered data and resource record (§3 #5, #6, #8).
