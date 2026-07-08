# Optimize for the deployment target from day one

**Status:** Absolute rule
**Domain:** Architecture / deployment
**Applies to:** `computer-vision-engineering`

> Engineering rule. Accelerator/runtime numbers are `[verify-at-use]`. No PII, no image data stored.

---

## Why this exists

The deployment target — cloud GPU, Jetson, mobile NPU, Coral, or the browser — fixes the model-size and latency budget. A model chosen for its benchmark accuracy without the target in mind can turn out to be un-runnable on the device you have to ship to: too large for the memory, too slow for the frame budget, or using ops the target runtime doesn't support. Discovering that after training is a full rebuild. The target is a design input, decided up front, not a deployment detail handled at the end.

## How to apply

- Decide the deployment target before or with the model, not after — traverse the deployment-target tree with the model-family tree together.
- Derive the latency budget from the target and required throughput (e.g. 30 fps → ~33 ms/frame) and hold model selection to it.
- Confirm the export runtime (TensorRT / CoreML / TFLite / OpenVINO / ONNX Runtime) supports the model's ops on the target `[verify-at-use]` before committing.
- Re-check accuracy against the operating point after every optimization (quantization/pruning/distillation) — a speedup that drops accuracy below the floor is a regression.

**Do:** choose the model with the target's budget as a hard constraint.
**Don't:** pick on benchmark accuracy and discover the target can't run it.

## Edge cases / when the rule does NOT apply

A pure server-side batch job with generous GPU has a loose budget — but even then, cost per inference and throughput are real constraints; "no budget" is rarely true.

## See also

- [`../skills/vision-inference-optimization/SKILL.md`](../skills/vision-inference-optimization/SKILL.md), [`../skills/video-pipeline-and-edge-deployment/SKILL.md`](../skills/video-pipeline-and-edge-deployment/SKILL.md)
- Template: [`../templates/cv-project-architecture.md`](../templates/cv-project-architecture.md)

## Provenance

Codifies `vision-deployment-engineer` house opinion and the deployment-target-choice tree. Accelerator/runtime numbers: [`../knowledge/cv-reference-2026.md`](../knowledge/cv-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
