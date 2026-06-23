---
scenario_id: 2026-06-14-green-status-hid-a-red-dependency
contributed_at: 2026-06-14
plugin: technical-program-management
product: status
product_version: "n/a"
scope: likely-general
tags: [status, dependency, critical-path, rollup, escalation, launch-slip]
confidence: medium
reviewed: false
---

## Situation

A four-team program to replace an internal billing platform reported "green" for
six straight weekly status updates. The status template averaged each
workstream's RAG color, and three of four teams were genuinely on track, so the
rollup came out green. In week seven the program slipped a month: the payments
team's API — the one deliverable the ledger and notifications teams both consumed
— had been quietly yellow-then-red for three weeks, but it averaged out.

## Constraints

- The TPM had no authority over the payments team's roadmap; influence only.
- The status went to an exec who skimmed the top line and trusted the color.
- The dependency was on the critical path; everything else had weeks of slack.

## What we tried

1. Kept sending the averaged-RAG status — green, green, green — because three of
   four teams really were fine.
2. Tracked the payments API slip in the RAID log, but as one yellow row among many
   and never surfaced to the top of the status.
3. Assumed the payments lead would "handle it" rather than escalating.

## Resolution

The fix, applied too late but kept for every program after: **roll up the worst
critical-path dependency, not the average**, and **lead the status with the
decision needed**. The next program's status opened each week with "the change in
the critical path" — the first time a critical-path dependency went yellow, the
status went yellow and the top line read "decision needed: re-sequence or add a
contractor to payments by Friday, or we slip three weeks." The exec made the call
the same day. The dependency never reached red.

## Lesson

A green status with a red dependency is a lie the math tells you. The rollup must
follow the critical path, not the arithmetic mean — and the status must lead with
the decision the worst dependency forces, framed as a dated ask to a named owner.
Escalating that early is the job, not a failure.
