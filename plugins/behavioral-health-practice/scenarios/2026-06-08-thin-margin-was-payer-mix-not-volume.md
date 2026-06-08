---
scenario_id: 2026-06-08-thin-margin-was-payer-mix-not-volume
contributed_at: 2026-06-08
plugin: behavioral-health-practice
product: payer-mix
product_version: "n/a"
scope: likely-general
tags: [payer-mix, reimbursement, margin, parity]
confidence: medium
reviewed: false
---

## Problem

An owner-clinician saw a full schedule but thin margin and assumed the practice needed more volume. The risk: a blended reimbursement number hides which payers drag margin — and adding volume on a payer that bills below variable cost deepens the loss (§3 #5).

## Context

- Setting: multi-payer outpatient practice.
- Constraint: margin is reimbursement net of variable cost, read by payer — a flush commercial book can mask a payer below cost (§3 #5).
- The owner reasoned from the blended number.

## Attempts

- Tried: **broke out reimbursement net of cost by payer** (`behavioral_health_practice_calc.py payer-mix`). Outcome: one payer's margin per visit was near zero or negative — invisible in the blend.
- Tried: **modeled a mix shift** toward higher-margin payers with capacity caveats. Outcome: the mix-shift delta beat raw volume growth on margin.
- Tried: **checked for a parity gap** where the behavioral rate lagged a medical-equivalent service, flagging it for counsel rather than ruling on it (§3 #5 #8). Outcome: a documented parity flag routed to counsel, not an in-team determination.

## Resolution

The response was a **per-payer margin read, a modeled mix shift, and a parity flag routed to counsel** — not a blanket volume push. The output was the per-payer margins, the blended figure, the mix-shift delta, and the routed parity question, with no PHI in the deliverable.

**Action for the next consultant hitting this pattern:** **read margin by payer before chasing volume, and flag parity to counsel.** A blended number hides a below-cost payer; the mix-shift delta usually beats raw volume, and the parity determination is counsel's, not the team's. See Tree 3 and the `model-payer-mix` skill.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
