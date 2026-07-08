---
name: speech-recognition-and-synthesis
description: "Engineer the ASR and TTS layer of a voice agent: choose STT/TTS providers on the channel (narrowband telephony vs wideband web), languages, streaming support, WER, and cost; stream transcription and synthesis to cut latency; tune VAD/endpointing; handle diarization, prosody/SSML, codecs & sample rates, and noise robustness; and measure WER on real audio. Provider/version specifics verify-at-use."
---

# Speech Recognition & Synthesis

The ears and the mouth of the voice agent. A wrong transcript poisons every downstream turn, and endpointing that's mistuned either cuts the user off or adds a dead pause — so ASR/TTS engineering is where the agent feels sharp or sluggish. Build for the channel's real audio and measure on real calls.

> **Engineering judgment, provider landscape is volatile.** ASR/TTS model versions, prices, WER claims, and streaming/feature support change with every release. Every provider/version specific here is `[verify-at-use]` — confirm against the vendor docs before it drives a commitment. No PII; call audio and transcripts are sensitive — don't store them beyond task need.

## Workflow

1. **Match ASR/TTS to the channel and latency budget.** Narrowband telephony (8 kHz) vs wideband web (16 kHz+) change which models perform; take the per-hop budget from `voice-agent-architecture-and-latency`.
2. **Stream everything.** Streaming (interim) transcription and streaming TTS (start speaking on the first LLM token) are the biggest latency wins — batch calls are latency you chose to pay.
3. **Tune VAD/endpointing as a first-class problem.** Energy-based VAD, semantic endpointing, silence thresholds, and minimum-speech duration decide when the agent responds; set measurable targets and coordinate barge-in gating with the dialog layer.
4. **Handle real audio.** Noise suppression, codec/sample-rate handling (µ-law/Opus/PCM), custom vocabulary/phrase biasing (names, SKUs, jargon), diarization for multi-party — this is what keeps WER usable in the field.
5. **Shape the voice.** Voice/model choice, prosody and SSML (pacing, emphasis, pronunciation), and consistent audio format make the agent sound intentional without blowing TTS time-to-first-byte.
6. **Measure WER on representative audio.** Score WER and latency on real calls across accents, noise, and channels — not a clean demo clip.

## Metrics table

| Metric | What it tells you | Flag |
|---|---|---|
| WER on representative real audio | Recognition quality that poisons/serves downstream | `[verify-at-use]` |
| Endpoint latency (silence -> final) | How responsive vs cutting-off the agent is | `[ESTIMATE]` `[verify-at-use]` |
| STT interim/final streaming latency | Latency hidden vs paid | `[verify-at-use]` per provider |
| TTS time-to-first-byte | First-audio latency | `[verify-at-use]` per provider |
| Sample rate / codec (channel) | Which models perform on this audio | `[verify-at-use]` |

## Anti-patterns

- Benchmarking on clean studio audio, then shipping onto 8 kHz noisy phone calls.
- Using batch STT/TTS when streaming is available, and paying the latency.
- Tuning endpointing to a single silence threshold instead of the conversation's feel.
- Shaving the last few ms while WER is still poisoning the turn.

## See also

- Traverse the **latency-budget triage** tree in [`../../knowledge/voice-ai-decision-trees.md`](../../knowledge/voice-ai-decision-trees.md).
- Dated ASR/TTS landscape: [`../../knowledge/voice-ai-reference-2026.md`](../../knowledge/voice-ai-reference-2026.md).
- Sibling skills: [`../voice-agent-architecture-and-latency/SKILL.md`](../voice-agent-architecture-and-latency/SKILL.md), [`../dialog-management-and-tool-calling/SKILL.md`](../dialog-management-and-tool-calling/SKILL.md).
- Best practices: [`../../best-practices/latency-is-the-product-budget-every-hop.md`](../../best-practices/latency-is-the-product-budget-every-hop.md), [`../../best-practices/test-with-real-audio-accents-and-noise.md`](../../best-practices/test-with-real-audio-accents-and-noise.md).
