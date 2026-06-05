---
scenario_id: 2026-06-05-credentialing-clock-hidden-in-time-to-fill
contributed_at: 2026-06-05
plugin: staffing-operations
product: healthcare-segment
product_version: "n/a"
scope: likely-general
tags: [credentialing, time-to-start, fall-off, healthcare, compliance]
confidence: medium
reviewed: false
---

## Problem

A division reported a fast, competitive **time-to-fill of ~9 days (req-open to offer-accept)** and a rising **fall-off rate (~8%, placements canceling before or just after start)**. Leadership read these as two unrelated metrics — "recruiting is fast" and "candidates are flaky" — and was about to launch a candidate-engagement program to fix the fall-off. The two numbers were actually the same problem: the firm was measuring the clock to *accept* and ignoring the credentialing/clearance stage between accept and start.

## Context

- Segment: healthcare (travel + allied), Joint-Commission-credentialed facility placements.
- Constraint: time-to-fill was measured to **offer-accept**, not to **start** (CLAUDE.md §3 #7). The ~21 days of licensure verification, primary-source verification, background, and facility documentation after accept were invisible in the headline metric — so a 9-day "fill" was really a ~30-day time-to-start.
- The fall-off was concentrated at the **accept→start** funnel stage, the signature of credentialing/clearance fallout (the dominant fall-off cause in credentialed healthcare work).

## Attempts

- Tried: **re-defined time-to-fill to time-to-start** (§3 #7) — accept-to-start credentialing days folded into the clock. Outcome: the "9-day" fill became a ~30-day time-to-start, and the firm's true competitiveness vs. a faster-credentialing competitor was suddenly visible (and worse than believed).
- Tried: **decomposed the accept→start stage** to see where the 21 days went — licensure/PSV turnaround, background, facility-specific documentation. Outcome: the bulk was a serial (not parallel) document-collection process and a licensure-verification queue, both compressible.
- Tried: **linked fall-off to the credentialing clock** rather than treating it as candidate flakiness — a candidate who accepts and then waits three weeks for clearance is a candidate a faster competitor poaches mid-credentialing. Outcome: reframed the fall-off fix from "engage candidates more" to "shorten and parallelize the clearance pipeline."

## Resolution

The two metrics collapsed into one root cause: **the credentialing clock was both lengthening the real fill time and driving the fall-off.** The recommendation was to measure time-to-start as the headline (with time-to-accept as a sub-metric), parallelize the document-collection workstream, and start a pre-clearance bench for the recurring credential profiles — attacking fill speed and fall-off with a single lever. Specific licensure/Joint-Commission requirements were flagged as the client's compliance counsel's domain, not advised on directly (§2).

**Action for the next consultant hitting this pattern:** **measure the whole clock — time-to-*start*, not time-to-accept** (§3 #7). A fast accept that then sits in credentialing is a slow fill wearing a disguise, and a high accept→start fall-off is almost always the credentialing clock, not candidate flakiness. Fix them together by shortening/parallelizing the clearance pipeline. See [`../knowledge/credentialing-and-compliance.md`](../knowledge/credentialing-and-compliance.md), [`../knowledge/staffing-decision-trees.md`](../knowledge/staffing-decision-trees.md) "Aged-order pileup" (step 2 credentialing bottleneck), and [`../best-practices/measure-the-credentialing-clock-as-part-of-time-to-fill.md`](../best-practices/measure-the-credentialing-clock-as-part-of-time-to-fill.md). The [`../scripts/staffing_calc.py`](../scripts/staffing_calc.py) `funnel-leak` mode will surface the accept→start stage when its conversion is the worst in the chain.

**Sources (retrieved 2026-06-05):**
- Time-to-present vs. time-to-start (the gap is the credentialing clock) + fall-off as accept→start fallout: [`../knowledge/staffing-kpi-glossary.md`](../knowledge/staffing-kpi-glossary.md) §A.2, §C.19, §E.28
- Credentialing stages as time-to-fill components: [`../knowledge/credentialing-and-compliance.md`](../knowledge/credentialing-and-compliance.md)

Credentialing-day estimates (~21 days) are illustrative `[ESTIMATE]` and vary widely by state licensure compact status, facility, and specialty — `[verify-at-use]` against the client's own accept→start data (§3 #7, §3 #9).
