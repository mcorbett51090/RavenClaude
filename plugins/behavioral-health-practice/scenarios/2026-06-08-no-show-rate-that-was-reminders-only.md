---
scenario_id: 2026-06-08-no-show-rate-that-was-reminders-only
contributed_at: 2026-06-08
plugin: behavioral-health-practice
product: generic
product_version: "unknown"
scope: likely-general
tags: [no-shows, scheduling, telehealth, waitlist, operations, cancellation-policy]
confidence: high
reviewed: false
---

## Problem

An outpatient practice had a ~22% no-show / late-cancellation rate that was wrecking utilization and clinician morale — therapists sat idle while a waitlist of new clients waited weeks for a first session. The practice had "tried reminders" (an automated text the day before) and concluded reminders "don't work." Telehealth visits no-showed even more often than in-person.

## Constraints context

- Mixed in-person + telehealth caseload across ~12 clinicians; payer mix included Medicaid managed care.
- No written cancellation policy clients had actually acknowledged; front desk waived fees inconsistently.
- A freed-up slot from a cancellation just went empty — there was no backfill mechanism.

## Attempts

- Tried: adding a second reminder (two texts instead of one). Marginal — reminders nudge memory but don't change the incentive, and a forgotten telehealth link is a different failure than forgetting the appointment.
- Tried: a punitive no-show fee announced by email. Backfired — clients hadn't acknowledged it, front desk waived it unevenly, and it felt adversarial without fixing the empty-slot problem.
- Tried: pairing the reminder cadence (text + email, plus a call for first-appointments) with a *fair, acknowledged* cancellation policy signed at intake, a telehealth-readiness step (the link + a tech check sent earlier, location/consent confirmed), and a waitlist backfill that auto-offered a freed slot to the next client. This worked.

## Resolution

The no-show rate dropped because the program had both halves — the nudge *and* the consequence — plus the waitlist turned an unavoidable residue of cancellations into filled slots instead of idle hours. The telehealth-readiness step specifically cut the "couldn't connect" sub-category. Crucially, the operational change was justified by clinician hours returned to care, not by a utilization number in isolation. No PHI lived in any of the templates — all examples used `[Client]` / `[DOB]` placeholders, and the clinical-appropriateness of any same-day backfill was left to the clinician.

## Lesson

A no-show program needs both the nudge (reminders) and the consequence (a fair, acknowledged cancellation policy) — plus a waitlist so a freed slot isn't lost. Reminders alone aren't a program. Operations exist to protect the clinical hour: justify the change by clinician time returned to care, keep PHI out of the artifacts, and route any clinical call (e.g. whether a same-day backfill is appropriate) to a clinician.
