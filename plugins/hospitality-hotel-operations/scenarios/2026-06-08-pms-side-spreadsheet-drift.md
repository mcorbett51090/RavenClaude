---
scenario_id: 2026-06-08-pms-side-spreadsheet-drift
contributed_at: 2026-06-08
plugin: hospitality-hotel-operations
product: mews
product_version: "unknown"
scope: likely-general
tags: [pms, room-status, housekeeping, front-office, sop, double-sold]
confidence: high
reviewed: false
---

## Problem

A 90-room boutique hotel ran its room-status flow off a shared Google Sheet because "the PMS housekeeping board was clunky." Housekeepers marked rooms clean in the sheet, the front desk checked the sheet at arrival, and the PMS room status lagged behind both. One busy afternoon the sheet showed a room ready that the PMS — and reality — said was still occupied by a late check-out; the desk assigned it, walked a family up to a door that opened on someone else's belongings, and the same week a different mismatch double-sold a room on the PMS while the sheet showed it open.

## Constraints context

- Two systems claimed to be the truth: the PMS (which fed the channel manager and the OTAs) and the side spreadsheet (which the staff actually trusted). When they disagreed, nobody knew which to believe.
- The spreadsheet had no link to the channel manager, so availability the OTAs saw was driven by the PMS while the desk worked off the sheet — guaranteeing the two would drift.
- The original complaint — "the PMS housekeeping board is clunky" — was real, but the fix had become a parallel truth instead of a configuration change at the PMS.

## Attempts

- Tried: telling staff to "keep both in sync." Failed — manual double-entry drifts the moment one person is busy; within a day the sheet and the PMS disagreed again.
- Tried: making the spreadsheet the master and updating the PMS from it nightly. Failed — the PMS feeds the channel manager in real time, so a nightly catch-up still let the OTAs oversell against stale availability during the day.
- Tried: killing the side spreadsheet and fixing the actual friction at the PMS — enabling the mobile housekeeping app so room status updates at the source, configuring the room-status board the team had found clunky, and writing an SOP that the PMS is the single system of record. This worked.

## Resolution

Once housekeepers updated status in the PMS mobile app at the door and the front desk read room status from the PMS, the two-truth problem disappeared and the channel manager stopped overselling against stale availability. The "clunky board" complaint was solved by configuration, not by a parallel system. Double-sells and wrong-room walk-ups stopped; the test "when they disagree, which does the desk trust at 11pm?" now had one answer — the PMS.

## Lesson

The PMS is the single system of record for room status, rate, folio, and profile — a side spreadsheet drifts the moment two people touch it and burns the guest at the worst moment. When a process needs something the PMS doesn't do well, fix it at the PMS (configuration, the mobile app, an integration), never by maintaining a parallel truth no other system reads. If the PMS and a spreadsheet disagree and the answer is ever "trust the spreadsheet," the workflow is already broken.
