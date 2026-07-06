# computer-vision-engineering

A RavenClaude plugin: a **computer-vision engineering** specialist team for building production image and video systems — the three engines of a vision build: system architecture, model engineering, and inference optimization & deployment.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Vision-specific by design.** This plugin is deliberately narrower and deeper than the sibling [`ml-engineering`](../ml-engineering/) plugin (which is MLOps-broad): it is about image/video tasks, annotation pipelines, and edge/embedded inference. For general model lifecycle, tabular/NLP modeling, and training infrastructure, use `ml-engineering`.

> **Engineering judgment — not a benchmark leaderboard, an accuracy guarantee, or a compliance/biometric-legality verdict.** The model / hardware / runtime / annotation-tool landscape is volatile: every model name/version, accelerator spec, and accuracy/latency number carries a retrieval date + `[verify-at-use]` and must be confirmed against the vendor/framework/paper before it drives a build commitment. The agents store no PII and no image/video data.

## What it's for

Building vision systems well: framing the task correctly (is it classification, detection, segmentation, OCR, pose, tracking, or a VLM?), deciding build-vs-fine-tune-vs-API, choosing the model family (CNN vs ViT vs foundation model) against the deployment target you'll actually ship to, measuring with the metric that matches the business decision, spending the annotation budget where active learning says it helps, and holding the latency budget on the edge or embedded target.

## Agents

| Agent | Use for |
|---|---|
| **cv-systems-architect** | Task framing (classification / detection / segmentation / OCR / pose / tracking / VLM), data & annotation strategy, model-family & build-vs-API choice, deployment-target selection, eval-metric design |
| **cv-model-engineer** | Dataset curation & augmentation, transfer learning / fine-tuning, model selection (YOLO / DETR / SAM / CLIP / EfficientNet / ViT), loss & metric design, active learning, class imbalance, the eval harness, drift detection |
| **vision-deployment-engineer** | Inference optimization (quantization / pruning / distillation), export/runtime (ONNX / TensorRT / CoreML / TFLite / OpenVINO), edge/embedded (Jetson / mobile NPU / Coral), batching, streaming-video pipelines, latency budgets, camera integration |

## What's inside

- **4 skills** — cv-task-and-data-strategy, cv-model-training-and-evaluation, vision-inference-optimization, video-pipeline-and-edge-deployment.
- **Knowledge bank** — [`cv-decision-trees.md`](knowledge/cv-decision-trees.md) (4 Mermaid trees: vision-task selection, build-vs-fine-tune-vs-API, model-family choice, deployment-target choice) + [`cv-reference-2026.md`](knowledge/cv-reference-2026.md) (dated model/accelerator/runtime/annotation-tool landscape + metric definitions, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — CV project architecture, CV evaluation plan.
- **2 commands** — `/choose-cv-approach`, `/plan-cv-evaluation`.

## Seams

Broad MLOps / non-vision modeling → [`ml-engineering`](../ml-engineering/) · VLM in a retrieval/RAG context → [`ai-rag-engineering`](../ai-rag-engineering/) · host firmware / sensor drivers / board bring-up → [`embedded-iot-engineering`](../embedded-iot-engineering/) · deep profiling → [`performance-engineering`](../performance-engineering/) · label/data store & orchestration → [`data-platform`](../data-platform/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install computer-vision-engineering@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the scope, routing rules, house opinions, and the output contract.
