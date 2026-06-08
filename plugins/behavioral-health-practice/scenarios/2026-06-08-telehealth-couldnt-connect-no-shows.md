---
scenario_id: 2026-06-08-telehealth-couldnt-connect-no-shows
contributed_at: 2026-06-08
plugin: behavioral-health-practice
product: generic
product_version: "unknown"
scope: likely-general
tags: [telehealth, no-shows, readiness, scheduling, place-of-service, consent]
confidence: high
reviewed: false
---

## Problem

A practice's telehealth no-show rate was meaningfully higher than its in-person rate, and the front desk had written it off as "telehealth clients are flakier." Digging in, a large share of the "no-shows" weren't no-shows at all — clients showed up but couldn't connect: wrong link, camera permissions, joining from a phone in a parking lot. Some had also moved out of state, which quietly broke both the clinician's licensure footing and the payer's coverage.

## Constraints context

- The join link was buried in a confirmation email sent at booking, sometimes weeks ahead — clients couldn't find it day-of.
- No tech check or location confirmation happened before the visit; the first time anyone learned the client had moved was when the clinician asked on camera.
- Telehealth place-of-service and modifier handling on the claim was inconsistent, so even connected visits sometimes denied.

## Attempts

- Tried: blaming the clients and tightening the no-show fee. Backfired — it punished a logistics failure the practice had created, and didn't fix the connection problem.
- Tried: re-sending the same confirmation email. Marginal — the link was still buried and there was still no tech check or location confirmation.
- Tried: treating readiness as a step of the appointment — a same-day join link plus a brief tech check, a location confirmation (for licensure / payer / emergency response), and a modality-consent check, with the place-of-service + telehealth modifier confirmed against current payer policy before billing. This worked.

## Resolution

The "couldn't connect" sub-category of no-shows dropped once readiness was an explicit step rather than an afterthought, and the location check caught out-of-state clients before a visit that couldn't be lawfully or billably delivered. The clinical-appropriateness of telehealth for any given client stayed the clinician's call — the plugin owned only the logistics. No PHI sat in the readiness templates; examples used `[Client]` placeholders, and the modifier/POS specifics were flagged `[verify-at-build]` against the payer's current policy.

## Lesson

A telehealth visit fails differently than an in-person one — treat readiness (link + tech check + location + consent) as part of the appointment, not an afterthought. A "couldn't connect" is a preventable operational failure, not a flaky client. Confirm the place-of-service and telehealth modifier against current payer policy before billing, and route the clinical-appropriateness call to a clinician.
