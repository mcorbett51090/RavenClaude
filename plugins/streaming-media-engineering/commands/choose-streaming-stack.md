---
description: "Choose VOD vs live and the streaming protocol (HLS / MPEG-DASH / CMAF / LL-HLS / WebRTC) on the use-case, latency target, and device/browser reach, with a CMAF packaging hedge, a single-vs-multi-CDN strategy, and the multi-DRM matrix (Widevine / FairPlay / PlayReady) named (protocol/DRM specifics verify-at-use)."
argument-hint: "[use-case (VOD/live) + latency target + device/browser reach + scale]"
---

You are running `/streaming-media-engineering:choose-streaming-stack`. Use `media-streaming-architect` + the `streaming-architecture-and-protocol-selection` skill.

> Engineering judgment, not legal/DRM-licensing advice. Every codec/protocol/DRM/CDN specific is `[verify-at-use]`. No PII.

## Steps
1. Capture the use-case (VOD / live / interactive), the required end-to-end latency, the audience's device/browser reach, and the scale.
2. Traverse the **VOD vs live** and **protocol choice** trees in `knowledge/streaming-decision-trees.md`.
3. Decide the protocol + packaging (prefer CMAF so shared fragments serve HLS + DASH), the origin/edge design, and the single-vs-multi-CDN strategy — each specific flagged `[verify-at-use]`.
4. Map the device/browser reach to the multi-DRM matrix (Widevine / FairPlay / PlayReady) and decide packaging/encryption early, not later.
5. Set the ABR-ladder philosophy and cost envelope, then emit using `templates/streaming-architecture.md` + the Structured Output block, handing the concrete ladder to `transcoding-pipeline-engineer` and player/QoE to `playback-and-delivery-engineer`.
