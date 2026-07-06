# Computer-Vision Engineering — Decision Trees

> Reference decision trees for the `computer-vision-engineering` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Engineering judgment, not a benchmark or compliance verdict.** Anything touching a model name/version, accelerator spec, latency/accuracy number, or runtime capability is `[verify-at-use]` — confirm against the vendor/framework/paper before it drives a build commitment. No PII, no image data stored.
>
> _Last reviewed: 2026-07-03 by `claude`. Principles are durable; dated specifics live in [`cv-reference-2026.md`](cv-reference-2026.md)._

---

## Decision Tree: which vision task?

```mermaid
flowchart TD
    A[Vision requirement] --> B{What decision must<br/>the system make?}
    B -- "is it present / which category?" --> C[Classification<br/>image-level label]
    B -- "where + what, boxes?" --> D[Object detection<br/>box + class, mAP/IoU]
    B -- "which pixels belong to what?" --> E[Segmentation<br/>semantic / instance masks]
    B -- "what text is written?" --> F[OCR<br/>detect + recognize text]
    B -- "body/keypoint configuration?" --> G[Pose estimation<br/>keypoints]
    B -- "same object across frames?" --> H[Tracking<br/>detection + association]
    B -- "open-ended describe / answer?" --> I[VLM<br/>caption / VQA / grounding]
    C --> J[Task fixes the annotation type<br/>+ the metric to measure it]
    D --> J
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J
```

**Rule:** pick the task on the **decision the system must make**, not the easiest thing to label. The task fixes the annotation type and the metric. If the answer is open-ended natural language over an image, consider a VLM; if it's a fixed closed-set decision, a specialist model is usually cheaper and tighter. All model specifics `[verify-at-use]`.

---

## Decision Tree: build vs fine-tune vs API?

```mermaid
flowchart TD
    A[Task framed] --> B{Does a general vision API<br/>or foundation model<br/>already solve it well enough?}
    B -- "yes, and cost/latency/privacy OK" --> C[Call the API / zero-shot foundation model<br/>— least effort]
    B -- "close but not on our domain" --> D{Have or can label<br/>domain data?}
    B -- "no / privacy or offline or cost rules it out" --> D
    D -- "yes, modest labeled set" --> E[Fine-tune a pretrained model<br/>— transfer learning, usual default]
    D -- "no labeled data, large budget,<br/>truly novel domain" --> F[Train from scratch<br/>— last resort, most cost/data]
    C --> G{Deployment target allows it?<br/>cloud call vs on-device}
    E --> G
    F --> G
    G -- "target rules out the choice" --> H[Re-decide with the target as a constraint]
    G -- ok --> I[Commit; wire the eval harness + operating point]
```

**Rule:** decide build-vs-fine-tune-vs-API **jointly with the deployment target** — the target can rule out a cloud API (privacy/offline/latency) or a large model (edge budget). Transfer-learning/fine-tuning is the usual default; from-scratch is a last resort. API vs on-device cost, privacy, and latency all `[verify-at-use]`.

---

## Decision Tree: which model family?

```mermaid
flowchart TD
    A[Fine-tune or train chosen] --> B{Task + dataset size + target budget}
    B -- "real-time detection,<br/>tight budget" --> C[YOLO-family / efficient detector<br/>fast, edge-friendly]
    B -- "detection, accuracy over speed,<br/>ample compute" --> D[DETR / transformer detector]
    B -- "segmentation, promptable / few labels" --> E[SAM-family<br/>promptable segmentation]
    B -- "zero-shot / embedding / retrieval" --> F[CLIP-family<br/>image-text embeddings]
    B -- "classification, edge budget" --> G[EfficientNet / MobileNet / ConvNeXt-tiny]
    B -- "classification, ample compute,<br/>large data" --> H[ViT / large CNN backbone]
    C --> I{OpenVINO/TensorRT/CoreML/TFLite<br/>support the ops on target? verify-at-use}
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I
    I -- no --> J[Re-check model or export path<br/>before committing]
    I -- yes --> K[Commit; transfer-learn from a pretrained checkpoint]
```

**Rule:** choose the family on **task + dataset size + target budget**, not leaderboard rank. ViT and large backbones need more data and compute than CNNs; edge budgets favor efficient CNNs and YOLO-family detectors. Confirm the export runtime supports the model's ops on the target — `[verify-at-use]` — before committing.

---

## Decision Tree: which deployment target?

```mermaid
flowchart TD
    A[Model + latency need] --> B{Where must inference run?}
    B -- "server-side, batch or API,<br/>ample GPU" --> C[Cloud GPU<br/>largest models, easiest ops]
    B -- "on a device near the camera,<br/>power/space constrained" --> D{Which edge class?}
    B -- "in the user's browser,<br/>zero-install" --> E[Browser<br/>WebGL/WebGPU/ONNX-runtime-web — tightest budget]
    D -- "NVIDIA edge module" --> F[Jetson<br/>TensorRT, INT8/FP16]
    D -- "phone / tablet" --> G[Mobile NPU<br/>CoreML / TFLite / NNAPI]
    D -- "tiny low-power accelerator" --> H[Coral / Edge TPU<br/>heavily quantized TFLite]
    C --> I[Fixes model-size + latency budget<br/>— quantize/export to the runtime]
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J[Re-check accuracy after optimization<br/>against the operating point]
```

**Rule:** the deployment target is a **design input, chosen up front** — it fixes the model-size and latency budget and the export runtime. Cloud GPU allows the largest models and easiest ops; edge/embedded/browser tighten the budget and force quantization/export. Always re-check accuracy after optimization. Accelerator specs + latency `[verify-at-use]`.

---

## See also

- [`cv-reference-2026.md`](cv-reference-2026.md) — dated model/accelerator/runtime/annotation-tool landscape + metric definitions (verify-at-use).
- Skills: [`../skills/cv-task-and-data-strategy/SKILL.md`](../skills/cv-task-and-data-strategy/SKILL.md), [`../skills/cv-model-training-and-evaluation/SKILL.md`](../skills/cv-model-training-and-evaluation/SKILL.md), [`../skills/vision-inference-optimization/SKILL.md`](../skills/vision-inference-optimization/SKILL.md), [`../skills/video-pipeline-and-edge-deployment/SKILL.md`](../skills/video-pipeline-and-edge-deployment/SKILL.md).
