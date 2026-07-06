# Use CBCS multi-DRM (encrypt once)

**Rule.** For premium content, encrypt **once with CBCS** at packaging time and drive
Widevine + FairPlay + PlayReady from a multi-DRM license service — never encrypt
three times. Match DRM level to content value: none → AES-128 → studio-grade
multi-DRM with hardware L1.

**Why.** CBCS is the encryption mode all three DRM systems share, so one packaging
serves every platform. Taking on studio-grade DRM adds a license server, key
rotation, and per-device testing — worth it only when licensing requires it.

**Smell.** Three separate encrypted rendition sets (one per DRM); studio-grade DRM
added by reflex to open content; DRM tested only in Chrome (Widevine).

**Cite:** plugin §4.3; the DRM matrix in
`knowledge/streaming-codecs-protocols-and-cdn-2026.md`.
