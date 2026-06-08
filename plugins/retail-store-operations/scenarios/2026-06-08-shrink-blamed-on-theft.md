---
scenario_id: 2026-06-08-shrink-blamed-on-theft
contributed_at: 2026-06-08
plugin: retail-store-operations
product: pos
product_version: "unknown"
scope: likely-general
tags: [shrink, loss-prevention, receiving, operational, diagnosis]
confidence: high
reviewed: false
---

## Problem

A mid-size chain saw shrink climb to roughly 2.3% of sales at a cluster of stores and reflexively treated it as a theft problem — it approved a capital request for additional camera coverage and an LP staffing bump. Two quarters and a meaningful spend later, shrink at those stores had barely moved. The book-vs-physical gap was real, but the money had gone to the wrong leak.

## Constraints context

- Shrink was reported only as a single blended % of sales — no split by source.
- Receiving was high-volume and understaffed at the affected stores; markdowns were executed manually at the register.
- LP budget was the easiest line to grow; "shrink = theft" was the default assumption nobody had tested.

## Attempts

- Tried: more cameras and LP hours on the assumption it was theft. Failed to move the number — the gap wasn't concentrated in high-value, easily-concealed SKUs the way a theft pattern would be; it was spread across categories.
- Tried: reconciling receiving counts, markdown execution, and damage logs against the book gap. This surfaced it — receiving discrepancies and un-keyed / mis-keyed markdowns accounted for the majority of the gap. The leak was operational, not theft.
- Tried: tightening the receiving-count SOP, moving markdown execution to a scanned/system-enforced step, and a vendor-claim process for short ships. The operational fixes were near-zero cost and closed most of the gap; a residual, genuinely-concentrated slice was then handed to LP — where the cameras actually fit the pattern.

## Resolution

The team split shrink into its three buckets — operational (receiving / markdown / damage), theft (internal / external), and vendor/admin (short ships, price/scan error) — and sized each before prescribing a control. Operational was the dominant leak, fixed with SOP discipline, not capital. Only the concentrated residual went to loss-prevention. Employee-surveillance and PII content was routed to the security-reviewer before anything touched staff monitoring.

## Lesson

Shrink is a diagnosable leak, not a fixed cost and not automatically theft. Split the gap into operational vs. theft vs. vendor/admin and size each bucket before spending — most shrink is operational, and cameras are the wrong (and expensive) fix for a receiving or markdown-execution error. Quantify, then control.
