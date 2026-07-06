---
name: vision-inference-optimization
description: "Make a trained vision model fit and run on its target: budget latency on the real device, optimize in order of leverage (quantization INT8/FP16 with calibration, then pruning, then distillation), export to the runtime the target uses (ONNX / TensorRT / CoreML / TFLite / OpenVINO), and re-check accuracy against the operating point after every step. Device/runtime numbers verify-at-use; no PII."
---

# Vision Inference Optimization

The discipline of holding the latency budget without giving away the accuracy the model was built to deliver. A model that hits its metric offline but can't run inside the budget on the target has shipped nothing.

> **Engineering judgment.** Accelerator specs, runtime op-support, and quantization behavior move with hardware and SDK versions — every device number and runtime-support claim here is `[verify-at-use]`. No PII, no image data stored.

## Workflow

1. **Budget latency on the real target.** The target + required throughput fix the budget (e.g. 30 fps → ~33 ms/frame). Profile on the actual device — a desktop GPU number is not a Jetson number.
2. **Optimize in order of leverage.** Quantization (INT8/FP16 with proper calibration) usually buys the most; then pruning; then distillation to a smaller student. Stop when the budget is met.
3. **Re-check accuracy after every step.** Every optimization can move accuracy — re-run the eval harness against the operating point after each, don't assume parity. A quantization that drops the rare class below the operating point is a regression, not a speedup.
4. **Export to the runtime the target uses.** ONNX as the interchange, then TensorRT (NVIDIA), CoreML (Apple), TFLite (mobile/Coral), OpenVINO (Intel). Confirm the ops your model uses are supported on the target runtime `[verify-at-use]` before committing.
5. **Profile the whole frame, not just the forward pass.** Decode, copy, and pre/post-processing often cost more than inference — find the real bottleneck before optimizing the model further.

## Metrics table

| Metric | Target/read | Flag |
|---|---|---|
| On-target latency vs budget (ms) | At or under the frame budget | `[verify-at-use]` per device |
| Post-optimization accuracy vs operating point | Still clears the acceptance criterion | durable check |
| Precision mode (FP32 / FP16 / INT8) | Smallest that holds accuracy | `[verify-at-use]` |
| Model size / memory on target | Fits the device | `[verify-at-use]` |
| Runtime op-support for the model | All ops supported on target | `[verify-at-use]` |

## Anti-patterns

- Optimizing without an on-target latency budget.
- Assuming quantization is accuracy-free — shipping without re-running eval.
- Exporting to a runtime that doesn't support an op the model uses.
- Optimizing the model when decode/copy is the real bottleneck.

## See also

- Traverse the **deployment-target choice** tree in [`../../knowledge/cv-decision-trees.md`](../../knowledge/cv-decision-trees.md).
- Dated accelerator/runtime landscape: [`../../knowledge/cv-reference-2026.md`](../../knowledge/cv-reference-2026.md).
- Sibling skills: [`../video-pipeline-and-edge-deployment/SKILL.md`](../video-pipeline-and-edge-deployment/SKILL.md), [`../cv-model-training-and-evaluation/SKILL.md`](../cv-model-training-and-evaluation/SKILL.md).
- Best practices: [`../../best-practices/optimize-for-the-deployment-target-from-day-one.md`](../../best-practices/optimize-for-the-deployment-target-from-day-one.md).
- Deep profiling methodology: [`../../../performance-engineering/CLAUDE.md`](../../../performance-engineering/CLAUDE.md).
