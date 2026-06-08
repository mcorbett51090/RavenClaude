---
scenario_id: 2026-06-08-last-touch-defunds-demand
contributed_at: 2026-06-08
plugin: revops
product: generic
product_version: "unknown"
scope: likely-general
tags: [attribution, budget, demand-gen, multi-touch, last-touch, lens]
confidence: high
reviewed: false
---

## Problem

A marketing org ran every channel-ROI report on last-touch attribution because it was the CRM's default and "felt objective." Last-touch credited the final converting touch — almost always a branded-search click or a sales-booked demo — so paid-search and SDR outreach looked like the only things that worked. Leadership cut the top-of-funnel demand programs (content, events, brand) that last-touch gave zero credit to. Two quarters later branded-search volume itself fell off a cliff: the demand that *fed* those bottom-funnel touches had been defunded, and nobody connected the two because the model that drove the budget couldn't see it.

## Constraints context

- The CRM shipped last-touch as the out-of-the-box model and finance treated its numbers as ground truth, not as one opinionated lens.
- No multi-touch data existed at first — touchpoints weren't being captured beyond the final one, so even building a different model meant instrumenting touch capture first.
- Stakeholders distrusted any "black box" — an algorithmic data-driven model would have been rejected as un-auditable even if the data had supported it.

## Attempts

- Tried: switching wholesale to first-touch. Failed the other way — it over-credited demand creation and defunded the closing/sales-assist touches, so the same one-model-drives-budget mistake just inverted. One lens is still one lens.
- Tried: jumping straight to an algorithmic data-driven model. Failed — not enough touch volume or clean multi-touch data yet, and stakeholders wouldn't trust an unexplainable number.
- Tried: instrumenting full touch capture, standing up a W-shaped (position-based) heuristic *beside* last-touch, and reporting the two side by side with each model's distortion named. Treating the divergence between models as the signal — not crowning one truth — worked.

## Resolution

W-shaped reporting restored visible credit to the lead-creating and opp-creating touches the demand programs drove, while last-touch stayed in view for the closing lens. Naming each model's known distortion (last-touch defunds demand; first-touch ignores closing; the heuristic weighting is opinionated, not truth) reframed the budget conversation from "which model is right" to "what does each tell us." The defunded demand programs were restored before the branded-search erosion compounded, and budget decisions started triangulating across models instead of letting one silently drive the spend.

## Lesson

Attribution is a chosen lens, never ground truth — and the CRM default (usually last-touch) is the most dangerous lens precisely because it looks objective. Never let one model silently drive budget: name what each under/over-credits, report at least two side by side, and treat the divergence between them as a signal rather than noise. A model you can't explain to finance won't survive contact with a budget cut, no matter how good its math.
