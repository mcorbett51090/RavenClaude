---
scenario_id: 2026-06-05-iep-fill-gap-redeployment-and-teletherapy
contributed_at: 2026-06-05
plugin: staffing-operations
product: education-segment
product_version: "n/a"
scope: segment-specific
tags: [iep, idea-compliance, school-based, redeployment, teletherapy]
confidence: medium
reviewed: false
---

## Problem

A school-based therapy division showed a **Q4 calendar-quarter "fill rate" of ~84% that read as a decline**, and a district client was escalating about **unfilled SLP/OT positions leaving IEP-mandated service minutes undelivered** — a FAPE/compensatory-services liability, not just a vacancy. Leadership was about to treat both as a recruiting-throughput problem and push for more sourcing headcount into a quiet hiring window. Two different errors were stacked: a seasonality artifact in the fill number, and an unfilled-mandate problem that needed a delivery-model fix, not raw headcount.

## Context

- Segment: education / school-based (special ed, SLP/OT/PT, school psych), IDEA/IEP mandated-service delivery, academic-calendar hiring cycle.
- Constraint: the fill rate was being read on a **calendar quarter** that crossed the academic-calendar seasonal boundary (CLAUDE.md §3 #5). Schools hire in spring/summer for a fall start and go quiet at year-end — so a Q4 calendar-quarter cut understates fill by construction.
- The unfilled positions were genuine, hard-to-source onsite roles in a region with a thin therapist supply; onsite time-to-fill ran into months, but the IEP minutes were due now regardless.

## Attempts

- Tried: **re-cut fill rate YoY same-period / cycle-aligned** instead of calendar-quarter (§3 #5). Outcome: cycle-aligned fill was actually healthy (~84% vs ~80% prior-year same period) — the "decline" was a seasonality artifact, removing the false urgency to over-hire into a quiet window.
- Tried: separated the **genuine** unfilled-mandate gap from the artifact. For the real onsite gaps, checked the cheapest lever first — **redeployment** (the cheapest placement; §3 #16) of existing clinicians and **teletherapy** as a delivery model that launches in days where onsite takes months. Outcome: teletherapy + redeployment covered the at-risk IEP minutes far faster than a new onsite hire could, addressing the compensatory-services exposure on the clock that matters (service minutes, not headcount).
- Tried: framed the unfilled-mandate metric as a **first-class compliance KPI** (IEP minutes delivered vs. contracted, missed-session rate) rather than a back-office number, since an undelivered service hour is a failed placement and a liability (§3 #8). Outcome: the readout led with the compliance exposure, which is what the district actually escalates on.

## Resolution

The diagnosis separated into "the fill-rate decline is a **calendar artifact** — re-cut cycle-aligned" and "the IEP gap is **real but a delivery-model problem** — close it with teletherapy + redeployment, not a slow onsite hire into a quiet window." The recommendation made IEP-minutes-delivered-vs-contracted and missed-session rate first-class scorecard tiles, and routed the at-risk minutes to teletherapy/redeployment for speed. FAPE/compensatory-services determinations were flagged as the district's / its counsel's call, not advised on directly (§2).

**Action for the next consultant hitting this pattern:** in school-based work, **align fill rate to the academic cycle, never the calendar quarter** (§3 #5) before reading a decline, and treat an **unfilled IEP-mandated service as a compliance KPI, not a vacancy** (§3 #8) — close it with the fastest delivery lever (teletherapy, redeployment; §3 #16) rather than a months-long onsite hire. See [`../knowledge/education-staffing-fundamentals.md`](../knowledge/education-staffing-fundamentals.md), [`../knowledge/staffing-decision-trees.md`](../knowledge/staffing-decision-trees.md) "Fill rate has declined" (step 1 seasonality), and [`../best-practices/idea-compliance-is-a-fill-rate-kpi-not-a-legal-department-issue.md`](../best-practices/idea-compliance-is-a-fill-rate-kpi-not-a-legal-department-issue.md). The [`../scripts/staffing_calc.py`](../scripts/staffing_calc.py) `fill-rate` mode shows how the cycle-aligned vs. calendar-quarter denominator changes the number.

**Sources (retrieved 2026-06-05):**
- Academic-calendar seasonality, IDEA/IEP mandated-service delivery, teletherapy, redeployment: [`../knowledge/education-staffing-fundamentals.md`](../knowledge/education-staffing-fundamentals.md)
- Redeployment as the cheapest placement: [`../knowledge/staffing-kpi-glossary.md`](../knowledge/staffing-kpi-glossary.md) §C.16

Fill-rate figures are illustrative `[ESTIMATE]`. FAPE/compensatory-services and IDEA legal determinations are out of scope (§2) — flag, don't advise. Teletherapy delivery rules vary by state and district — `[verify-at-use]`.
