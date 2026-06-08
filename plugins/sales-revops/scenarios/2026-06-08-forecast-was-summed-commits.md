---
scenario_id: 2026-06-08-forecast-was-summed-commits
contributed_at: 2026-06-08
plugin: sales-revops
product: forecast
product_version: "n/a"
scope: likely-general
tags: [forecast, stage-weighting, aging, slip-risk]
confidence: medium
reviewed: false
---

## Problem

A sales team forecast by summing rep-committed deals and missed high three quarters running. The risk: a commit-sum forecast inherits rep optimism and ignores both stage win-rate and deal aging, so it systematically over-calls (§3 #2 #6).

## Context

- Motion: mid-market, monthly commit cadence.
- Constraint: a defensible forecast weights by stage win-rate and ages the pipeline; a commit is an input to calibrate the weights, not the model (§3 #2).
- The team reasoned from the commit roll-up.

## Attempts

- Tried: **rebuilt the forecast as stage-weighted** (`revops_calc.py forecast`). Outcome: the weighted number landed materially below the commit roll-up and far closer to prior actuals.
- Tried: **aged the pipeline** and flagged deals past expected close or beyond stage-normal dwell (§3 #6). Outcome: a cluster of 'commit' deals had dwelt well past stage-normal — classic slips dressed as commits.
- Tried: **calibrated stage win-rates from trailing closed deals** instead of rep confidence. Outcome: a repeatable model that no longer drifted with optimism.

## Resolution

The fix was a **stage-weighted, aged forecast with rep commits used only to calibrate weights** — not a commit sum. Forecast accuracy improved because the model stopped inheriting optimism. The output was the weighted/aged forecast, the slip-flagged deals, and the accuracy delta vs the old method.

**Action for the next consultant hitting this pattern:** **never forecast by summing commits; weight by stage and age the pipeline.** A commit is a calibration input, not the forecast. Pull stage win-rates from trailing closed deals and haircut for slip. See Tree 1 and the `revops_calc.py` `forecast` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
