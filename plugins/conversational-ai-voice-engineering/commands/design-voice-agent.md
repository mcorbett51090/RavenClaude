---
description: "Design a production voice agent: choose cascade vs speech-to-speech, the channel (telephony / web / SDK), and the build-vs-platform bet (Twilio / Vapi / Retell / LiveKit / Pipecat), then allocate the end-to-end latency budget and design turn-taking / barge-in / fallback (model/platform specifics verify-at-use)."
argument-hint: "[use-case + channel + acceptable response latency]"
---

You are running `/conversational-ai-voice-engineering:design-voice-agent`. Use `voice-ai-architect` + the `voice-agent-architecture-and-latency` skill.

> Engineering judgment, not legal/compliance advice. Every model version, platform feature, provider price, and latency number is `[verify-at-use]`. No PII; call audio/transcripts are sensitive.

## Steps
1. Capture the use-case, the channel (how users reach the agent), and the acceptable end-to-end response latency.
2. Traverse the **cascade vs speech-to-speech**, **channel choice**, and **build-vs-platform** trees in `knowledge/voice-ai-decision-trees.md`.
3. Decide the pipeline shape + channel + build-vs-platform, and allocate the end-to-end latency budget per hop (VAD/endpointing, STT, LLM TTFT, TTS TTFB, network) — each model/platform/latency specific flagged `[verify-at-use]`.
4. Design the turn-taking / barge-in / endpointing model and the unhappy-path + human-transfer fallback; isolate the provider behind a seam.
5. Emit using `templates/voice-agent-architecture.md` + the Structured Output block, handing ASR/TTS engineering to `speech-pipeline-engineer` and dialog/telephony/eval to `dialog-and-integration-engineer`.
