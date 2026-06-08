---
scenario_id: 2026-06-08-forecast-on-padded-pipeline
contributed_at: 2026-06-08
plugin: revops
product: generic
product_version: "unknown"
scope: likely-general
tags: [forecast, coverage, pipeline-hygiene, win-rate, velocity, methodology]
confidence: high
reviewed: false
---

## Problem

A sales org missed its forecast by ~20% three quarters running, always to the downside. Leadership's response each quarter was "we need more pipeline — get to 3x coverage." Teams dutifully built to 3x, and the forecast still missed. The forecast itself was a rep-by-rep commit roll-up with no stated methodology; reps with "happy ears" inflated commit, and the CRM's default stage probabilities (10/25/50/75) bore no relation to how deals actually converted. Worse, a chunk of the "pipeline" was stuck deals weeks past their close date that nobody had closed-lost.

## Constraints context

- The real win-rate in their core segment was ~18%, not the 33% a 3x rule implicitly assumes — so 3x coverage was structurally short.
- Roughly 30% of open pipeline was past close date or had no activity in 60+ days — padding that inflated every aggregate.
- Reps were never asked for objective stage exit criteria; "stage 3" meant a different thing per rep.

## Attempts

- Tried: mandating 3x coverage harder. Failed — coverage on padded pipeline is precise nonsense; more padded pipeline didn't convert.
- Tried: switching wholesale to an AI forecast tool. Failed at first — fed the same dirty, mis-staged pipeline, it produced a confident wrong number; garbage in, confident garbage out.
- Tried: inspecting first (flagging and closing past-close-date/no-activity deals), re-deriving stage probabilities from actual historical conversion, switching to a weighted-by-stage forecast reported beside the commit roll-up with the gap named, and deriving coverage as gap ÷ the real 18% win-rate (~5.5x). This worked.

## Resolution

Inspection alone cut "pipeline" by ~30% — and the cleaned number was far more predictive. Re-derived stage probabilities replaced the CRM defaults. Reporting weighted and commit side by side exposed the happy-ears gap and made the conversation about evidence, not optimism. The honest coverage target (~5.5x, not 3x) showed they'd been structurally under-pipelined the whole time. The next two quarters' forecasts landed within tolerance, and a back-test against prior quarters confirmed the method reconstructed history.

## Lesson

Inspect the pipeline before the pipeline math — coverage, win-rate, and velocity on padded pipeline are precise nonsense. A forecast is a methodology with a named bias (report weighted and commit side by side), stage probabilities come from your own history not the CRM defaults, and coverage is derived from this segment's win-rate, never a hand-me-down 3x.
