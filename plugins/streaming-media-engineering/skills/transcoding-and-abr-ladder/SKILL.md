---
name: transcoding-and-abr-ladder
description: "Choose codecs in tiers (H.264 reach floor + HEVC/AV1/VP9 efficiency), design the ABR ladder per-title from content complexity rather than a fixed table, build the FFmpeg pipeline for the quality/throughput/cost triangle (CRF vs 2-pass, GPU vs CPU, chunked parallel, GOP/segment alignment), and package once to CMAF/fMP4 with captions and loudness-normalized audio. Codec/flag/bitrate specifics verify-at-use."
---

# Transcoding & ABR Ladder

The discipline of turning source into the smallest set of renditions that reach every device at the promised quality, for a defensible cost. Encoding is where bitrate efficiency and quality are won or lost.

> **Engineering judgment.** Codec capabilities, encoder flags, and hardware support move with library and hardware versions — every codec claim, FFmpeg flag, and per-tier bitrate here is `[verify-at-use]`. No PII.

## Workflow

1. **Choose codecs in tiers.** H.264/AVC as the universal reach floor; HEVC and AV1 (VP9 where relevant) as efficiency tiers for capable devices at higher encode cost. Serve reach *and* save egress.
2. **Design the ladder per-title.** Analyze content complexity and set resolutions/bitrates the content needs — a talking-head and a sports clip do not deserve the same ladder. Cap the top by realistic screens and bandwidth.
3. **Build the FFmpeg pipeline for the triangle.** CRF/constrained-VBR vs 2-pass, preset, GOP/segment-aligned keyframes across renditions (clean ABR switching), and chunked parallel encoding for throughput. Name the quality/throughput/cost trade.
4. **Decide GPU vs CPU per tier.** Hardware (NVENC/QSV/VAAPI) is fast/cheap per stream at some quality cost; CPU (x264/x265/libaom/SVT-AV1) gives best quality-per-bit at higher cost. Match to the tier and farm economics.
5. **Package once and finish the tracks.** CMAF/fMP4 fragments serving HLS + DASH, correct segment/GOP alignment, captions (WebVTT, CEA-608/708), audio (AAC for reach, Opus where supported) with loudness normalization, and thumbnails/sprites for scrubbing.

## Metrics table

| Metric | Target/read | Flag |
|---|---|---|
| Bitrate per rendition vs quality (VMAF/PSNR) | Content-justified, not table-copied | `[verify-at-use]` |
| Encode throughput (x realtime) | Meets farm SLA | `[verify-at-use]` |
| Encode cost per hour of content | Within budget | `[ESTIMATE]` |
| GOP/segment alignment across ladder | Aligned for clean ABR switching | must-hold |
| Audio loudness (target LUFS) | Normalized to target | `[verify-at-use]` |

## Anti-patterns

- Copying a fixed bitrate ladder instead of encoding per-title.
- Picking one codec and either starving reach or overpaying egress.
- Misaligned keyframes across renditions — ABR switching stutters.
- Encoding twice to feed HLS and DASH separately instead of CMAF once.
- Forgetting captions/audio/thumbnails until QA finds them missing.

## See also

- Traverse the **codec choice** tree in [`../../knowledge/streaming-decision-trees.md`](../../knowledge/streaming-decision-trees.md).
- Dated codec/encoder/bitrate landscape: [`../../knowledge/streaming-reference-2026.md`](../../knowledge/streaming-reference-2026.md).
- Sibling skills: [`../streaming-architecture-and-protocol-selection/SKILL.md`](../streaming-architecture-and-protocol-selection/SKILL.md), [`../playback-qoe-and-delivery/SKILL.md`](../playback-qoe-and-delivery/SKILL.md).
- Best practices: [`../../best-practices/design-the-abr-ladder-per-title-not-fixed.md`](../../best-practices/design-the-abr-ladder-per-title-not-fixed.md), [`../../best-practices/test-across-devices-and-network-conditions.md`](../../best-practices/test-across-devices-and-network-conditions.md).
- Template: [`../../templates/abr-ladder-plan.md`](../../templates/abr-ladder-plan.md).
