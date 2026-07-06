# Test with real audio, accents, and noise

**Status:** Absolute rule
**Domain:** ASR/TTS / QA
**Applies to:** `conversational-ai-voice-engineering`

> Engineering rule. Provider/WER specifics are `[verify-at-use]`. No PII; call audio/transcripts are sensitive.

---

## Why this exists

Clean-audio benchmarks lie. A voice agent that transcribes a studio-quality clip flawlessly can fall apart on a real call: 8 kHz narrowband telephony, background noise, cross-talk, phone-speaker distortion, and the full range of human accents and speaking styles are a completely different signal. If your test set is a few clean clips in one accent, you're measuring a system you'll never ship. The real test set is the audio your callers actually produce.

## How to apply

- **Build a representative test set:** real recorded calls (with consent), across accents, noise conditions, channels (telephony narrowband vs wideband web), and speaking styles.
- **Measure WER and endpointing on that set**, not on clean demo audio — the field WER is the one that governs downstream quality.
- **Test the channel's real codec/sample rate** (µ-law 8 kHz for telephony, Opus for web) so the ASR gets the audio it'll actually receive.
- **Use phrase biasing / custom vocabulary** for the names, SKUs, and jargon your domain requires, and verify it on real utterances.
- **Handle audio as sensitive:** minimize retention, redact PII, and secure any stored recordings/transcripts.

**Do:** treat the on-real-audio capture as the source of truth; test across accents and noise.
**Don't:** trust clean-clip WER; ship an ASR choice validated only on wideband studio audio.

## Edge cases / when the rule does NOT apply

Early prototyping can iterate on clean audio for speed — but any WER, comfort, or quality claim must be confirmed on representative real audio before it's trusted or drives a provider decision.

## See also

- [`../skills/speech-recognition-and-synthesis/SKILL.md`](../skills/speech-recognition-and-synthesis/SKILL.md)
- Dated ASR/TTS landscape: [`../knowledge/voice-ai-reference-2026.md`](../knowledge/voice-ai-reference-2026.md)

## Provenance

Codifies `speech-pipeline-engineer` house opinion on measuring on real audio. Provider/WER specifics: [`../knowledge/voice-ai-reference-2026.md`](../knowledge/voice-ai-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
