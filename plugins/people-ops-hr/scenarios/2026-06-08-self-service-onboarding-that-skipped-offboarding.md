---
scenario_id: 2026-06-08-self-service-onboarding-that-skipped-offboarding
contributed_at: 2026-06-08
plugin: people-ops-hr
product: bamboohr
product_version: "unknown"
scope: likely-general
tags: [lifecycle, onboarding, offboarding, hris, access, final-pay]
confidence: high
reviewed: false
---

## Problem

A fast-growing startup had invested in a polished onboarding experience — a slick first-day checklist, swag, a buddy program — and was proud of it. But there was no equivalent for offboarding: when someone left, it was improvised the day of, by whoever happened to be around. A security audit then found three former employees still had active SSO access weeks after their last day, one final paycheck had been calculated on a stale PTO balance, and the HRIS still listed two departed people as "active" — which meant headcount reports and the benefits census were both wrong.

## Constraints context

- The HRIS (BambooHR) was the supposed system of record, but offboarding never reliably updated it, so downstream reports drifted.
- Access provisioning was centralized; deprovisioning was not — nobody owned the revocation step.
- Final pay depended on an accurate PTO balance that lived in a field nobody confirmed at exit.

## Attempts

- Tried: a reminder email to managers to "handle offboarding." Failed — no owned checklist meant steps were skipped inconsistently, and the security-critical ones (access) were exactly the ones forgotten.
- Tried: making IT solely responsible for deprovisioning. Failed — IT wasn't told in time because the trigger (the HRIS status change) was itself unreliable.
- Tried: building an owned offboarding checklist mirroring onboarding — access revocation, final pay handoff (with a confirmed PTO balance), equipment return, knowledge transfer, and the HRIS status/term-date update as the *first* step that triggers the rest. This worked.

## Resolution

Making the HRIS status change the trigger meant access revocation, the benefits census, and headcount reports all flowed from one canonical event instead of separate memories. The final-pay step now confirmed the PTO balance before calculation, and the access-revocation step had a named owner with an SLA. The separation-agreement and final-pay-timing questions were flagged for counsel rather than answered in the checklist.

## Lesson

Offboarding is half the lifecycle and the half everyone forgets — give it an owned checklist (access, final pay, equipment, knowledge transfer) and make the HRIS update the trigger, because the HRIS is the source of truth or it's nothing. Route final-pay timing and separation terms to counsel.
