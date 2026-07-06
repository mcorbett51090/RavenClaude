---
name: frame-a-cv-task
description: "Turn an ambiguous vision goal ('detect defects', 'read labels', 'count people') into a concrete CV task formulation + candidate model family + deployment target, grounded in the task->model decision tree. Reach for this at the START of any CV project, before choosing a model or labeling data."
---

# Skill: Frame a CV Task

Most failed CV projects solved the *wrong task*. This skill converts a vague goal
into a concrete formulation before any model or data decision. Driven by
`cv-systems-architect`.

## Step 1 — Name the output the system must produce

Force the goal into one output type (traverse
[`../../knowledge/cv-task-to-model-decision-tree.md`](../../knowledge/cv-task-to-model-decision-tree.md)):

| The user says… | The output they actually need | Task |
|---|---|---|
| "Is this part defective?" | one label per image | classification |
| "Where are the defects and how many?" | boxes | detection |
| "How big is the defect / measure its area?" | pixel mask | segmentation |
| "Read the serial number" | text string | OCR |
| "Count unique people crossing the line" | identity over frames | tracking |
| "Where are the joints?" | keypoints | pose |
| "Answer questions about the scene" | free-form text | vision-LLM |
| "Find similar images" | an embedding + index | retrieval |

If two apply (e.g. "count *and* measure"), it is two tasks — say so.

## Step 2 — State the budget explicitly

Pin four numbers *before* choosing a model:

- **Accuracy target** — the task-appropriate metric and the threshold that means
  "good enough" (mAP for detection, IoU/Dice for segmentation, CER for OCR).
- **Latency / frame rate** — per-image ms or fps, on what hardware.
- **Cost** — per-inference or monthly ceiling.
- **Where it runs** — cloud / edge accelerator / CPU / browser / offline.

A model that can't hit the latency budget on the target hardware is the *wrong
model*, however accurate.

## Step 3 — Pick the build-vs-adapt path

Cheapest path that clears the accuracy bar wins:

1. **Zero-shot foundation model** (open-vocab detector, SAM, a VLM) — try this
   first; it may remove the need to label anything.
2. **Fine-tune a pretrained backbone** — the default when you have hundreds–thousands
   of labels.
3. **Train custom / heavy fine-tune** — only when the distribution is far from
   pretraining and you have a lot of data. Justify the jump.

## Step 4 — Name the deployment target + runtime

Traverse the cloud-vs-edge tree in
[`../../knowledge/cv-inference-deployment-and-tooling-2026.md`](../../knowledge/cv-inference-deployment-and-tooling-2026.md).
Cloud GPU for throughput; edge/CPU/browser for latency, privacy, or offline. Name
the runtime (ONNX / TensorRT / OpenVINO / CoreML) and give a rough latency estimate.

## Step 5 — Output

A one-page framing: **task + acceptance metric & threshold + model-family
candidate + build-vs-adapt path + deployment target/runtime + the 1–2 flip
conditions**. Hand to `design-cv-dataset-and-eval` next if training/fine-tuning is
on the path, then to `cv-implementation-engineer` to build.
