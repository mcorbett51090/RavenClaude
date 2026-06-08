---
scenario_id: 2026-06-08-missed-auto-renew-notice-window
contributed_at: 2026-06-08
plugin: legal-ops-clm
product: generic
product_version: "unknown"
scope: likely-general
tags: [renewals, auto-renew, notice-window, alerts, repository, obligations]
confidence: high
reviewed: false
---

> Not legal advice — an operational field note. A qualified lawyer owned the legal judgement throughout.

## Problem

A company got auto-renewed into a $180k/year SaaS contract it had already decided to drop. The contract auto-renewed for a 12-month term unless written notice was given 60 days before expiry. The team had the expiry date on a spreadsheet, but tracked only the expiry — not the 60-day notice window — so the reminder (set for the expiry month) fired three weeks after the window had already closed. They were locked in for another year.

## Constraints context

- ~250 active contracts across departments; renewals tracked in scattered spreadsheets and individual calendars.
- Many vendor contracts had auto-renew clauses with notice windows ranging from 30 to 90 days.
- No single owner per contract — the spreadsheet had a department, not a person.

## Attempts

- Tried: a shared "renewals" calendar with the expiry dates. Failed — the team kept reacting at expiry, which is too late when a 60-90 day notice window has already closed; an expiry reminder is structurally the wrong trigger.
- Tried: asking each department to "watch their own renewals." Failed — diffuse ownership meant everyone assumed someone else was watching; the next near-miss was a 90-day-notice contract.
- Tried: a repository with a metadata schema that captured, per contract, the auto-renew flag and the **notice-window deadline** (computed back from expiry), a **named owner** per contract, and tiered alerts at 90/60/30 days before the notice deadline. This worked.

## Resolution

Tracking the notice deadline instead of the expiry, plus a named owner and tiered early alerts, moved every renewal decision to *before* the window closed. The next two unwanted contracts were exited cleanly with notice given in time, and a wanted-but-overpriced one was renegotiated using the notice as leverage. The obligations register (built at the same time) also surfaced payment and SLA commitments that had previously gone untracked after signature.

## Lesson

Track the notice window, not just the expiry — an auto-renew fires unless notice lands inside the window, so the notice deadline is the actionable date. Give every contract a named owner and tier the alerts (90/60/30) so the renew/renegotiate/exit decision happens while there's still time. Signature is the start of the lifecycle, not the end. Not legal advice — a lawyer owned any interpretation of the notice terms.
