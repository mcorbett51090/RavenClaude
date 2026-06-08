---
scenario_id: 2026-06-08-pipeline-coverage-looked-fine-aggregate
contributed_at: 2026-06-08
plugin: sales-revops
product: pipeline
product_version: "n/a"
scope: likely-general
tags: [coverage, forecast, segmentation, pipeline-creation]
confidence: medium
reviewed: false
---

## Problem

A CRO saw 3.8x aggregate pipeline coverage and told the board the quarter was safe. The risk: an aggregate coverage ratio blends a flush SMB segment with a starved enterprise segment; the number that matters is coverage *where the quota actually is*, and a healthy total can mask a segment that will miss badly (§3 #1).

## Context

- Motion: hybrid SMB + enterprise; most quota dollars sit in enterprise.
- Constraint: coverage is a ratio against quota, and required coverage ≈ 1 ÷ win-rate — which differs sharply by segment (§3 #1).
- The CRO reasoned from one blended number.

## Attempts

- Tried: **segmented coverage before trusting the aggregate** (`revops_calc.py coverage`). Outcome: SMB sat at 6x while enterprise sat at 1.9x against a ~4x need — the bulk of the quota was badly under-covered.
- Tried: **checked pipeline-creation trend by segment.** Outcome: enterprise pipeline creation had stalled two quarters running — a leading indicator the aggregate hid (§3 #5).
- Tried: **back-solved required coverage from each segment's win-rate.** Outcome: enterprise needed more coverage *and* more time than the quarter had.

## Resolution

The fix was a **segment-targeted enterprise pipeline-generation push** plus a realistic re-forecast of the enterprise number — **not** a confident board commit on the blended ratio. The output was a segmented coverage read, the creation trend, and the dollar gap per segment.

**Action for the next consultant hitting this pattern:** **segment coverage before you commit a forecast.** A blended coverage ratio is the most reassuring and least informative number in the deck; read it where the quota lives and back-solve the required ratio from each segment's win-rate. See Tree 1 and the `revops_calc.py` `coverage` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
