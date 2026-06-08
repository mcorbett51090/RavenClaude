---
scenario_id: 2026-06-08-tampering-with-a-stable-process
contributed_at: 2026-06-08
plugin: manufacturing-operations
product: spc
product_version: "unknown"
scope: likely-general
tags: [spc, control-chart, special-cause, common-cause, tampering, run-rules, capability]
confidence: high
reviewed: false
---

## Problem

A CNC machining cell had an experienced operator who "kept the process centered" by nudging the offset toward nominal on every part that drifted off-target. The fill dimension was technically in spec most of the time, but variation was high, scrap was creeping up, and the Cpk on the critical bore had quietly fallen below the customer's 1.33 floor — triggering a supplier-quality flag. The operator was proud of the constant adjustments; everyone assumed a more diligent operator would help, when the adjustments were the cause.

## Constraints context

- The "control chart" on the bore was drawn with the print's spec limits as its control limits — so any part trending toward a spec edge looked like an out-of-control point demanding a correction.
- The process was actually stable (common-cause variation only) when left alone; the per-part offset nudges were classic tampering, injecting variation into a process that had none to remove (the Deming funnel experiment, live on the floor).
- Capability (Cpk) was being reported on this over-adjusted, inflated-variation data, so the index looked worse than the untampered process actually was.

## Attempts

- Tried: assigning the "best" operator and writing a tighter adjustment work instruction. Failed — more diligent tampering is more variation, not less; scrap and the variation both rose.
- Tried: re-deriving the control limits from the process itself (X-bar/R from a stable baseline run with no adjustments), then applying the standard run rules instead of reacting to every spec-edge drift. This made the chart legible: most points were common-cause noise, not signals.
- Tried: a standing rule — do not adjust unless a run rule trips (point beyond 3-sigma, a run, a trend, a zone rule) — plus re-computing Cpk only on the now-stable process. This worked.

## Resolution

With control limits from the voice of the process (not the customer's spec), the operator stopped adjusting on noise. Variation dropped immediately because the tampering stopped; the bore Cpk recovered above 1.33 on stable data, clearing the supplier-quality flag. When a genuine special cause did appear later (a worn fixture), it stood out clearly against the stable limits and got a real investigation — the chart finally did its job because it was no longer drowned in tampering. The gauge-trust and capability-study rigor were routed to `applied-statistics`; this cell owned applying SPC and reading the chart.

## Lesson

Special cause vs common cause is the first SPC question — and the most expensive error is reacting to common-cause noise. Control limits come from the voice of the process, not the customer's spec; charting against spec limits invites tampering, which adds variation to a stable process. Don't adjust unless a run rule trips, and never report capability (Cpk) on tampered, inflated-variation data.
