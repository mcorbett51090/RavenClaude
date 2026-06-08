---
scenario_id: 2026-06-08-loss-ratio-mistaken-for-mlr-rebate
contributed_at: 2026-06-08
plugin: insurance-life-health-benefits
product: fully-insured
product_version: "unknown"
scope: likely-general
tags: [underwriting, loss-ratio, mlr, aca, rating, verify-at-build]
confidence: high
reviewed: false
---

## Problem

A fully-insured employer's broker pulled a claims report, computed incurred claims ÷ earned premium at ~78%, and told leadership "we're under 80%, so the carrier owes us an ACA MLR rebate — budget for it." Finance penciled the rebate into next year's numbers. The 78% was the raw underwriting loss ratio, not the ACA medical-loss-ratio calculation, and the rebate never came — leaving a hole in the forecast.

## Constraints context

- The raw loss ratio (claims ÷ premium) and the ACA MLR test (80%/85% rebate thresholds) were being treated as the same number.
- The MLR numerator adds quality-improvement spend and applies credibility and risk adjustment, and it's measured on a pooled, multi-year basis at the issuer/market level — not on one employer's single-year claims report.
- Nobody had marked the 80% threshold `[verify-at-build]`; it was quoted from memory.

## Attempts

- Tried: take the 78% loss ratio as the MLR and book the rebate. Failed — conflating the underwriting loss ratio with the regulatory MLR test is the classic error; one group's raw loss ratio doesn't determine an issuer-level, credibility-adjusted MLR rebate.
- Tried: run the raw loss ratio AND the MLR rebate flag as two distinct numbers (the calculator's `loss-ratio` mode does exactly this), and verify the current-year 80%/85% threshold against the CMS source rather than memory. This separated the two cleanly.
- Tried: route the actual MLR-rebate question to the carrier and a credentialed actuary, since the issuer-level MLR is theirs to compute, not the employer's. This was the correct hand-off.

## Resolution

The forecast rebate was pulled back out — the 78% loss ratio was a useful underwriting signal (the book was running rich) but was never the MLR test. The team showed both numbers side by side, flagged the threshold `[verify-at-build]`, and let the carrier/actuary confirm whether any issuer-level MLR rebate was actually owed. Finance re-planned without the phantom rebate.

## Lesson

The underwriting loss ratio (claims ÷ premium) is not the ACA MLR test, and one group's single-year ratio doesn't trigger an issuer-level, credibility-adjusted rebate — never conflate them, and verify the 80%/85% threshold against the current-year source. (Educational scaffolding; a credentialed actuary and the carrier confirm the actual MLR and any rebate.)
