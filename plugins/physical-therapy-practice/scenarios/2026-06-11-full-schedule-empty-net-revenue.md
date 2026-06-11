---
scenario_id: 2026-06-11-full-schedule-empty-net-revenue
contributed_at: 2026-06-11
plugin: physical-therapy-practice
product: clinic-pl
product_version: "n/a"
scope: likely-general
tags: [reimbursed-visits, denials, cancellations, payer-mix, net-collection]
confidence: medium
reviewed: false
---

## Problem

A clinic had its busiest quarter by booked appointments and still missed budget. The risk: a full
appointment book is not full revenue — cancellations, no-shows, and denials sit between booking and
collection, and the clinic was managing to booked visits, not reimbursed ones.

## Context

- Surface: the P&L, built on booked-visit volume and gross fee schedule.
- Constraint: the revenue unit is the reimbursed visit (delivered, documented, coded, collected).
- The team celebrated schedule density without watching net collection per delivered visit.

## Attempts

- Tried: **rebuilt the P&L from reimbursed-visit economics** via `pt_calc.py
  net_collection_per_visit`, `cancellation_rate`, and `clinic_contribution_margin`. Outcome: an 11%
  cancellation/no-show rate and a denial cluster were quietly removing a fifth of the booked volume.
- Tried: **analyzed payer mix by net collection AND admin burden**. Outcome: the highest gross-fee
  payer also had the worst denial rate — a low *net* collector once rework was counted.
- Tried: **traced the denials to origin** (intake auth + unrecorded minutes) and the cancellations to
  mid-episode "felt better" dropout. Outcome: source fixes, not back-end appeals.

## Resolution

The fix was to **manage to reimbursed visits and net collection per visit, re-rank payer mix by net
not gross, and fix denials and cancellations at their source** — not to add more bookings. The output
was the reimbursed-visit P&L, the payer-mix re-ranking, and the source fixes.

**Action for the next consultant hitting this pattern:** **a busy book is not full revenue — start
the P&L from reimbursed visits.** See `best-practices/count-reimbursed-visits-not-booked-visits.md`,
`best-practices/denials-are-prevented-at-the-source.md`, and
`knowledge/referral-and-revenue-cycle-reference.md`.
