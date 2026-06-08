---
scenario_id: 2026-06-08-hris-treated-as-a-spreadsheet
contributed_at: 2026-06-08
plugin: people-ops-hr
product: rippling
product_version: "unknown"
scope: likely-general
tags: [hris, data-hygiene, source-of-truth, payroll-seam, input-controls]
confidence: high
reviewed: false
---

## Problem

A company had an HRIS but treated it like a spreadsheet anyone could amend: managers kept their own side lists of team comp and titles, several employees existed twice (a duplicate created at a re-hire), level and location fields were free-text and inconsistent ("Sr.", "Senior", "SR" all live), and there were no input controls on who could change what. The breakage surfaced downstream: a payroll run picked up a stale location and withheld against the wrong jurisdiction, the benefits census was wrong because two records were duplicates, and a comp-band exercise stalled because nobody could trust the level field it depended on. The standing answer to "what's true?" was "depends which list you look at."

## Constraints context

- The HRIS was *nominally* the system of record, but nothing enforced that — manual edits and shadow spreadsheets drifted from it constantly.
- Payroll and benefits both read from the HRIS, so a drifted field there became a compliance and money problem, not just a tidiness one.
- Free-text fields (level, location, title) made any rollup or band mapping unreliable.

## Attempts

- Tried: a one-time cleanup pass (de-dupe, normalize) with no governance change. Failed — it drifted back within a quarter because the shadow spreadsheets and free-text inputs were still there.
- Tried: asking managers to "keep their lists in sync with the HRIS." Failed — two sources can't both be canonical; the lists immediately diverged again.
- Tried: declaring the HRIS the single canonical source, retiring the shadow lists, adding input controls (constrained pick-lists for level/location/title, restricted who can edit which fields, a re-hire dedupe check), and assigning a named data owner — then re-running payroll and the band exercise off the clean spine. This worked.

## Resolution

One canonical record with input controls and an owner meant payroll, the benefits census, and the comp-band work all read the same trustworthy data instead of competing lists. Constrained fields made level/location/title rollups reliable, which unblocked the band mapping. The mis-withholding that had already happened was routed to payroll/finance to correct and to counsel for any tax/compliance exposure — not self-adjudicated in HR.

## Lesson

The HRIS is the source of truth or it's nothing — one canonical record, input controls, a named owner; payroll and benefits depend on it, so a drifted field is worse than a missing one. A one-time cleanup without governance just drifts back; retire the shadow spreadsheets. Any tax/withholding-compliance fallout from the bad data goes to finance and counsel.
