# Date device and codec-support claims

**Rule.** Device/browser codec support, DRM support, CDN features, and per-platform
LL-HLS behavior shift over time. Cite any such claim with a retrieval date, or mark
it `[unverified — training knowledge]` and verify before a commitment.

**Why.** "Device X supports AV1 / FairPlay / LL-HLS" asserted from training data is
stale by the time it ships, and a codec/DRM misread can make a whole delivery design
unplayable on a target platform. Durable mechanics (CMAF package-once, CBCS,
keyframe alignment, QoE definitions) don't need dates; the device-support specifics do.

**Smell.** A device-compatibility or DRM-support claim with no date; a codec ladder
committed to a platform without checking current support.

**Cite:** plugin §4.7; the marketplace accuracy discipline (`AGENTS.md`); the dated
map in `knowledge/streaming-codecs-protocols-and-cdn-2026.md`.
