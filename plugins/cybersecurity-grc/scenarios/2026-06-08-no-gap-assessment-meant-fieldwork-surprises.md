---
scenario_id: 2026-06-08-no-gap-assessment-meant-fieldwork-surprises
contributed_at: 2026-06-08
plugin: cybersecurity-grc
product: soc2
product_version: "unknown"
scope: likely-general
tags: [gap-assessment, audit-readiness, fieldwork, remediation, type-ii]
confidence: high
reviewed: false
---

## Problem

A company went straight into SOC 2 Type II fieldwork without running its own gap assessment first — leadership figured the controls "felt solid" and didn't want to spend on a dry run. During fieldwork the auditor sampled controls across the observation period and surfaced three gaps the team had never checked: a vendor-review cadence that had lapsed, a quarterly access review missing one quarter, and a change-management control whose evidence didn't show approver independence. All three landed as disclosed exceptions in the report — discovered on the auditor's timeline, with no room to remediate before the period closed.

## Constraints context

- ~80 people; first Type II, controls live for roughly the full observation period.
- No prior self-assessment against the actual criteria with the auditor's sampling rigor.
- The report date was already committed to a customer, so there was no slack to extend the window.

## Attempts

- Tried: trusting that controls "felt solid" and skipping the gap assessment to save time and money. Failed — the gaps were exactly the kind a structured self-assessment would have surfaced months earlier.
- Tried: remediating the gaps mid-fieldwork. Failed — a control fixed during fieldwork still didn't operate across the past observation period, so the exception stood for that period regardless.
- Tried (for the next cycle): running a gap assessment before the observation window — against the real criteria, with the same sampling approach the auditor uses, assessing design first then operating effectiveness, and logging each gap as a remediation with an owner and a date. This worked: the gaps were closed and a clean evidence window accrued before the clock started.

## Resolution

The current report carried the three exceptions honestly. For the following cycle the pre-fieldwork gap assessment caught the same class of issues early — the team remediated on its own timeline, stood up the missing cadences, and entered the observation period with controls that demonstrably operated. The report date was set to the evidence window rather than the sales calendar.

## Lesson

Run the gap assessment before fieldwork, not during. The cheapest finding is the one you find yourself. A self-assessment against the actual criteria — design first, then operating effectiveness, with each gap logged as an owned, dated remediation — turns would-be audit exceptions into items you control the timing of. A fix made during fieldwork doesn't un-break a past observation period.
