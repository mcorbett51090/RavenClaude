---
name: voice-agent-architecture-and-latency
description: "Choose the voice-agent pipeline shape (cascade STT->LLM->TTS vs speech-to-speech), the channel (telephony / web / SDK), and the build-vs-platform bet (Twilio / Vapi / Retell / LiveKit / Pipecat), then allocate the end-to-end latency budget per hop and design the turn-taking / barge-in / fallback model. Model/platform/latency specifics verify-at-use."
---

# Voice-Agent Architecture & Latency

The first and most expensive voice-AI decision: what pipeline shape you build, on what platform, over what channel — and the latency budget it all has to live inside. Everything downstream — the ASR/TTS latency the pipeline engineer must hold, the turn-taking the dialog engineer can build — is fixed by this choice, so make it deliberately. In voice, latency is the product.

> **Engineering judgment, landscape is volatile.** Model versions, platform features, and provider prices change with every release. Every model/platform/latency specific here is `[verify-at-use]` — confirm against the vendor/provider docs before it drives a build commitment. No PII; call audio/transcripts are sensitive.

## Workflow

1. **State the use-case, channel, and acceptable response latency.** Inbound support, outbound reminders, in-app assistant, and IVR replacement have different latency, control, and telephony needs.
2. **Choose cascade vs speech-to-speech on the use-case.** Cascade (STT -> LLM -> TTS) buys transcripts, swappable components, and mid-turn tool calling; speech-to-speech buys latency and prosody at the cost of control/observability. Name the trade.
3. **Pick the channel.** Telephony (SIP/PSTN, 8 kHz narrowband, DTMF), WebRTC (browser/app, wideband), or SDK — the channel fixes the media constraints and part of the latency.
4. **Decide build-vs-platform.** Managed platform (Vapi/Retell) for speed, framework (LiveKit/Pipecat) for control, telephony primitives (Twilio) + your orchestration, or from scratch. Isolate the provider behind seams.
5. **Allocate the end-to-end latency budget per hop.** VAD/endpointing + STT final + LLM TTFT + TTS TTFB + network must sum under the target (conversational feel wants sub-second first audio, `[verify-at-use]`). Hand the per-hop targets to `speech-recognition-and-synthesis`.
6. **Design turn-taking, barge-in, and fallback in.** Endpointing, interruption, and the unhappy path (silence, ASR error, LLM stall, human handoff) are architecture, not later tickets.

## Metrics table

| Decision input | What it tells you | Flag |
|---|---|---|
| Target end-to-end response latency (ms) | The budget every hop shares | `[verify-at-use]` |
| Need for transcripts / mid-call tools | Cascade vs speech-to-speech | `[verify-at-use]` |
| Channel (phone / web / app / SDK) | Media constraints + transport latency | `[verify-at-use]` per channel |
| Control-vs-speed priority | Build-vs-platform bet | `[verify-at-use]` platform features |
| Barge-in / interruption requirement | Turn-taking model complexity | n/a |

## Anti-patterns

- Choosing speech-to-speech for its "naturalness" when the use-case needs mid-call tool calling and transcripts.
- Picking a platform on brand familiarity without checking it supports your channel, tools, and latency.
- Deferring the latency budget until after the pipeline is wired.
- Treating barge-in and the unhappy path as polish instead of architecture.

## See also

- Traverse the **cascade vs speech-to-speech**, **build-vs-platform**, and **channel choice** trees in [`../../knowledge/voice-ai-decision-trees.md`](../../knowledge/voice-ai-decision-trees.md).
- Dated landscape: [`../../knowledge/voice-ai-reference-2026.md`](../../knowledge/voice-ai-reference-2026.md).
- Sibling skills: [`../speech-recognition-and-synthesis/SKILL.md`](../speech-recognition-and-synthesis/SKILL.md), [`../telephony-and-call-flow-integration/SKILL.md`](../telephony-and-call-flow-integration/SKILL.md).
- Best practices: [`../../best-practices/latency-is-the-product-budget-every-hop.md`](../../best-practices/latency-is-the-product-budget-every-hop.md), [`../../best-practices/design-for-barge-in-and-interruption.md`](../../best-practices/design-for-barge-in-and-interruption.md).
- Template: [`../../templates/voice-agent-architecture.md`](../../templates/voice-agent-architecture.md).
