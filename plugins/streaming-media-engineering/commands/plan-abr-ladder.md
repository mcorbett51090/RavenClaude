---
description: "Design a per-title ABR ladder for a content class: choose codec tiers (H.264 reach + HEVC/AV1/VP9 efficiency), set resolutions/bitrates from content complexity rather than a fixed table, define the FFmpeg pipeline (GPU vs CPU, rate control, GOP alignment), and the CMAF packaging + captions + audio plan (codec/bitrate specifics verify-at-use)."
argument-hint: "[content class + source characteristics + target device/bandwidth reach + ABR-ladder philosophy]"
---

You are running `/streaming-media-engineering:plan-abr-ladder`. Use `transcoding-pipeline-engineer` + the `transcoding-and-abr-ladder` skill.

> Engineering judgment. Every codec claim, FFmpeg flag, and per-tier bitrate is `[verify-at-use]`. Encode per-title, not from a fixed table. No PII.

## Steps
1. Capture the content class, source characteristics (resolution/fps/HDR/complexity), the target device/bandwidth reach, and the ABR-ladder philosophy from the architect.
2. Traverse the **codec choice** tree in `knowledge/streaming-decision-trees.md` — pick a reach tier (H.264) and an efficiency tier (HEVC / AV1 / VP9) on target decode support and the cost/royalty trade.
3. Design the ladder per-title: resolutions/bitrates justified by content complexity, top rung capped by realistic screens/bandwidth, GOP/segment-aligned keyframes for clean ABR switching.
4. Define the FFmpeg pipeline (rate control, preset, GPU vs CPU, chunked parallel) and the CMAF/fMP4 packaging + captions (WebVTT/CEA-608/708) + audio (AAC/Opus + loudness) + thumbnails plan.
5. Emit using `templates/abr-ladder-plan.md` + the Structured Output block, taking the ladder philosophy/CDN/DRM from `media-streaming-architect` and handing playback validation/QoE to `playback-and-delivery-engineer`.
