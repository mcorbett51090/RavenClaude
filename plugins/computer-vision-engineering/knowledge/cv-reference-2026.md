# Computer-Vision Engineering — 2026 Reference

> Dated reference for the `computer-vision-engineering` team: the model/hardware/runtime/annotation-tool landscape and the metric definitions agents reach for. The durable reasoning lives in [`cv-decision-trees.md`](cv-decision-trees.md); this file is the freshness-anchored "what the landscape and numbers are."
>
> **Engineering judgment, not a benchmark or compliance verdict.** The CV model/hardware/runtime landscape moves fast. Every model name/version, accelerator spec, accuracy or latency number, and framework capability below is **volatile** and carries a **source placeholder + retrieval date + `[verify-at-use]`** — re-confirm against the vendor/framework/paper before it drives a build commitment. Estimates are marked `[ESTIMATE]`. No PII, no image/video data stored.
>
> _Last reviewed: 2026-07-03 by `claude`. Treat every specific as `[verify-at-use]` unless re-confirmed this session._

---

## 1. Model-family / architecture landscape

| Family | Typical task | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| YOLO-family (single-stage detectors) | Real-time object detection | Fast, edge-friendly; versions/variants change often | _<model card / repo>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| DETR / transformer detectors | Detection (accuracy over speed) | Higher compute; no hand-tuned anchors | _<paper / repo>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| SAM-family | Promptable / few-shot segmentation | Strong zero-shot masks; check licensing/size | _<model card>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| CLIP-family | Zero-shot classification, image-text embedding/retrieval | Embeddings for retrieval; not a detector | _<model card>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| EfficientNet / MobileNet / ConvNeXt | Classification (incl. edge) | CNN backbones; MobileNet-class for edge | _<model card>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| ViT / large backbones | Classification, dense prediction | Data- and compute-hungry vs CNNs | _<paper / repo>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Vision-Language Models (VLMs) | Caption / VQA / grounding | Open-ended; heavier, often API/cloud | _<vendor / model card>_ — retrieved 2026-07-03 | `[verify-at-use]` |

> Model names, versions, checkpoints, and their reported accuracies change constantly. Confirm the current model and its licensing/accuracy before committing an architecture to it.

---

## 2. Accelerator / hardware landscape (cloud + edge)

| Class | Examples (names change) | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| Cloud GPU | Data-center GPUs | Largest models, easiest ops; cost per hour matters | _<cloud provider docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| NVIDIA edge module | Jetson-family | TensorRT, INT8/FP16; power/thermal constrained | _<vendor spec>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Mobile NPU / SoC | Phone/tablet neural engines | CoreML / TFLite / NNAPI; per-device op support varies | _<platform docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Tiny edge accelerator | Coral / Edge TPU-class | Heavily-quantized (INT8) TFLite only; tight op set | _<vendor docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Browser (WebGPU/WebGL) | Any WebGPU-capable device | Zero-install; tightest budget, support gated by browser | _<caniuse / runtime>_ — retrieved 2026-07-03 | `[verify-at-use]` |

> Accelerator specs (TOPS, memory, thermal-sustained clock) and their real achievable throughput change per model and generation. Profile on the actual device — a spec-sheet number is not a measured latency.

---

## 3. Framework / runtime landscape

| Layer | What it is | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| PyTorch / TensorFlow | Training frameworks | Where you fine-tune; export from here | _<framework docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| ONNX | Model interchange format | The portability layer between train and target runtime | _<onnx.ai>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| TensorRT | NVIDIA inference runtime | Jetson/data-center GPU; INT8/FP16, op support varies | _<vendor docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| CoreML | Apple on-device runtime | iOS/macOS NPU; convert from ONNX/PyTorch | _<apple docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| TFLite | Mobile/edge runtime | Android/Coral; INT8 quantization for tiny targets | _<tflite docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| OpenVINO | Intel inference runtime | Intel CPU/iGPU/VPU; quantization toolkit | _<intel docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| ONNX Runtime (incl. web) | Cross-platform inference | Server + browser (wasm/WebGPU) execution providers | _<onnxruntime docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |

> Runtime op-support and quantization behavior change release to release. Verify the ops your model uses are supported on the chosen runtime/target before committing an export path.

---

## 4. Annotation-tool landscape

| Category | What it is | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| Bounding-box / polygon labelers | Detection/segmentation annotation UIs | Where the dominant cost lives; consistency process matters | _<tool docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Model-assisted / auto-label | Pre-label with a model, human corrects | Speeds labeling; risks propagating model bias | _<tool docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Active-learning tooling | Selects which unlabeled images to label next | Uncertainty/diversity sampling; buys metric per label | _<tool docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Dataset / label versioning | Versioned datasets + label store | Reproducible eval; see data-platform seam | _<tool docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |

> Tool names and capabilities change; the durable point is that annotation is usually the dominant cost — design the workflow, quality checks, and active-learning loop deliberately.

---

## 5. Metric definitions (durable math, operating point verify-at-use)

| Metric | What it is | Flag |
|---|---|---|
| Precision / Recall | TP/(TP+FP) and TP/(TP+FN) at a chosen threshold | durable; operating point `[verify-at-use]` |
| IoU (Intersection over Union) | Overlap of predicted vs true box/mask | durable |
| mAP (mean Average Precision) | Area under precision-recall, averaged over classes/IoU thresholds | durable; the IoU thresholds used `[verify-at-use]` |
| F1 | Harmonic mean of precision and recall | durable |
| Operating point | The threshold chosen from the cost of a miss vs false alarm | `[verify-at-use]` per use-case |
| Per-class / per-slice metric | The above computed per class or data slice | durable |

> The metric math is durable; the **operating point** and the exact mAP IoU-threshold convention are choices that must match the business cost — state them and treat them as `[verify-at-use]` per use-case.

---

## 6. How to use this file

1. Find the model/accelerator/runtime/tool/metric you need.
2. Read its retrieval date — if stale or unconfirmed this session, **re-verify** against the cited source type before quoting.
3. Quote it with its flag (`[ESTIMATE]` / `[verify-at-use]`) intact when it informs an architecture, model, or deployment commitment.
4. For anything that gates a build decision: confirm against the vendor/framework/paper first, and re-check accuracy on the target after any optimization.

---

## See also

- [`cv-decision-trees.md`](cv-decision-trees.md) — the durable task/build-vs-API/model-family/deployment-target trees.
- Deep profiling methodology: [`../../performance-engineering/CLAUDE.md`](../../performance-engineering/CLAUDE.md).
- Label/data store & orchestration: [`../../data-platform/CLAUDE.md`](../../data-platform/CLAUDE.md).
