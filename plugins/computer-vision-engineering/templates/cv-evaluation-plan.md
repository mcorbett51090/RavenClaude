# CV Evaluation Plan — <project / model / date>

> Output template for the metric-to-decision map, the eval dataset, and the operating-point plan. One per model/task. Every metric/threshold cell carries a source + date or `[verify-at-use]`; evaluate on production-like data; no PII, no image data stored.

## Header
- **Project / model / task:** _____
- **The decision the metric must inform:** _____
- **Prepared:** 2026-__-__  · **Owner:** _____

## 1. Metric-to-decision map
| Item | Value | Flag |
|---|---|---|
| Primary metric (mAP / IoU / precision-recall / F1) | | _[verify-at-use]_ |
| Cost of a false negative vs false positive | | drives the operating point |
| Operating point (threshold / recall floor / max FP rate) | | _[verify-at-use]_ |
| Acceptance criterion (pass/fail bar) | | the "done" definition |

## 2. Eval dataset
| Item | Value | Flag |
|---|---|---|
| Source (production-like? cameras / lighting / distribution) | | in-the-wild, not just a clean split |
| Size + class balance | | rare classes represented? |
| Slices to report separately | | per-class / per-condition |
| Leakage check | | no train/test overlap | 

## 3. Results (per-slice, not just average)
| Slice | Metric | vs operating point | vs previous model | Flag |
|---|---|---|---|---|
| Overall | | | | |
| Rare / hard class | | | | |
| Condition A (e.g. low light) | | | | _[ESTIMATE]_ |
| Regression suite | | no key slice worse | | |

## 4. Post-optimization & drift
- **Accuracy after quantization/export (vs operating point):** _____
- **Drift monitoring plan (signal + alarm):** _____
- **Re-label / active-learning trigger:** _____

## Headline + actions
- **Headline:** _does it clear the operating point on production-like data?_
- **Top 2 actions:** _action — owner — expected metric movement — by when_
- **In-the-wild note:** _how far is the eval set from real production?_

---
_Plus the ravenclaude-core Structured Output block. Evaluate in the wild, per-slice; re-check accuracy after optimization. Seams: cv-systems-architect (metric/operating point), vision-deployment-engineer (post-optimization accuracy)._
