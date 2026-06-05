---
scenario_id: 2026-06-05-hygiene-recall-reactivation
contributed_at: 2026-06-05
plugin: dental-practice
product: hygiene
product_version: "n/a"
scope: likely-general
tags: [hygiene, recall, reappointment, reactivation, unscheduled-treatment]
confidence: medium
reviewed: false
---

## Problem

A general practice's hygiene schedule had soft spots — open columns most afternoons — and the owner's reflex was to "do some marketing" to find new patients. But the active-patient count was healthy; the practice was *losing the patients it already had* out the back door. The real leak was a recall/reappointment failure: patients finished a hygiene visit and walked out **without** the next one booked, then drifted past due.

## Context

- Segment: general-practice, independent, 1 doctor + 2 hygienists, PPO-heavy.
- Constraint: the front desk "called to reschedule later" instead of pre-booking the next recall before the patient left the chair — the single highest-leverage habit in hygiene retention.
- The owner was about to spend on new-patient acquisition (the most expensive growth lever) to fill a schedule that was leaking retained patients (the cheapest to keep).

## Attempts

- Tried: measured the **hygiene reappointment rate** (% of hygiene patients who leave with the next recall booked) before any marketing spend. Found it sitting near the typical-practice level of ~50%, well under the 85–90%+ target the recall literature cites [verify-at-use]. Outcome: confirmed the leak was retention, not demand — reframed the whole engagement away from acquisition.
- Tried: pulled the **unscheduled-active-patient** and overdue-recall lists from the PMS (patients with no future appointment) and sized the recoverable book. Outcome: quantified a large reactivation pool already in the practice's own database — no ad spend required.
- Tried (the move that worked): instituted **pre-book-before-they-leave** as the default (book the next recall from the chair, not "we'll call you"), plus a structured reactivation campaign against the overdue list, plus tracking reappointment rate weekly on the scorecard. Outcome: reappointment rate climbed toward the 70%+ top-performer band and the soft afternoon columns filled from the existing patient base.

## Resolution

The fix was **retention, not acquisition** — pre-booking the next recall before the patient leaves the chair and working the overdue list, tracked as a first-class weekly metric. Hygiene is a profit engine, and an under-booked hygiene schedule is unbooked margin the practice already paid to acquire (CLAUDE.md §3 #5). New-patient marketing was deferred until the back-door leak was closed.

**Action for the next consultant hitting this pattern:** before recommending new-patient marketing for a soft hygiene schedule, **measure the reappointment rate and size the overdue-recall pool first.** A ~50% reappointment rate against an 85–90% target means the cheapest fill is the patients you already have. Pre-book from the chair; track reappointment weekly. Cross-reference [`../skills/protect-the-collection-ratio/SKILL.md`](../skills/protect-the-collection-ratio/SKILL.md) for the production side and [`../knowledge/dental-kpi-glossary.md`](../knowledge/dental-kpi-glossary.md) for the recall/reappointment definitions.

**Sources (retrieved 2026-06-05):**
- Dental Intelligence (Dental Intel) — Performance Board: Hygiene Re-Appointment (typical ~50% vs top-performer ~70%): https://learn.dentalintel.com/en/articles/6070096-performance-board-hygiene-re-appointment
- Adams Brown CPA — Top KPIs to track (hygiene reappointment, recall targets): https://www.adamsbrowncpa.com/blog/top-6-kpis-to-track-in-your-dental-practice/
- Dentx — 10 Dental KPIs with 2026 benchmarks (recall reappointment 90%+ target): https://dentx.ca/dental-kpi/

Reappointment/recall targets are trade-source rules-of-thumb, not hard rules — treat as `[verify-at-use]` and calibrate to the practice's segment and patient base (§3 #8).
