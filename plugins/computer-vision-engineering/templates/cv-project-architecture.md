# CV Project Architecture — <project / date>

> Output template for the task/data/model/deployment decision and the vision-system architecture that follows. One per project (revisit on a task or target change). Every model/version/latency cell carries a source + date or `[verify-at-use]`; no PII, no image data stored.

## Header
- **Project / use-case:** _____
- **The decision the system must make:** _____
- **Prepared:** 2026-__-__  · **Owner:** _____

## 1. Task & metric
| Decision | Choice | Basis | Flag |
|---|---|---|---|
| Vision task (classification / detection / segmentation / OCR / pose / tracking / VLM) | | the decision the system makes | n/a |
| Metric (mAP / IoU / precision-recall / F1) | | mirrors the cost of a miss | _[verify-at-use]_ |
| Operating point (threshold / recall floor / max FP rate) | | cost of a miss vs false alarm | _[verify-at-use]_ |
| Annotation type + budget | | cheapest that supports the task | _[verify-at-use]_ |

## 2. Build vs fine-tune vs API + model
| Decision | Choice | Basis | Flag |
|---|---|---|---|
| Build / fine-tune / API | | data available + privacy/latency/cost | _[verify-at-use]_ |
| Model family (YOLO / DETR / SAM / CLIP / EfficientNet / ViT / VLM) | | task + dataset size + target budget | _[verify-at-use]_ |
| Pretrained checkpoint / backbone | | transfer-learning source | _[verify-at-use]_ |

## 3. Deployment target & budget
| Constraint | Value | Flag |
|---|---|---|
| Target (cloud GPU / Jetson / mobile NPU / Coral / browser) | | _[verify-at-use]_ per device |
| Latency / throughput budget (fps -> ms) | | _[verify-at-use]_ |
| Export runtime (ONNX -> TensorRT / CoreML / TFLite / OpenVINO) | | op-support confirmed? _[verify-at-use]_ |
| Model-size / memory ceiling | | _[verify-at-use]_ |

## 4. Pipeline & data strategy (vision-MLOps)
- **Data → train → eval → deploy → monitor:** _____
- **Annotation & active-learning loop:** _____
- **Drift / regression monitoring:** _____

## Headline + risks
- **Headline decision:** _the task + model + target bet, in one line_
- **Top risks:** _the reversal-expensive assumptions + how they're verified_
- **Two things that would change the answer:** _____

---
_Plus the ravenclaude-core Structured Output block. All model/version/latency cells: verify-at-use before commitment. Seams: cv-model-engineer (training/eval), vision-deployment-engineer (export/latency)._
