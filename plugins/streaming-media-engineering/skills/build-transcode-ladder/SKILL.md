---
name: build-transcode-ladder
description: "Build the transcode/ABR ladder and packaging: choose resolution/bitrate rungs, set codec + GOP/keyframe settings aligned across rungs for clean ABR switching, package CMAF fMP4 into HLS + DASH from one segment set, and validate the manifests. Reach for this when implementing the delivery the architect designed. Driven by media-pipeline-engineer."
---

# Skill: Build the Transcode Ladder

The ladder is what ABR switches across; keyframe alignment is what makes the switch
clean. This skill builds a validated ladder + packaging. Driven by
`media-pipeline-engineer`, to the design the architect set.

## Step 1 — Choose the rungs

- Cover the device/network range: a low rung for poor networks up to the top rung
  the content and audience justify. Don't add rungs no one plays.
- Use a **per-title / context-aware** ladder when volume justifies the analysis —
  simple content doesn't need the top bitrates; complex content needs more rungs in
  the middle.
- Declare each rung's resolution, bitrate, and codec string accurately (players use
  the manifest's codec strings to decide what they can play).

## Step 2 — Codec + GOP settings

- Encode each rung with the codec strategy from the design (H.264 baseline;
  HEVC/AV1 where supported). Match audio codec.
- **Align keyframes/IDR at the segment boundary across every rung** with a fixed
  GOP. This is the single most important setting — misaligned GOPs stop ABR from
  switching cleanly and cause stalls. Set closed GOPs and a segment duration that
  matches the latency tier.

## Step 3 — Package CMAF → HLS + DASH

- Produce **CMAF fragmented-MP4** segments once; generate both the HLS `.m3u8`
  master+media playlists and the DASH `.mpd` from them.
- For a low-latency tier, emit chunked/partial segments (LL-HLS parts) — but only if
  the design calls for it; shorter segments raise request overhead and hurt cache
  efficiency.

## Step 4 — Integrate DRM (if the design calls for it)

Encrypt **once with CBCS** at packaging time and drive Widevine + FairPlay +
PlayReady from a multi-DRM license service. Wire key delivery. (Details:
`build-transcode-ladder` hands the DRM playback test to Step 5 of this skill and to
the QoE skill.)

## Step 5 — Validate — don't eyeball

- Run a manifest conformance check (segment durations, codec strings, rung
  declarations, encryption signaling).
- **Play it on a real player on each target platform** — and, if DRM is on, on each
  DRM target (FairPlay/Safari-iOS, Widevine/Chrome-Android, PlayReady/Edge-Windows).
  "Works in Chrome" is not a validated multi-DRM ladder.

## Step 6 — Output

A built, validated ladder + packaging: **the rungs, the codec/GOP settings, the
CMAF→HLS+DASH manifests (validated), the DRM packaging if any, and the platforms
tested.** Feed playback problems into `diagnose-playback-qoe`.
