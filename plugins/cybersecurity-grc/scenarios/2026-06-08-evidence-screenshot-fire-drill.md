---
scenario_id: 2026-06-08-evidence-screenshot-fire-drill
contributed_at: 2026-06-08
plugin: cybersecurity-grc
product: soc2
product_version: "unknown"
scope: likely-general
tags: [evidence, ccm, type-ii, operating-effectiveness, audit-readiness]
confidence: high
reviewed: false
---

## Problem

A SaaS company pursuing its first SOC 2 Type II spent the week before fieldwork in a frantic scramble — engineers screenshotting IAM consoles, exporting ticket histories by hand, and reconstructing access-review records that hadn't actually been performed on cadence. The auditor sampled the access-review control across the observation period and found three months with no record. What had been described internally as "we have an access-review control" was, in evidence terms, design-only: a policy existed, but there was no proof it had operated.

## Constraints context

- ~60 engineers; controls had been "live" for about four months but the Type II observation period was six.
- Evidence was entirely manual — no continuous control monitoring, no GRC platform integrations.
- Leadership had committed a report date to a prospect before checking the evidence window.

## Attempts

- Tried: back-filling the missing access reviews the week of fieldwork. Failed — the auditor flagged that evidence created after the fact for a past period isn't evidence the control operated then; it became an exception.
- Tried: arguing the control was "in place" because the policy existed. Failed — design state is not operating effectiveness; the auditor needs the control to have run across the period.
- Tried: wiring evidence collection to the source — an automated quarterly access-review workflow that records reviewer, date, and decisions, plus an API export of IAM state on a schedule, retained automatically. Combined with shifting the report date to capture a full clean observation period. This worked for the *next* cycle.

## Resolution

The current report carried the access-review exception honestly (a narrow, disclosed exception beat a back-filled fabrication the auditor would catch). For the following period, continuous control monitoring at the source meant evidence accumulated automatically and the control demonstrably operated. The report date was set to the evidence window, not the sales calendar.

## Lesson

Evidence is a system, not a fire drill, and a control has three states — designed, implemented, operating-effectively. A policy without evidence it ran over the period is design-only; Type II needs the third state. Automate evidence at the source and set the report date to the observation window, not to a deal.
