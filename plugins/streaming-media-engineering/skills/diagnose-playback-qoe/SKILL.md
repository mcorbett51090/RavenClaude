---
name: diagnose-playback-qoe
description: "Root-cause a streaming playback QoE problem — rebuffering, slow startup, ABR thrash, playback errors — from player analytics, not encoder metrics. Walks the chain from ladder/keyframe alignment to segment duration to cache-miss/origin latency to ABR logic. Driven by media-pipeline-engineer."
---

# Skill: Diagnose Playback QoE

QoE is measured at the player. This skill root-causes rebuffering/startup/error
problems along the delivery chain. Driven by `media-pipeline-engineer`.

## Step 0 — Get the player-side numbers first

Diagnose from **player analytics**, not encoder VMAF: **startup time, rebuffer
ratio, average bitrate, error/exit-before-video rate**, and the ABR switch log.
Encoder-side quality metrics don't tell you whether users can watch. If there's no
player instrumentation, that's finding #1 — add it.

## Step 1 — Rebuffering

Walk the chain, cheapest cause first:

| Symptom | Likely cause | Fix |
|---|---|---|
| Stalls at rung switches | **Misaligned keyframes/GOP** across rungs | Re-encode with aligned closed GOPs at segment boundaries. |
| Stalls under load / spiky | **Cache misses → origin latency** | Fix cache keys/TTLs, add origin shield, check query-string/byte-range handling. |
| Stalls on poor networks | **Ladder gap** (no low-enough rung) | Add a lower rung; check ABR down-switch aggressiveness. |
| Constant micro-stalls | Segment duration too short for the tier | Retune segment duration to the latency tier. |

## Step 2 — Slow startup

- Startup = manifest fetch + first segments + player buffer target. Check: is the
  first rung too high (start lower, switch up)? Is the initial buffer target too
  large? Is the manifest/first segment a cache miss?
- For LL tiers, confirm partial-segment delivery is actually working end to end.

## Step 3 — ABR thrash

Rapid up/down switching hurts perceived quality. Check the player's ABR config
(switching thresholds, buffer-based vs bandwidth-based logic) and whether the ladder
rungs are too closely spaced.

## Step 4 — Playback errors

Separate hard errors: manifest/codec-string mismatch (player can't decode a rung),
CORS misconfiguration (browser players), DRM license failures (per-platform — test
each DRM), and 4xx/5xx from origin/CDN. Each is a different owner.

## Step 5 — Output

A root-caused diagnosis: **the QoE metric that regressed, the cause located on the
delivery chain, the fix, and the metric it should move.** If the fix requires a
design change (e.g. the latency tier can't hit the QoE bar), escalate to
`streaming-media-architect` with the player metrics as evidence.
