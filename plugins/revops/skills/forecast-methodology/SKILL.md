---
name: forecast-methodology
description: "Choose and run a B2B sales forecast as a methodology with a named bias: weighted-by-stage vs commit/category vs AI/regression, coverage derived from this segment's win-rate (not a folk 3x), sales-velocity math, deal inspection for padded/stale pipeline, and a back-test against recent quarters before trusting the number."
---

# Forecast Methodology

## A forecast is a method with a named bias
Name the method, its inputs, and its known bias every time. Weighted-by-stage over-counts early pipeline; commit/category is rep-sentiment-driven (sandbagging or happy-ears); AI/regression needs clean multi-quarter history and is blind to an unprecedented deal. Report weighted *and* commit side by side, with the gap named.

## Stage exit criteria drive the probabilities
Every stage's probability comes from your own historical stage→close conversion, not the CRM's out-of-the-box 10/25/50/75. A stage defined by rep optimism makes its probability meaningless — anchor each stage to an objective buyer action first.

## Inspect before you compute
Coverage/win-rate/velocity on padded or stale pipeline is precise nonsense. Flag stuck/aged/past-close-date/no-recent-activity deals, clean the number, and make every aggregate traceable to an inspected deal list.

## Derive coverage from win-rate
Required coverage = gap-to-target ÷ stage-weighted win-rate. "3x" is somebody else's win-rate; derive from *this* segment's conversion and recompute as it drifts. Apply it only to inspected pipeline.

## Velocity is the lever-finder
Sales velocity = (open opps × win-rate × avg deal size) ÷ avg cycle length. It isolates which input a proposed change actually moves — so you can tell a real lever from a vanity initiative.

## Back-test before you trust
A method earns trust by reconstructing the last several quarters within tolerance, not by sounding sophisticated. Report the back-test bias and the tolerance alongside the forecast.

## Output
A forecast-and-pipeline spec: the chosen method + its bias, stage exit criteria + historical probabilities, the win-rate-derived coverage target, win-rate/velocity, the deal-inspection pass, and the back-test. Route warehouse/dashboard build to `data-platform` / `tableau`; significance questions to `applied-statistics`.
