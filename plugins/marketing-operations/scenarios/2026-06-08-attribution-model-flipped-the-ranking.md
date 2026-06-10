---
scenario_id: 2026-06-08-attribution-model-flipped-the-ranking
contributed_at: 2026-06-08
plugin: marketing-operations
product: channel-roi
product_version: "n/a"
scope: likely-general
tags: [attribution, channel-mix, marginal-roi, model-choice]
confidence: medium
reviewed: false
---

## Problem

A team defended a paid-search budget with a last-touch ROI report and wanted to cut content marketing as a poor performer. The risk: reporting a channel ROI without naming the attribution model is unreadable — last-touch systematically over-credits closing channels and under-credits the channels that opened the relationship (§3 #2).

## Context

- Motion: hybrid inbound + ABM.
- Constraint: first-touch, last-touch, and multi-touch credit channels differently and will rank them differently (§3 #2).
- The team reasoned from a single un-named model.

## Attempts

- Tried: **named the model and re-ran ROI under first-touch and multi-touch** (`marketingops_calc.py channel-roi`). Outcome: content marketing, near-zero under last-touch, was the top first-touch opener — the ranking flipped on model alone.
- Tried: **read marginal ROI on paid search** (§3 #5). Outcome: paid search had saturated — its average ROI was high but the marginal dollar had gone negative.
- Tried: **reconciled across models instead of trusting one** (§3 #2). Outcome: a defensible mix decision rather than a model artifact.

## Resolution

The response was to **keep content (the opener) and reallocate the saturated paid-search dollars to higher marginal-ROI channels** — not cut content. The output was the multi-model ROI comparison, the marginal-ROI read, and an explicit attribution-model statement.

**Action for the next consultant hitting this pattern:** **state the attribution model before any channel number, and read marginal not average ROI.** The model choice can flip the ranking, and a saturated channel's high average hides a negative marginal dollar. See Tree 2 and the `marketingops_calc.py` `channel-roi` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
