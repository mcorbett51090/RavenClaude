---
description: "Allocate the end-to-end voice latency budget per hop (VAD/endpointing, STT, LLM TTFT, TTS TTFB, network), triage the dominant hop from an end-to-end measurement, and produce an ordered latency-reduction plan that holds sub-second conversational feel (latency numbers verify-at-use)."
argument-hint: "[channel + target response latency + per-hop measurements or the awkward-pause symptom]"
---

You are running `/conversational-ai-voice-engineering:plan-voice-latency-budget`. Use `voice-ai-architect` + `speech-pipeline-engineer` and the `voice-agent-architecture-and-latency` skill.

> Engineering judgment. Every per-hop and end-to-end latency number is `[verify-at-use]`. Measure END-TO-END on the real path, not a clean local test. No PII.

## Steps
1. Set the end-to-end target (conversational feel wants sub-second first audio, `[verify-at-use]`) and confirm every hop is instrumented on the real path.
2. Traverse the **latency-budget triage** tree in `knowledge/voice-ai-decision-trees.md` — confirm an end-to-end measurement exists, then identify the dominant hop (endpointing / STT / LLM TTFT / TTS TTFB / network).
3. Build the ordered reduction plan (stream STT/LLM/TTS -> tune endpointing -> faster LLM/prompt trim -> faster TTS -> co-locate/network), with expected ms recovered and an owner per item.
4. Where latency can't be removed, hide it with fillers/backchannel/speak-partial rather than dead silence, and add a regression gate so a model/prompt change can't quietly blow the budget.
5. Emit using `templates/voice-latency-budget.md` + the Structured Output block, handing ASR/TTS/endpointing tuning to `speech-pipeline-engineer` and orchestration/tool-latency to `dialog-and-integration-engineer`.
