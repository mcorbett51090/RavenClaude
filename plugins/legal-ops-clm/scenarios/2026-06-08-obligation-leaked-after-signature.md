---
scenario_id: 2026-06-08-obligation-leaked-after-signature
contributed_at: 2026-06-08
plugin: legal-ops-clm
product: generic
product_version: "unknown"
scope: likely-general
tags: [obligations, post-signature, sla, payment-terms, owner, ambiguity]
confidence: high
reviewed: false
---

> Not legal advice — an operational field note. A qualified lawyer owned the legal judgement throughout.

## Problem

A company signed a customer MSA with a service-credit SLA (99.9% uptime, credits owed if missed) and a contractual obligation to deliver a SOC 2 report annually and to notify the customer of any subprocessor change 30 days in advance. Nine months later the customer invoked a missed-SLA credit the company hadn't tracked, asked for the SOC 2 report nobody had queued, and flagged a subprocessor swap that had shipped with no notice. The deal team had treated signature as the finish line; the commitments inside the contract were never turned into tracked items, so they quietly leaked until the counterparty surfaced them.

## Constraints context

- The contract review was thorough at the redline stage — and then the file was closed at signature.
- Obligations lived only inside the PDF prose; nothing extracted them into a register with owners and triggers.
- One obligation ("notify of material changes promptly") had no defined timeframe — genuinely ambiguous.

## Attempts

- Tried: relying on the account owner to "remember the commitments." Failed — memory is not a tracking system; the account owner had changed once, and the recurring/annual obligations had no trigger to fire against, so they simply didn't.
- Tried: a flat checklist of obligations copied into a doc. Failed — a static list with no owner, no due-date/trigger, and no recurrence rule doesn't alert; the annual SOC 2 and the per-incident SLA credit need different handling (recurring vs. event-triggered), and the checklist captured neither.
- Tried: an obligations register — each commitment as a tracked item with a named owner, a trigger type (one-time / recurring / event-triggered), a due date or recurrence rule, and tiered alerts; the genuinely ambiguous "promptly" obligation flagged to the lawyer rather than assigned an invented deadline. This worked.

## Resolution

Extracting the commitments into a register with owners and triggers turned the contract from a closed file back into a live list. The annual SOC 2 obligation got a recurrence rule and an owner; the SLA-credit obligation became an event-triggered watch item tied to the uptime monitor; the subprocessor-notice obligation got a 30-day-advance trigger. The ambiguous "promptly notify" term went to the lawyer to pin down rather than being guessed at. The next renewal cycle, the company entered negotiations current on every commitment instead of being surprised by the counterparty.

## Lesson

Signature is the start of the lifecycle, not the end — a signed contract is a list of commitments, and each becomes a tracked item with a named owner and a trigger, or it leaks. Distinguish one-time, recurring, and event-triggered obligations; a flat checklist alerts no one. And when a due date or trigger is genuinely ambiguous, flag it for the lawyer — never invent a deadline (ambiguity-is-a-flag-not-a-guess). Not legal advice — a lawyer owned every interpretation of what an obligation required.
