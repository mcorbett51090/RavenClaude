---
name: design-streaming-delivery
description: "Design an audio/video delivery system end to end: interrogate the real latency requirement, pick the tier + protocol + packaging (HLS/LL-HLS/DASH/CMAF/WebRTC), decide DRM (CBCS multi-DRM vs AES-128 vs none), the codec ladder, and the CDN/QoE/cost plan. Reach for this at the START, before building any pipeline. Driven by streaming-media-architect."
---

# Skill: Design Streaming Delivery

The binding decision in streaming is the **latency tier**, and most "real-time"
requirements aren't. This skill produces the delivery design before any pipeline is
built. Driven by `streaming-media-architect`.

## Step 1 — Interrogate the latency requirement

Traverse [`../../knowledge/latency-tier-to-protocol-decision-tree.md`](../../knowledge/latency-tier-to-protocol-decision-tree.md).
Ask what breaks if latency is 10–30s:

| Real requirement | Tier | Protocol |
|---|---|---|
| One-way broadcast, huge scale, 10–30s fine | Broadcast | Standard HLS / DASH |
| Near-real-time, ~2–6s (sports, live events) | Low | LL-HLS / LL-DASH over CMAF |
| Two-way / interactive / bet-in-play, <1s | Ultra-low | WebRTC (WHIP/WHEP) |

Each step down costs scale, cost, and complexity. Don't pay the real-time tax for
seconds you don't need.

## Step 2 — Package once (CMAF)

Default to **CMAF fragmented-MP4** so one segment set serves HLS and DASH. Only
maintain a parallel legacy rendition tree if a specific old-device set forces it.

## Step 3 — Decide DRM by content value

- **Open content** → no DRM.
- **Basic protection** → AES-128 / clear-key.
- **Premium / licensed** → studio-grade **multi-DRM** (Widevine + FairPlay +
  PlayReady) via **CBCS package-once** — never encrypt three times. This adds a
  license server, key rotation, and per-device testing; take it on only when
  licensing requires it. (See the DRM matrix in
  [`../../knowledge/streaming-codecs-protocols-and-cdn-2026.md`](../../knowledge/streaming-codecs-protocols-and-cdn-2026.md).)

## Step 4 — Codec ladder for reach vs cost

H.264 as the reach baseline; add HEVC/AV1 where the device base supports them and
bitrate (⇒ egress) savings justify the extra encode. Per-title ladders when volume
justifies it. Keyframe alignment across rungs is mandatory for ABR.

## Step 5 — CDN topology + QoE + cost

Single vs multi-CDN + origin shield; the cache-key/segment strategy; and the QoE
contract — **startup time, rebuffer ratio, average bitrate, error rate**. Egress
dominates the bill, so name the cost seam to `finops-cloud-cost` for any at-scale
design.

## Step 6 — Output

A delivery design: **latency tier + protocol/packaging + DRM + codec ladder +
CDN/QoE/cost plan + the 1–2 flip conditions.** Hand to `media-pipeline-engineer` to
build via `build-transcode-ladder`.
