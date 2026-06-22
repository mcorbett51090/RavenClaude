---
name: computer-vision-pipeline
description: "Run the computer-vision MLOps lane end to end: data/annotation -> CV task -> architecture choice -> training (transfer-learn first) -> eval by task (mAP/IoU/CER/OKS) -> serving/edge placement. CV-specific leakage (scene-aware split, augment-after-split). Seams back to training/serving/monitoring agents."
---

# Computer-Vision Pipeline

CV is a **sub-domain of MLOps**, not a separate track — it runs the same train->register->serve->monitor loop with image/video-specific choices. Full decision trees + notes: [`../../knowledge/computer-vision-engineering.md`](../../knowledge/computer-vision-engineering.md).

## 1. Data & annotation
Define a label guideline, measure inter-annotator agreement, version the label schema (a relabel = a new data version). Class imbalance is the norm — track per-class, not aggregate. Watch metadata/near-duplicate leakage (capture device, filename, timestamp). Faces/plates/medical/PII -> `data-governance-privacy` + `security-engineering`.

## 2. Task -> architecture
Pick the **cheapest family that answers the question** (task -> architecture tree): classification, detection (real-time YOLO/RT-DETR vs accuracy-first DETR/Faster-RCNN), semantic vs instance segmentation, OCR, keypoint/pose. Then take that family through the build-vs-fine-tune-vs-prompt sourcing tree.

## 3. Training
**Transfer-learn / fine-tune a pretrained backbone first**; from-scratch only for exotic-domain + large-data cases. Freeze-then-unfreeze; version the pretrained checkpoint exactly. CV leakage discipline: **split by scene/source/patient, not random frame** (near-duplicate frames leak); **augment the training split only, after the split**, and only with label-preserving transforms (a flip can be label-destroying for text/pose).

## 4. Eval by task
The metric is task-specific: classification -> precision/recall/F1/PR-AUC (accuracy lies under imbalance); detection -> mAP@IoU; semantic seg -> mean IoU/Dice; instance/panoptic -> mask mAP/PQ; OCR -> CER/WER; keypoint -> PCK/OKS-mAP. Eval set held out and **not augmented**; per-class/per-slice over aggregate. Whether a lift is *real* -> `applied-statistics`.

## 5. Serving / edge placement
Choose edge-vs-cloud (inference-placement tree): cloud batch (offline corpus), on-device/edge (real-time / no connectivity / raw imagery can't leave), edge-opt (quantize/prune/distill + compile — **re-measure accuracy after**), edge->cloud hybrid, or cloud real-time. **Same preprocessing in train and at the inference target**, or you have image-form training-serving skew.

## Seams back to the core agents
- **Training** (reproducible pipeline, scene-aware split, augmentation discipline, experiment tracking) -> `training-pipeline-engineer`.
- **Serving / edge** (placement, quantize/compile + accuracy re-check, latency budget) -> `model-serving-engineer`.
- **Monitoring** (CV input drift = lighting/camera/domain shift; decay; retrain trigger) -> `ml-monitoring-engineer`.
- **Architecture / build-vs-buy** -> `ml-platform-architect`.
- LLM/vision-generative or open-ended NL-over-image tasks -> `claude-app-engineering` (this team owns classical/custom-CV MLOps).
