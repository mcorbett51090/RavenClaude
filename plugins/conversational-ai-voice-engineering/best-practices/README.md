# conversational-ai-voice-engineering — best-practice docs

Named, citable rules for the `conversational-ai-voice-engineering` team's specialists. Each file is **one rule**. Engineering judgment, not legal/compliance advice; ASR/TTS/platform/telephony specifics are `[verify-at-use]`; no PII, and call audio/transcripts are sensitive.

---

## Index

_5 rules across latency, interruption, the unhappy path, evaluation, and real-audio testing._

| Doc | Status | Use when |
|---|---|---|
| [`latency-is-the-product-budget-every-hop.md`](./latency-is-the-product-budget-every-hop.md) | Absolute rule | Any voice build — the end-to-end response latency is the top constraint; a pause the user notices is a bug. |
| [`design-for-barge-in-and-interruption.md`](./design-for-barge-in-and-interruption.md) | Absolute rule | Turn-taking design — if the user can't interrupt the agent, it isn't a conversation. |
| [`handle-the-unhappy-path-first.md`](./handle-the-unhappy-path-first.md) | Absolute rule | Dialog + integration — silence, noise, misrecognition, and tool failure are the common case on real calls. |
| [`measure-task-success-not-just-word-error-rate.md`](./measure-task-success-not-just-word-error-rate.md) | Absolute rule | Evaluation — score whether the caller's goal was met, not just how clean the transcript looks. |
| [`test-with-real-audio-accents-and-noise.md`](./test-with-real-audio-accents-and-noise.md) | Absolute rule | ASR/TTS + QA — clean-audio benchmarks lie; telephony narrowband, noise, and accents are the real test set. |

---

Each rule cites its provenance and carries a `Last reviewed` date. Volatile ASR/TTS/platform/telephony/latency specifics live (dated, verify-at-use) in [`../knowledge/voice-ai-reference-2026.md`](../knowledge/voice-ai-reference-2026.md).
