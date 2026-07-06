# computer-vision-engineering plugin

> **Computer vision as an engineering discipline** for the RavenClaude marketplace:
> framing the vision task, choosing the model against an accuracy/latency/cost
> budget, designing the dataset + eval, and building/optimizing the inference
> pipeline. It answers **"what CV task is this, what model solves it, and how do we
> build, evaluate, and ship it — in the cloud or on the edge?"** — the CV-specific
> layer that `ml-engineering` (generic training/MLOps) and `ai-rag-engineering`
> (text/RAG) are too general to own.

**Designed for:** an engineer with a vision problem — inspect parts, read labels,
count/track objects, segment for measurement, or answer questions about images — who
needs the task framed correctly, the right model family, a trustworthy eval, and a
pipeline that hits its latency budget on the target hardware.

## What this plugin gives you

- **Task framing done right** — turn "detect defects" / "read labels" / "count
  people" into a concrete formulation (classification / detection / segmentation /
  OCR / tracking / pose / vision-LLM) before choosing a model, via a decision tree.
- **A trustworthy evaluation** — a train/val/test split that doesn't leak (no
  frame-level splitting over video), mirrors production, and uses the
  task-appropriate metric (mAP / IoU / CER) with an explicit ship threshold.
- **The least-effort path** — zero-shot foundation model → fine-tune → custom, so you
  don't label thousands of images for something SAM or an open-vocab detector does
  zero-shot.
- **Inference that hits budget** — export (ONNX / TensorRT / OpenVINO / CoreML),
  quantization behind an accuracy gate, resolution/batching tuning, all measured on
  the deployment hardware — plus a fix for the #1 CV production bug (train/serve
  preprocessing skew).

## The two agents

| Agent | Owns |
|---|---|
| `cv-systems-architect` | The approach: task formulation, model-family + build-vs-adapt choice, deployment target/runtime, and the dataset + eval design — against a stated accuracy/latency/cost budget. |
| `cv-implementation-engineer` | The build: preprocessing/augmentation, training/fine-tuning or wiring a zero-shot model, inference/serving, edge/real-time optimization, and debugging accuracy/latency regressions — measured on the target hardware. |

## The three skills

| Skill | What's inside |
|---|---|
| `frame-a-cv-task` | Turn a vague vision goal into a concrete task + model family + deployment target + budget. The first step of any CV project. |
| `design-cv-dataset-and-eval` | Label schema + QA, a non-leaking split mirroring production, the metric + ship threshold, and failure-slice analysis — before any training. |
| `optimize-cv-inference` | Hit an edge/real-time latency budget: export, quantize behind an accuracy gate, tune resolution/batching, watch thermal throttling. Also diagnoses preprocessing skew. |

## When to use it

- You're starting a CV project and need the task framed and a model family chosen
  before you label data or write code.
- Your model is great in the notebook but bad in production (usually preprocessing
  skew or a leaky eval).
- Your model is too slow on the target device and needs to hit a real-time or edge
  latency budget without quietly losing accuracy.

## When *not* to use it

- You need the generic training platform / MLOps (experiment tracking, feature
  stores, model CI) — that's `ml-engineering`. This plugin runs *on* it.
- You're doing text/document RAG or LLM-app plumbing — that's `ai-rag-engineering`.
- You're writing camera firmware / an accelerator HAL / MCU inference — that's
  `embedded-iot-engineering`. This plugin hands off at the firmware line.
- You're transcoding or delivering the video — that's `streaming-media-engineering`.

## Seams to neighbouring plugins

- **`ml-engineering`** — the generic training platform + MLOps this plugin sits on.
- **`ai-rag-engineering`** — text/document retrieval and LLM-app plumbing.
- **`embedded-iot-engineering`** — camera driver / accelerator HAL / MCU inference.
- **`streaming-media-engineering`** — video ingest / transcode / delivery around the model.
- **`performance-engineering`** — system-level latency budgeting beyond the model.
- **`ravenclaude-core`** — the domain-neutral constitution + protocols.

## Requires

- `ravenclaude-core@>=0.7.0`.

See [`CLAUDE.md`](CLAUDE.md) for the team constitution and house opinions.
