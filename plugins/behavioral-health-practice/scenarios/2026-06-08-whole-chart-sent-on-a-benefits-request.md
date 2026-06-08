---
scenario_id: 2026-06-08-whole-chart-sent-on-a-benefits-request
contributed_at: 2026-06-08
plugin: behavioral-health-practice
product: generic
product_version: "unknown"
scope: likely-general
tags: [minimum-necessary, disclosure, roi, consent, records-request, privacy]
confidence: high
reviewed: false
---

## Problem

A payer requested documentation to support a prior-authorization decision. The practice had a valid authorization on file from the client, so staff exported and sent the client's *entire* chart — every session note going back years — to satisfy the request. The consent was valid, but the disclosure scope wasn't: the payer needed the diagnosis and medical-necessity support, not the full session-by-session narrative, and the over-send was itself a privacy failure.

## Constraints context

- The mental model on the floor was "a valid consent means we can send the chart" — true for *whether* we can disclose, silent on *how much*.
- The EHR's easy button was "export full chart"; a scoped export (specific records, date range) took more steps, so nobody used it.
- Part of the chart contained content unrelated to the auth decision, and a portion was SUD content that should never have left on the general authorization at all.

## Attempts

- Tried: sending the whole chart on the valid consent (the original move). Wrong — a valid consent authorizes the *needed* scope for the stated purpose, not everything.
- Tried: redacting by hand after the fact. Late and error-prone — the over-disclosure had already occurred, and manual redaction missed items.
- Tried: scoping the disclosure up front to exactly what the purpose required (diagnosis + medical-necessity support for the auth), excluding unrelated content, and routing the SUD content through its own specific Part 2 consent. This was the correct path.

## Resolution

The disclosure was scoped to the minimum necessary for the stated purpose — the auth decision needed the necessity story, not the whole history. Unrelated content stayed out; the SUD content was handled under its own specific Part 2 consent with the redisclosure-prohibition notice. The principle held: a valid consent answers *whether*, minimum-necessary answers *how much*. No real PHI appeared in the rewritten disclosure checklist — it used `[Client]` / `[Recipient]` / `[Date range]` placeholders — and any question about what the clinical content meant went to the clinician.

## Lesson

A valid consent on file is not a license to send everything — minimum necessary is the default disclosure scope, tightened further for 42 CFR Part 2 SUD content. Send only the records, date range, and content the purpose requires; when unsure, send less and offer more on a follow-up request. Over-disclosure on a valid consent is still a privacy failure.
