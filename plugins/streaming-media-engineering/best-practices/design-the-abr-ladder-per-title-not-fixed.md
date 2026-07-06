# Design the ABR ladder per-title, not fixed

**Status:** Absolute rule
**Domain:** Encoding / ABR ladder
**Applies to:** `streaming-media-engineering`

> Engineering rule. Codec/bitrate specifics are `[verify-at-use]`. No PII.

---

## Why this exists

A fixed bitrate ladder (the same resolutions and bitrates for every asset) is convenient and wrong. A low-complexity talking-head reaches perceptual transparency far below the bitrate a fast-motion sports clip needs — so a fixed ladder simultaneously **wastes bits and egress on easy content** and **starves hard content into visible artifacts**. Per-title encoding analyzes content complexity and sets the ladder the content actually needs, which improves quality where it matters and cuts the bill where it doesn't. The savings pay for the analysis.

## How to apply

- Analyze content complexity (per-title, or per-scene where affordable) and set resolutions/bitrates from it, not from a copied table.
- Cap the top rung by the audience's realistic screens and bandwidth — don't ship a 4K rung nobody can pull.
- Keep a reach tier (H.264) and an efficiency tier (HEVC/AV1) with GOP/segment-aligned keyframes so ABR switching is clean (`[verify-at-use]` codec support).
- Measure quality objectively (e.g. VMAF) against bitrate so each rung is justified.

**Do:** justify every rung by content complexity + reach; align keyframes across renditions.
**Don't:** copy a fixed ladder across a whole catalog; add rungs no device will select.

## Edge cases / when the rule does NOT apply

Ultra-low-latency live may not have time for full per-title analysis before encoding — there a well-chosen fixed/live ladder is acceptable, but it should still be tuned to the content class (sports vs studio) rather than a single global table.

## See also

- [`../skills/transcoding-and-abr-ladder/SKILL.md`](../skills/transcoding-and-abr-ladder/SKILL.md)
- Template: [`../templates/abr-ladder-plan.md`](../templates/abr-ladder-plan.md)

## Provenance

Codifies `transcoding-pipeline-engineer` house opinion and the codec-choice decision tree. Codec/bitrate specifics: [`../knowledge/streaming-reference-2026.md`](../knowledge/streaming-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
