---
scenario_id: 2026-06-08-submittal-surfaced-the-week-of-install
contributed_at: 2026-06-08
plugin: construction-field-management
product: generic
product_version: "unknown"
scope: likely-general
tags: [submittals, lead-time, schedule, document-control, ball-in-court]
confidence: high
reviewed: false
---

## Problem

The submittal log tracked status (sent / in review / approved) but had no required-by dates tied to the install schedule. The week the team needed to install the structural steel, they discovered the connection-detail submittal was still in "revise and resubmit" — it had bounced once, sat with the detailer for three weeks, and nobody noticed because there was no date saying when it had to be approved. The steel erection slipped a month, cascading into the trades behind it.

## Constraints context

- ~12-week fabrication lead time on the steel; a 2-week review cycle that had already bounced once.
- The submittal register was a flat status list with no ball-in-court owner and no required-by date.
- Separately, the detailer had been working off a superseded structural sheet because an ASI revising the connection had never been transmitted to them.

## Attempts

- Tried: expediting fabrication once the block was discovered. Failed — the lead time was real; no amount of pushing recovered 12 weeks of fab in the week of install.
- Tried: a weekly submittal status meeting. Helped visibility but still reacted to "in review" without knowing which items were *late* against the schedule.
- Tried: rebuilding the register with required-by = install date − lead time − review time computed for every item, ball-in-court on each, and a flag on any item whose required-by had already passed; plus reconciling the current drawing set and transmitting the open ASIs so the detailer worked off the right sheet. This worked.

## Resolution

Back-calculating required-by dates turned the register from a status list into an early-warning system: items whose review window was already too tight surfaced weeks ahead, while there was still time to expedite review or re-sequence. The ball-in-court field made it obvious who owed the next action on each. Fixing document control (transmitting the ASI) stopped the detailer from resubmitting against a superseded sheet, which had caused the first bounce. The next long-lead package was approved with two weeks of float instead of being discovered late.

## Lesson

Schedule submittals backward from the install date — required-by = need-by − lead time − review time — and flag anything already past its required-by as a schedule risk now, not the week of install. Pair it with document control: a detailer working off a superseded sheet will bounce, so transmit the ASIs and keep the field on one current set.
