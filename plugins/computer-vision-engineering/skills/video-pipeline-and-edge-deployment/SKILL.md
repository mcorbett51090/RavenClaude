---
name: video-pipeline-and-edge-deployment
description: "Design streaming-video pipelines that hold the frame budget — frame sampling / keyframe strategy, ROI cropping, tracking-by-detection so the detector doesn't run every frame, and batching where latency allows — and deploy to edge/embedded targets (Jetson, mobile NPU, Coral) with the camera/sensor capture and pre-processing counted inside the budget. Device numbers verify-at-use; no PII."
---

# Video Pipeline & Edge Deployment

The discipline of holding real-time throughput on a stream, on the edge. The pipeline — capture, decode, pre-process, detect, track, post-process — is the product, not just the model, and the whole frame has to finish inside the budget.

> **Engineering judgment.** Edge accelerator specs, codec/decode support, and runtime behavior move with hardware and SDK versions — every device number and support claim here is `[verify-at-use]`. No PII, no image data stored.

## Workflow

1. **Set the frame budget from the stream.** The target fps fixes the per-frame budget (30 fps → ~33 ms). The whole pipeline — not just inference — must finish inside it.
2. **Don't run the detector on every frame.** Frame sampling / keyframe strategy, ROI cropping (run the detector on a region, not the full frame), and tracking-by-detection (detect periodically, track cheaply between) are the highest-leverage moves on most video pipelines.
3. **Batch where latency allows.** Batching raises throughput but adds latency — only where the budget has room. For hard real-time, prefer a streaming, low-latency path.
4. **Count capture and pre-processing in the budget.** Camera/sensor capture, color/format conversion, resize, and normalization live inside the frame budget too. Zero-copy and on-device pre-processing where the target supports it.
5. **Deploy to the edge target with headroom for thermal + sustained load.** Jetson / mobile NPU / Coral throttle under sustained load — budget for the sustained clock, not a short demo, and leave headroom.

## Metrics table

| Metric | Target/read | Flag |
|---|---|---|
| End-to-end frame time vs budget (ms) | Whole pipeline under the fps budget | `[verify-at-use]` per device |
| Detector invocation rate | Below every-frame via sampling/tracking | durable |
| Dropped-frame rate on the stream | Near zero in sustained use | `[verify-at-use]` |
| Capture + pre/post-process share of frame | Bounded; often the real cost | `[ESTIMATE]` |
| Sustained thermal frame time on edge | Held at throttled clock | `[verify-at-use]` |

## Anti-patterns

- Running the full detector on every frame at full resolution.
- Batching a hard-real-time stream and adding latency you can't afford.
- Ignoring decode/capture/pre-process cost and blaming the model.
- Budgeting on a 30-second demo instead of a sustained, thermally-throttled session.

## See also

- Traverse the **deployment-target choice** tree in [`../../knowledge/cv-decision-trees.md`](../../knowledge/cv-decision-trees.md).
- Dated edge/accelerator landscape: [`../../knowledge/cv-reference-2026.md`](../../knowledge/cv-reference-2026.md).
- Sibling skills: [`../vision-inference-optimization/SKILL.md`](../vision-inference-optimization/SKILL.md), [`../cv-task-and-data-strategy/SKILL.md`](../cv-task-and-data-strategy/SKILL.md).
- Best practices: [`../../best-practices/optimize-for-the-deployment-target-from-day-one.md`](../../best-practices/optimize-for-the-deployment-target-from-day-one.md).
- Host firmware / sensor drivers / board bring-up: [`../../../embedded-iot-engineering/CLAUDE.md`](../../../embedded-iot-engineering/CLAUDE.md).
