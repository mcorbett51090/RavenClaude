---
scenario_id: 2026-06-08-stale-kyc-broke-the-suitability-basis
contributed_at: 2026-06-08
plugin: wealth-management-ria
product: compliance
product_version: "unknown"
scope: likely-general
tags: [suitability, kyc, books-and-records, periodic-review, documentation]
confidence: high
reviewed: false
---

## Problem

A practice ran "annual reviews" that were really market-update calls — the adviser walked the client through performance, took no notes, and re-confirmed nothing about the client's circumstances. Suitability information (objectives, risk tolerance *and capacity*, horizon, liquidity, tax status) had been captured once at onboarding and never refreshed. When a long-time client retired, inherited a property, and quietly shifted to needing income, the portfolio kept running the old growth-tilted allocation. A later examiner asked for the documented basis for continuing that allocation after the client's circumstances changed — and there was nothing in the file. The recommendation wasn't necessarily wrong; it was simply undefensible.

## Constraints context

- KYC was a one-time onboarding form, not a living record refreshed at each review.
- "Reviews" produced no record of what was discussed or re-confirmed — a books-and-records gap as much as a suitability one.
- No trigger linked a life event (retirement, inheritance, a liquidity need) to a suitability re-confirmation.

## Attempts

- Tried: just adding a generic "annual review completed ✓" checkbox to the CRM. Failed — a checkbox with no captured facts proves a call happened, not that suitability was re-confirmed; an examiner reads it as theater.
- Tried: re-papering every client's KYC from scratch each year. Helped completeness but was so heavy that advisers skipped it under load, so the freshest files were the ones that least needed it.
- Tried: a standing periodic-review agenda that re-confirms the core suitability fields, flags any material change, and writes the basis-for-advice (or "no change, basis still holds") into books-and-records — plus event triggers (retirement, inheritance, large liquidity need) that force an off-cycle suitability refresh. This worked.

## Resolution

Making the review agenda re-confirm suitability *and* record the result turned each review into a dated, retained basis instead of a market chat. When the retired client's income need surfaced, the event trigger forced the refresh, the allocation conversation happened on time, and the file showed *why* the portfolio changed and when. The recommendation became defensible because the basis was written and current — KYC was now gathered then refreshed, not captured once and frozen. The lighter standing-agenda format meant advisers actually ran it under load.

## Lesson

Suitability is gathered then refreshed, and if it isn't documented it didn't happen. Re-confirm the core KYC fields at every periodic review, link life events to an off-cycle refresh, and write the basis-for-advice (even "no change") into books-and-records so every recommendation has a current, retained basis. A review that re-confirms nothing and records nothing is a market-update call wearing a compliance label — this is an educational/operational framework, not legal advice.
