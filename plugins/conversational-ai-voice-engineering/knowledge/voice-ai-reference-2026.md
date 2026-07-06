# Conversational Voice-AI Engineering — 2026 Reference

> Dated reference for the `conversational-ai-voice-engineering` team: the ASR/TTS/platform/telephony landscape and the latency targets agents reach for. The durable reasoning lives in [`voice-ai-decision-trees.md`](voice-ai-decision-trees.md); this file is the freshness-anchored "what the landscape and numbers are."
>
> **Engineering judgment, not legal/compliance advice.** The voice-AI landscape moves fast. Every model version, provider price, feature-support claim, telephony detail, and latency number below is **volatile** and carries a **source placeholder + retrieval date + `[verify-at-use]`** — re-confirm against the vendor/provider docs before it drives a build commitment. Estimates are marked `[ESTIMATE]`. **No PII; call audio and transcripts are sensitive — do not store them beyond what the task requires.**
>
> _Last reviewed: 2026-07-03 by `claude`. Treat every specific as `[verify-at-use]` unless re-confirmed this session._

---

## 1. ASR (speech-to-text) provider / model landscape

| Provider / model family | Fit | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| Whisper-family (open / hosted) | Batch + near-real-time, broad language coverage | Strong accuracy; streaming needs a wrapper/hosted variant — confirm the streaming path | _<provider / model card>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Deepgram | Real-time streaming ASR | Low-latency streaming, telephony-tuned models, diarization | _<deepgram docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Cloud ASR (Google / Azure / AWS) | Enterprise, wide language + telephony models | Streaming APIs, phrase biasing, per-minute pricing | _<cloud provider docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Platform-bundled ASR | Comes with the voice platform | Convenient; less control over model/tuning | _<platform docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |

> Model names, streaming support, language coverage, and per-minute prices change frequently. Confirm the current model, its streaming latency, and its telephony (8 kHz) accuracy before committing.

---

## 2. TTS (text-to-speech) provider / voice landscape

| Provider / family | Fit | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| ElevenLabs-class | Expressive, natural voices | Low time-to-first-byte streaming, voice library; watch cloning consent | _<provider docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Cloud TTS (Google / Azure / AWS) | Enterprise, many languages/voices | SSML support, streaming, per-character pricing | _<cloud provider docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Real-time/streaming TTS | Lowest first-audio latency | Start speaking on first LLM token; chunked synthesis | _<provider docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Platform-bundled TTS | Comes with the voice platform | Convenient; fewer voice/prosody controls | _<platform docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |

> Voice availability, streaming TTFB, SSML feature support, and pricing move release to release. Confirm the voice, its streaming latency, and consent terms (for any cloned/custom voice) before committing.

---

## 3. Voice-platform / orchestration landscape

| Layer | What it is | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| Managed voice-agent platforms (Vapi / Retell class) | End-to-end hosted voice agents | Fastest to production; STT/LLM/TTS + telephony bundled, less low-level control | _<platform docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Real-time media frameworks (LiveKit / Pipecat class) | Self-orchestrated real-time pipelines | Control over media + turn-taking; you run the stack | _<framework docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Telephony primitives (Twilio class) | Programmable voice / SIP / media streams | You own orchestration; broad carrier reach | _<twilio docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Build-from-scratch | Your own media + STT/LLM/TTS wiring | Max control, max effort | _<internal>_ — retrieved 2026-07-03 | `[verify-at-use]` |

> Platform feature sets, supported channels, tool-calling hooks, and pricing change frequently. Verify the platform supports your channel, mid-call tools, barge-in, and latency needs before committing, and isolate it behind seams.

---

## 4. Telephony protocols (SIP / PSTN / WebRTC)

| Protocol / concept | What it is | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| PSTN | Public switched telephone network | Legacy phone reach; 8 kHz narrowband audio | _<carrier / provider docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| SIP | Session Initiation Protocol | Call signaling/setup for VoIP trunks | _<RFC / provider docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| RTP / media streams | Real-time audio transport | Codec + jitter/latency handling | _<provider docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| WebRTC | Browser/app real-time media | Wideband, lower transport latency, Opus | _<w3c / webrtc docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| DTMF | Keypad tones (touch-tone) | In-band vs RFC 2833/SIP INFO — capture path varies | _<provider docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Codecs | µ-law/a-law (telephony), Opus/PCM (web) | Sample rate + codec fix ASR/TTS audio format | _<provider docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |

> Protocol behavior is durable, but DTMF capture paths, codec support, and provider-specific media formats vary. Confirm the DTMF path and codec/sample rate for your provider before wiring.

---

## 5. Per-hop latency targets `[ESTIMATE]`

| Hop | Rough target (concept) | Note | Flag |
|---|---|---|---|
| VAD / endpointing decision | ~200–500 ms of trailing silence | Trade responsiveness vs cutting the user off; tune on real audio | `[ESTIMATE]` `[verify-at-use]` |
| STT final result | Low hundreds of ms after speech ends | Streaming interim results hide most of this | `[ESTIMATE]` `[verify-at-use]` |
| LLM time-to-first-token | Low hundreds of ms | Model size + prompt length dominate; stream tokens | `[ESTIMATE]` `[verify-at-use]` |
| TTS time-to-first-byte | ~100–300 ms | Start speaking on the first token; streaming TTS | `[ESTIMATE]` `[verify-at-use]` |
| Network / carrier | Varies | Region co-location and fewer media round-trips help | `[ESTIMATE]` `[verify-at-use]` |
| **End-to-end (user stops -> first audio)** | **conversational feel wants sub-second** | Sum of the hops; the number people actually feel | `[ESTIMATE]` `[verify-at-use]` |

> These are order-of-magnitude planning estimates, not guarantees — the **achievable** number depends on the specific models, providers, region, and channel and must be measured end-to-end on the real path. Instrument every hop; the end-to-end round-trip is what the user feels. Fillers/backchannel hide residual latency but don't remove it.

---

## 6. Safety / privacy notes (durable)

| Concept | What it is | Flag |
|---|---|---|
| Call-recording consent | Jurisdiction-dependent one/two-party consent | route to legal — `[verify-at-use]` per jurisdiction |
| Voice-cloning consent | Consent for any cloned/custom voice | route to `trust-and-safety` |
| Sensitive call content | Audio/transcripts may carry PII, payment, health data | do not store beyond task need; minimize + redact |
| Impersonation / disclosure | Whether/how to disclose the caller is an AI | policy + jurisdiction — `[verify-at-use]` |

---

## 7. How to use this file

1. Find the ASR/TTS/platform/telephony detail or latency target you need.
2. Read its retrieval date — if stale or unconfirmed this session, **re-verify** against the cited source type before quoting.
3. Quote it with its flag (`[ESTIMATE]` / `[verify-at-use]`) intact when it informs an architecture or budget commitment.
4. For anything that gates a build decision: confirm against the vendor/provider docs first. For anything touching consent, recording, or disclosure: route to legal / `trust-and-safety`.

---

## See also

- [`voice-ai-decision-trees.md`](voice-ai-decision-trees.md) — the durable cascade-vs-S2S / build-vs-platform / channel / latency-triage trees.
- Deep latency profiling methodology: [`../../performance-engineering/CLAUDE.md`](../../performance-engineering/CLAUDE.md).
- Safety / consent policy: [`../../trust-and-safety/CLAUDE.md`](../../trust-and-safety/CLAUDE.md).
