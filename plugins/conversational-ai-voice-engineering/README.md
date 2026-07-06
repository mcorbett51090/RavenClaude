# conversational-ai-voice-engineering

A RavenClaude plugin: a **conversational voice-AI engineering** specialist team for building production real-time voice agents — the three engines of a voice build: system architecture, the speech pipeline, and dialog + integration.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Engineering judgment — not legal, compliance, or telephony-law advice.** The ASR/TTS/platform/telephony landscape is volatile: every model version, provider price, and latency number carries a retrieval date + `[verify-at-use]` and must be confirmed against the vendor/provider docs before it drives a build commitment. The agents store no PII, and treat call audio and transcripts as sensitive.

## What it's for

Building voice agents well: picking the pipeline shape (cascade STT->LLM->TTS vs a speech-to-speech model) and the platform (Twilio / Vapi / Retell / LiveKit / Pipecat vs from scratch) you won't have to reverse, holding the end-to-end latency budget so the conversation feels natural, getting turn-taking and barge-in right so the user can interrupt, recognizing real-world noisy/accented audio, and connecting to real telephony with a graceful unhappy path and human handoff. This is the speech-and-latency team — distinct from text retrieval (`ai-rag-engineering`) and Claude app-building (`claude-app-engineering`).

## Agents

| Agent | Use for |
|---|---|
| **voice-ai-architect** | Cascade vs speech-to-speech, end-to-end latency budget, turn-taking / barge-in / endpointing strategy, channel choice (telephony / web / SDK), build-vs-platform, guardrails & fallback |
| **speech-pipeline-engineer** | ASR & TTS model/provider choice, streaming transcription, VAD & endpointing tuning, diarization, prosody/SSML, codecs & sample rates, noise robustness, WER |
| **dialog-and-integration-engineer** | Dialog/state, LLM orchestration + mid-call tool calling, SIP/telephony integration, IVR/DTMF, call routing/transfer, conversation-flow testing & eval |

## What's inside

- **4 skills** — voice-agent-architecture-and-latency, speech-recognition-and-synthesis, dialog-management-and-tool-calling, telephony-and-call-flow-integration.
- **Knowledge bank** — [`voice-ai-decision-trees.md`](knowledge/voice-ai-decision-trees.md) (4 Mermaid trees: cascade vs speech-to-speech, build-vs-platform, channel choice telephony-vs-web/app, latency-budget triage) + [`voice-ai-reference-2026.md`](knowledge/voice-ai-reference-2026.md) (dated ASR/TTS/platform/telephony landscape + per-hop latency targets, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — voice-agent architecture, voice latency budget.
- **2 commands** — `/design-voice-agent`, `/plan-voice-latency-budget`.

## Seams

Knowledge-base grounding / retrieval → [`ai-rag-engineering`](../ai-rag-engineering/) · building the LLM/agent app on Claude → [`claude-app-engineering`](../claude-app-engineering/) · contact-center ops & CX → [`customer-support-cx-operations`](../customer-support-cx-operations/) · deep latency profiling → [`performance-engineering`](../performance-engineering/) · abuse / impersonation / voice-cloning consent → [`trust-and-safety`](../trust-and-safety/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install conversational-ai-voice-engineering@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the scope, routing rules, house opinions, and the output contract.
