# Changelog — computer-vision-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.2] — 2026-09-14

### Changed

- `vision-deployment-engineer`: `model: opus` → `model: sonnet`. Second model-tier pass — export/runtime/quantization work downstream of `cv-systems-architect` (task framing) and `cv-model-engineer` (model selection), both of which stay on `opus`. This is the `sonnet` row of the marketplace's tier table (`ravenclaude-core/knowledge/model-tier-delegation.md`: bounded, well-specified work against a design made upstream), and the sibling-plugin parity rule the doctrine now states: the same role shape gets the same tier across plugins. Listed by the model-tier-fit gate's `--report` pair-review queue (`check-model-tier-fit.py`, Gate 288). No behaviour change beyond the model the agent runs on — it moves tier, not role.

## [0.1.1] — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself; Gate 206 forbids the digit.

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
