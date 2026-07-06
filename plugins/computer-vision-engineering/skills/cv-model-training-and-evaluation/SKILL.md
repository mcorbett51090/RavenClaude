---
name: cv-model-training-and-evaluation
description: "Curate and augment the dataset, choose and fine-tune the model (YOLO / DETR / SAM / CLIP / EfficientNet / ViT) on the task and target budget, design the loss and metric to match the cost, spend the annotation budget with active learning, handle class imbalance, and build an eval harness you can trust with per-slice metrics and drift detection. Model/checkpoint specifics verify-at-use; no PII."
---

# CV Model Training & Evaluation

The discipline of moving the metric honestly. Take the framed task, metric, and operating point and produce a model that hits them on the real distribution — with an eval harness rigorous enough that a passing score means something.

> **Engineering judgment.** Model checkpoints and their reported accuracies move with every release — every model/benchmark number here is `[verify-at-use]`. A benchmark score is not a production guarantee. No PII, no image data stored.

## Workflow

1. **Fix the data first.** Clean labels, resolve annotation inconsistency, and design augmentation that reflects real variation (lighting, scale, occlusion, sensor). Data quality beats model choice on most projects.
2. **Select the model on task + dataset size + target budget.** YOLO-family (fast detection), DETR/transformer detectors, SAM (promptable segmentation), CLIP (zero-shot/embedding), EfficientNet/ConvNeXt/ViT (classification). Prefer transfer learning from a pretrained backbone; train from scratch only when the domain demands it.
3. **Design loss + metric to match the cost.** Class-weighted or focal loss for imbalance, the right IoU/mAP or precision-recall implementation, and the operating point chosen from the cost of a miss — not the default threshold.
4. **Spend the annotation budget with active learning.** Uncertainty/margin sampling, diversity, hard-negative and failure-case mining pick which images to label next. Buy the most metric movement per label; keep a labeler-consistency check.
5. **Build an eval harness you trust.** A held-out split that mirrors production, per-class and per-slice metrics (never just the average), a fixed regression suite so a "better" model can't silently regress a key slice, and a drift check once live.

## Metrics table

| Metric | Target/read | Flag |
|---|---|---|
| Task metric vs operating point (mAP / IoU / P-R) | At or above the acceptance criterion | `[verify-at-use]` per task |
| Per-class / per-slice recall | No dead class hidden by the average | durable |
| Regression suite delta vs last model | No key slice worse | durable |
| Label budget spent per metric point gained | Active learning beats random sampling | `[ESTIMATE]` |
| Drift signal (score / distribution) | Stable in production | `[verify-at-use]` |

## Anti-patterns

- Reaching for a bigger backbone before cleaning the labels.
- Reporting only overall accuracy while a rare class is dead.
- Choosing the operating point at the default 0.5 instead of from the cost.
- Random-sampling the next labels instead of active learning.
- An eval split that leaks or doesn't look like production.

## See also

- Traverse the **model-family choice** and **build-vs-fine-tune-vs-API** trees in [`../../knowledge/cv-decision-trees.md`](../../knowledge/cv-decision-trees.md).
- Dated model/metric landscape: [`../../knowledge/cv-reference-2026.md`](../../knowledge/cv-reference-2026.md).
- Sibling skills: [`../cv-task-and-data-strategy/SKILL.md`](../cv-task-and-data-strategy/SKILL.md), [`../vision-inference-optimization/SKILL.md`](../vision-inference-optimization/SKILL.md).
- Best practices: [`../../best-practices/data-quality-and-labels-beat-model-choice.md`](../../best-practices/data-quality-and-labels-beat-model-choice.md), [`../../best-practices/evaluate-in-the-wild-not-just-on-the-benchmark.md`](../../best-practices/evaluate-in-the-wild-not-just-on-the-benchmark.md).
- Template: [`../../templates/cv-evaluation-plan.md`](../../templates/cv-evaluation-plan.md).
