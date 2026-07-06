---
description: "Build the metric-to-decision map for a vision model — choose the metric and operating point that mirror the cost, design a production-like eval dataset with per-slice reporting and a regression suite, and plan drift + post-optimization accuracy checks (metric/threshold specifics verify-at-use)."
argument-hint: "[task + the decision the metric must inform + the data/cameras you can evaluate on]"
---

You are running `/computer-vision-engineering:plan-cv-evaluation`. Use `cv-model-engineer` (with `cv-systems-architect` for the metric-to-decision map) + the `cv-model-training-and-evaluation` skill.

> Engineering judgment. A benchmark number is not a production guarantee. The metric math is durable; the operating point is `[verify-at-use]` per use-case. Evaluate on production-like data. No PII.

## Steps
1. Map the metric to the decision: pick mAP/IoU/precision-recall/F1 from the cost of a miss, and state the operating point and the acceptance bar.
2. Design the eval dataset from production-like data (real cameras, lighting, distribution, including hard/rare cases) and check for train/test leakage.
3. Define the per-slice reporting (per-class + per-condition) and a fixed regression suite so a "better" model can't silently regress a key slice.
4. Plan the post-optimization accuracy re-check (after quantization/export) and the drift-monitoring signal + trigger for re-labeling / active learning.
5. Emit using `templates/cv-evaluation-plan.md` + the Structured Output block, taking the metric/operating point from `cv-systems-architect` and the post-optimization check from `vision-deployment-engineer`.
