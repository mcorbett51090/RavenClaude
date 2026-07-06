# Package once with CMAF

**Rule.** Produce one set of **CMAF fragmented-MP4** segments and generate both HLS
(`.m3u8`) and DASH (`.mpd`) from it. Don't maintain parallel TS-HLS and MP4-DASH
rendition trees unless a specific legacy device set forces it.

**Why.** Package-once halves storage and encode work, keeps HLS and DASH in sync,
and is the foundation for CBCS multi-DRM (encrypt one segment set for all three DRM
systems).

**Smell.** Separate TS-HLS and MP4-DASH pipelines; segments re-encoded per protocol;
drift between the HLS and DASH renditions of the same title.

**Cite:** plugin §4.2; the packaging table in
`knowledge/streaming-codecs-protocols-and-cdn-2026.md`.
