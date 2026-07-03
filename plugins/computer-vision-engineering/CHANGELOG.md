# Changelog — computer-vision-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-03

Initial release.

### Added

- **3 agents** — `cv-systems-architect` (task framing across classification/detection/segmentation/OCR/pose/tracking/VLM, data & annotation strategy, model-family & build-vs-API choice, deployment-target selection, eval-metric design), `cv-model-engineer` (dataset curation & augmentation, transfer learning/fine-tuning, model selection across YOLO/DETR/SAM/CLIP/EfficientNet/ViT, loss & metric design, active learning/hard-negative mining, class imbalance, the eval harness, drift/regression detection), `vision-deployment-engineer` (quantization/pruning/distillation, export/runtime across ONNX/TensorRT/CoreML/TFLite/OpenVINO, edge/embedded targets — Jetson/mobile NPU/Coral, batching & throughput, streaming-video pipelines, latency budgets, camera integration).
- **4 skills** — `cv-task-and-data-strategy`, `cv-model-training-and-evaluation`, `vision-inference-optimization`, `video-pipeline-and-edge-deployment`.
- **Knowledge bank** — `cv-decision-trees.md` (4 Mermaid trees: vision-task selection, build-vs-fine-tune-vs-API, model-family choice, deployment-target choice) and `cv-reference-2026.md` (dated reference: model-family/architecture landscape, accelerator/hardware landscape — cloud GPU + edge, framework/runtime landscape, annotation-tool landscape, metric definitions — each with source placeholder + retrieval date + verify-at-use, estimates marked `[ESTIMATE]`).
- **5 best-practices** — measure with the metric that matches the decision, data quality and labels beat model choice, optimize for the deployment target from day one, evaluate in the wild not just on the benchmark, label and annotation cost drives the pipeline.
- **2 templates** — cv-project-architecture, cv-evaluation-plan.
- **2 commands** — `/choose-cv-approach`, `/plan-cv-evaluation`.

### Scope & verify-at-use

- **Vision-specific by design** — distinct from the MLOps-broad `ml-engineering` plugin: image/video tasks, annotation pipelines, and edge/embedded inference.
- **Engineering judgment, not a benchmark leaderboard, an accuracy guarantee, or a compliance/biometric-legality verdict.** The agents store no PII and no image/video data.
- The model / hardware / runtime / annotation-tool landscape is volatile — every model name/version, accelerator spec, and accuracy/latency number in `cv-reference-2026.md` carries a retrieval date + `[verify-at-use]`; re-confirm against the vendor/framework/paper before quoting or committing.
- Seams to `ml-engineering` (broad MLOps/non-vision modeling), `ai-rag-engineering` (VLM in retrieval/RAG), `embedded-iot-engineering` (host firmware/sensor drivers), `performance-engineering` (deep profiling), and `data-platform` (label/data store & orchestration).
