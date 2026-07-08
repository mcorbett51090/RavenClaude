# Changelog — conversational-ai-voice-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-03

Initial release.

### Added

- **3 agents** — `voice-ai-architect` (cascade vs speech-to-speech, end-to-end latency budget, turn-taking/barge-in/endpointing, channel + build-vs-platform, guardrails/fallback), `speech-pipeline-engineer` (ASR & TTS model/provider choice, streaming transcription, VAD/endpointing, diarization, prosody/SSML, codecs & sample rates, noise robustness, WER), `dialog-and-integration-engineer` (dialog/state, LLM orchestration + mid-call tool calling, SIP/telephony, IVR/DTMF, routing/transfer, conversation-flow testing & eval).
- **4 skills** — `voice-agent-architecture-and-latency`, `speech-recognition-and-synthesis`, `dialog-management-and-tool-calling`, `telephony-and-call-flow-integration`.
- **Knowledge bank** — `voice-ai-decision-trees.md` (4 Mermaid trees: cascade vs speech-to-speech, build-vs-platform, channel choice telephony-vs-web/app, latency-budget triage) and `voice-ai-reference-2026.md` (dated reference: ASR provider/model landscape, TTS provider/voice landscape, voice-platform/orchestration landscape, telephony protocols SIP/PSTN/WebRTC, per-hop latency targets `[ESTIMATE]` — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — latency is the product (budget every hop), design for barge-in and interruption, handle the unhappy path first, measure task success not just word error rate, test with real audio/accents/noise.
- **2 templates** — voice-agent-architecture, voice-latency-budget.
- **2 commands** — `/design-voice-agent`, `/plan-voice-latency-budget`.

### Scope & verify-at-use

- **Engineering judgment, not legal, compliance, or telephony-law advice.** The agents store no PII and treat call audio/transcripts as sensitive.
- The ASR/TTS/platform/telephony landscape is volatile — every model version, provider price, latency number, and feature-support claim in `voice-ai-reference-2026.md` carries a retrieval date + `[verify-at-use]`; re-confirm against the vendor/provider docs before quoting or committing.
- Seams to `ai-rag-engineering` (retrieval/grounding), `claude-app-engineering` (LLM/agent app), `customer-support-cx-operations` (contact-center ops/CX), `performance-engineering` (deep latency profiling), and `trust-and-safety` (abuse/impersonation/voice-cloning consent).
