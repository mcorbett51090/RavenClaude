---
scenario_id: 2026-06-08-auth-ran-out-mid-treatment-and-claims-denied
contributed_at: 2026-06-08
plugin: behavioral-health-practice
product: payer-portal
product_version: "unknown"
scope: likely-general
tags: [prior-authorization, reauth, claims, denial, units, billing]
confidence: high
reviewed: false
---

## Problem

A practice kept getting claims denied mid-treatment for "no authorization on file." Clients were authorized for a block of sessions, treatment continued past the approved unit count, and nobody noticed until the claim bounced — weeks after the sessions were already delivered. By then the practice was carrying unbillable sessions and an awkward re-auth conversation with the payer about visits that had already happened.

## Constraints context

- Authorizations came as a unit count (e.g. "N sessions through a date") but the EHR didn't surface a running "remaining authorized" count against the schedule.
- Different payers had different re-auth lead times and required different medical-necessity attachments.
- The clinician didn't see the auth status at all — it lived in the billing team's portal, not the calendar.

## Attempts

- Tried: reconciling auths manually at month-end. Too late — by the time the spreadsheet was updated, sessions had already been delivered past the limit.
- Tried: a hard stop that blocked scheduling the moment units hit zero. Reduced denials but created clinical disruption — a client hit the wall mid-treatment with no warning, which is exactly the gap to avoid.
- Tried: tracking remaining authorized sessions against the schedule and starting the re-auth a fixed lead time *before* the units ran out (a "sessions before re-auth" buffer), with the medical-necessity attachment assembled from the note in advance. This worked — the re-auth landed before the gap.

## Resolution

Re-auth started before the units ran out, not after a denied claim. The buffer (start the re-auth N sessions before zero) gave billing time to assemble the necessity packet and the payer time to respond, so treatment continued uninterrupted. The auth number and unit count were captured in writing every time — an assumed auth is a denied claim. No PHI lived in the tracking artifacts; the worked example used session counts and `[Member ID]` placeholders, and the medical-necessity content was authored by the clinician, not invented by billing.

## Lesson

Track authorized vs. used sessions with a lead-time buffer and re-auth *before* the units run out. An auth is confirmed in writing (number + unit count) or it doesn't exist, and the code reflects the service rendered — never stretched to fit a stale auth. Verify units and policy with the specific payer; quote any code or limit as `[verify-at-build]`.
