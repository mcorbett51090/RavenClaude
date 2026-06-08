---
scenario_id: 2026-06-08-part-2-record-disclosed-on-a-general-roi
contributed_at: 2026-06-08
plugin: behavioral-health-practice
product: generic
product_version: "unknown"
scope: likely-general
tags: [42-cfr-part-2, roi, consent, disclosure, sud, hipaa]
confidence: high
reviewed: false
---

## Problem

A practice's front desk received a records request: a client was transferring to another provider and signed a standard release-of-information (ROI) form authorizing the practice to send their chart. The chart included notes from substance-use-disorder (SUD) treatment. Staff were about to send the full record on the strength of the general HIPAA authorization — which would have been an improper disclosure of 42 CFR Part 2-protected content.

## Constraints context

- The practice ran a Part 2-covered SUD program alongside general behavioral health, and the two record types lived in one chart.
- The intake ROI form was a generic HIPAA authorization — it did not name a recipient and purpose specifically enough for Part 2, and it carried no redisclosure-prohibition language.
- Front desk's mental model was "a signed ROI means we can send the chart" — true for general PHI, not for Part 2 SUD content.

## Attempts

- Tried: treating the signed general ROI as sufficient (the original plan). Wrong — Part 2 SUD content needs *specific* written consent naming the recipient and purpose; a general HIPAA authorization does not cover it.
- Tried: redacting all SUD content and sending the rest. Workable for the non-SUD portion, but it left the receiving provider without the SUD history the client actually wanted transferred.
- Tried: obtaining a specific Part 2 consent for the SUD content (naming the recipient + purpose, with the redisclosure-prohibition notice), then disclosing the minimum necessary to that recipient. This was the correct path.

## Resolution

The disclosure waited until the specific Part 2 consent was on file — consent precedes disclosure, every time. When unsure whether a given note was Part 2-covered, staff treated it as covered (the conservative default). The intake ROI form was revised so a specific Part 2 consent could be captured up front when relevant. The clinical content of what was disclosed (what the notes *meant*) was left to the clinician; this was a consent/operations call, not a clinical one. No real PHI appeared in any process artifact — the rewritten checklist used `[Client]` / `[Recipient]` placeholders.

## Lesson

42 CFR Part 2 is stricter than HIPAA — a general ROI does not authorize disclosing SUD content; that needs specific written consent naming the recipient and purpose. When unsure a record is Part 2-covered, assume it is, and never let a record leave without verifying the right consent is on file. Route the clinical-content questions to a clinician and the legal questions to counsel.
