---
scenario_id: 2026-06-08-leads-up-pipeline-flat
contributed_at: 2026-06-08
plugin: marketing-operations
product: funnel
product_version: "n/a"
scope: likely-general
tags: [funnel, leaking-stage, lead-scoring, pipeline-contribution]
confidence: medium
reviewed: false
---

## Problem

A CMO celebrated a record lead quarter while sourced pipeline stayed flat, and the instinct was to buy more leads. The risk: lead and MQL counts are activity, not outcome; pouring volume into a funnel that leaks at MQL→SQL spends more to produce the same flat pipeline (§3 #1 #4).

## Context

- Motion: inbound-led B2B, mid-market.
- Constraint: the funnel is a system; the constraint is the worst-converting stage, and required volume back-solves through every stage (§3 #1).
- Leadership reasoned from the top-of-funnel count.

## Attempts

- Tried: **mapped stage conversion before buying volume** (`marketingops_calc.py funnel`). Outcome: lead→MQL looked healthy but MQL→SQL had collapsed — the leak was downstream of the spend.
- Tried: **validated the lead score against actual SQL conversion** (§3 #6). Outcome: the score's 'hot' band converted no better than 'warm' — the score was inflating MQLs without predicting conversion.
- Tried: **reframed the scorecard on sourced pipeline, not lead count** (§3 #4). Outcome: the flat pipeline was the real signal the lead count had masked.

## Resolution

The fix was a **re-scored, re-routed MQL definition tied to observed conversion** plus a hand-off SLA — **not** more lead spend. The output was the stage-conversion read, the scoring-validity finding, and the pipeline-contribution reframe.

**Action for the next consultant hitting this pattern:** **read the funnel as a system and fix the leaking stage before buying volume.** Lead count is activity; sourced pipeline is the outcome. Validate the lead score against actual conversion or it's noise. See Tree 1 and the `marketingops_calc.py` `funnel` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
