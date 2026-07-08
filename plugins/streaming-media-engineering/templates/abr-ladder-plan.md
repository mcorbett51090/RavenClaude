# ABR Ladder Plan — <project / content class / date>

> Output template for the per-title ABR ladder and the codec/encoding/packaging plan behind it. One per content class (revisit on a codec or reach change). Every codec/bitrate cell carries a source + date or `[verify-at-use]`; encode per-title; no PII.

## Header
- **Project / content class:** _____
- **Source characteristics (resolution / fps / HDR / complexity):** _____
- **Target device/bandwidth reach:** _____
- **Prepared:** 2026-__-__  · **Owner:** _____

## 1. Codec tiers
| Tier | Codec | Role | Flag |
|---|---|---|---|
| Reach | H.264/AVC | plays everywhere | _[verify-at-use]_ |
| Efficiency | HEVC / AV1 / VP9 | cut bitrate for capable devices | _[verify-at-use]_ |
| GPU vs CPU encode | | tier + farm economics | _[verify-at-use]_ |

## 2. Ladder (per-title, justified by complexity)
| Rung | Resolution | Bitrate | Codec | Quality (VMAF/PSNR) | Flag |
|---|---|---|---|---|---|
| 1 (top) | | | | | _[verify-at-use]_ |
| 2 | | | | | _[verify-at-use]_ |
| 3 | | | | | _[verify-at-use]_ |
| 4 | | | | | _[verify-at-use]_ |
| 5 (floor) | | | | | _[verify-at-use]_ |

> Cap the top by realistic screens/bandwidth. Align GOP/segment boundaries across all rungs for clean ABR switching.

## 3. Pipeline & packaging
| Item | Choice | Flag |
|---|---|---|
| Rate control (CRF / constrained-VBR / 2-pass) | | _[verify-at-use]_ |
| Keyframe / GOP alignment across rungs | | must-hold |
| Chunked parallel encoding | | throughput |
| Packaging (CMAF/fMP4 → HLS + DASH) | | _[verify-at-use]_ |
| Captions (WebVTT / CEA-608/708) | | n/a |
| Audio (AAC / Opus) + loudness (LUFS) | | _[verify-at-use]_ |
| Thumbnails / sprites | | scrubbing |

## Headline + actions
- **Headline:** _codec tiers + ladder rationale in one line_
- **Top 2 actions:** _action — owner — expected bitrate/cost movement — by when_
- **Cost note:** _encode + egress at scale (estimate)_

---
_Plus the ravenclaude-core Structured Output block. Encode per-title, not from a fixed table. Align keyframes. Seams: media-streaming-architect (ladder philosophy/CDN/DRM), playback-and-delivery-engineer (player validation/QoE)._
