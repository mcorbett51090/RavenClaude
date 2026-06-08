---
scenario_id: 2026-06-08-base-year-drift-broke-the-trend
contributed_at: 2026-06-08
plugin: esg-sustainability-reporting
product: ghg-protocol
product_version: "unknown"
scope: likely-general
tags: [base-year, recalculation, structural-change, emission-factors, trend, assurance]
confidence: high
reviewed: false
---

## Problem

A company with a public 2030 reduction target reported a 12% drop against its base year and used the number to anchor a target-progress narrative for an insurer and a lender. During the limited-assurance readiness review, the assurer asked for the base-year recalculation policy and the reconciliation behind the 12%. Neither existed in usable form. Two structural changes had landed in the intervening years — a mid-size acquisition that had been folded into the current-year inventory but never added back into the base year, and a switch to a newer emission-factor library that lowered several Scope 2 and Scope 3 lines. The "reduction" was substantially an artifact of an inconsistent baseline, not a real decline in emissions.

## Constraints context

- A public 2030 target already communicated externally; restating the baseline was politically uncomfortable.
- A base year set three years earlier with no documented recalculation policy or significance threshold.
- An emission-factor-library change made for good reasons (the old library was stale) but applied to the current year only.

## Attempts

- Tried: keep the headline and add a footnote that the inventory "reflects updated methodology." Rejected — the dual problem (an acquisition in the numerator year but not the base year, and a one-sided factor change) made the trend non-comparable, and a footnote doesn't restore like-for-like.
- Tried: recalculate only for the factor-library change and leave the acquisition. Rejected — partial recalculation is still an inconsistent boundary; the significance test has to be applied to *every* qualifying structural change, not the convenient ones.
- Tried: write the recalculation policy and significance threshold first, then test both events against it; both crossed the threshold, so the base year was restated for the acquisition (added back) and for the factor change (applied consistently to base and current years). This worked.

## Resolution

The base year was restated under a newly documented recalculation policy: a significance threshold defined up front, the acquisition added back into the base-year inventory, and the new factor library applied to both the base and current years so the comparison was like-for-like. The restated trend was a low-single-digit change rather than 12%, disclosed with the restatement and its trigger. The assurer could then trace the trend to a consistent boundary, and the target-progress narrative was corrected before it hardened further externally.

## Lesson

Base year is a commitment, not a convenience. Set the recalculation policy and significance threshold up front, apply the structural-change test to every qualifying event (acquisitions, divestitures, methodology and factor-library shifts), and restate the base year — and disclose the restatement — when the threshold is crossed. A baseline that drifts silently turns an emission-factor housekeeping change into a fake reduction that won't survive assurance.
