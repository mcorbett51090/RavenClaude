---
name: cv-task-and-data-strategy
description: "Frame the computer-vision task (classification / detection / segmentation / OCR / pose / tracking / VLM) on the decision the system must make, choose the metric that mirrors the business cost, decide build-vs-fine-tune-vs-API jointly with the deployment target, and design the data & annotation strategy. Model/metric specifics verify-at-use; no PII, no image data stored."
---

# CV Task & Data Strategy

The first and most expensive vision decision: what task the problem actually is, what metric proves it works, and what data it needs. Everything downstream — the model, the labeling budget, the deployment path — is fixed by this framing, so make it deliberately.

> **Engineering judgment, landscape is volatile.** Model families, vision APIs, and their reported accuracies change with every release. Every model/metric specific here is `[verify-at-use]` — confirm against the vendor/framework/paper before it drives a build commitment. No PII, no image data stored.

## Workflow

1. **State the decision the system must make.** "Is there a defect?" (classification), "where are the defects?" (detection), "which pixels?" (segmentation), "what does the label say?" (OCR), "same car across frames?" (tracking) are different problems. The decision picks the task; the task fixes the annotation type.
2. **Choose the metric that mirrors the cost, up front.** mAP/IoU for detection/segmentation, precision/recall at a stated operating point for a cost-asymmetric classifier. Name the false-positive rate you can live with — that is the acceptance criterion.
3. **Decide build-vs-fine-tune-vs-API jointly with the deployment target.** A cloud vision API, a fine-tuned open model, and a from-scratch train differ in cost/control/latency — and the target (cloud GPU / edge / embedded / browser) fixes the model-size and latency budget. Never pick the model without the target.
4. **Design the annotation strategy.** The label schema, the quality/consistency process, and an active-learning loop — annotation is usually the dominant cost, so treat it as a first-class design input, not an afterthought.
5. **Sketch the vision-MLOps pipeline.** data → train → eval (against the chosen metric) → deploy (to the target) → monitor (for drift). Hand the eval harness to `cv-model-training-and-evaluation` and the deployment path to `vision-inference-optimization` / `video-pipeline-and-edge-deployment`.

## Metrics table

| Decision input | What it tells you | Flag |
|---|---|---|
| The decision the system makes | The vision task + annotation type | durable |
| Cost of a miss vs a false alarm | The metric + operating point | `[verify-at-use]` per use-case |
| Deployment target (cloud / edge / embedded / browser) | Model-size + latency budget | `[verify-at-use]` per device |
| Labeled data available vs affordable | Build-vs-fine-tune-vs-API + active-learning need | `[verify-at-use]` |
| Distribution / lighting / sensors in production | Augmentation + in-the-wild eval design | durable |

## Anti-patterns

- Solving a detection problem as classification (or the reverse) because it's easier to label.
- Optimizing overall accuracy when the cost is asymmetric — the operating point is the real target.
- Choosing the model before the deployment target, then discovering it can't run there.
- Treating annotation as a one-shot dump instead of an active-learning loop.

## See also

- Traverse the **vision-task selection**, **build-vs-fine-tune-vs-API**, and **deployment-target choice** trees in [`../../knowledge/cv-decision-trees.md`](../../knowledge/cv-decision-trees.md).
- Dated landscape: [`../../knowledge/cv-reference-2026.md`](../../knowledge/cv-reference-2026.md).
- Sibling skills: [`../cv-model-training-and-evaluation/SKILL.md`](../cv-model-training-and-evaluation/SKILL.md), [`../vision-inference-optimization/SKILL.md`](../vision-inference-optimization/SKILL.md).
- Best practices: [`../../best-practices/measure-with-the-metric-that-matches-the-decision.md`](../../best-practices/measure-with-the-metric-that-matches-the-decision.md), [`../../best-practices/label-and-annotation-cost-drives-the-pipeline.md`](../../best-practices/label-and-annotation-cost-drives-the-pipeline.md).
- Template: [`../../templates/cv-project-architecture.md`](../../templates/cv-project-architecture.md).
