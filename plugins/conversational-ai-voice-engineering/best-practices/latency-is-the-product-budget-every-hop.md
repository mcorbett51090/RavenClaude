# Latency is the product — budget every hop

**Status:** Absolute rule
**Domain:** Architecture / performance
**Applies to:** `conversational-ai-voice-engineering`

> Engineering rule. Per-hop and end-to-end latency numbers are `[verify-at-use]`. No PII.

---

## Why this exists

In a voice conversation the user feels every millisecond. A response that lands even a few hundred milliseconds late reads as an awkward, unnatural pause — the single most common reason a voice agent feels robotic. The end-to-end round-trip (user stops speaking -> first audio back) is the sum of every hop: VAD/endpointing, STT final, LLM time-to-first-token, TTS time-to-first-byte, and network. If you don't budget each hop and measure the total, latency creeps in silently and the conversation dies of a thousand small pauses.

## How to apply

- Set an **end-to-end target** for the round-trip (conversational feel wants sub-second first audio, `[verify-at-use]`) and allocate it across the hops as a budget.
- **Instrument every hop** — you can't fix the dominant one if you only see the total.
- **Stream everywhere:** interim STT results, LLM token streaming, and streaming TTS (start speaking on the first token) are the biggest wins.
- When latency can't be removed, **hide it** with natural fillers/backchannel — never dead silence.
- Guard the budget with a regression gate so a model or prompt change doesn't quietly blow it.

**Do:** treat a blown budget at the severity of a wrong answer; measure end-to-end on the real path.
**Don't:** optimize a hop you haven't measured; ship a build that only feels fast in a clean local test.

## Edge cases / when the rule does NOT apply

Asynchronous or non-interactive voice (voicemail transcription, batch narration) has no live turn-taking, so the sub-second round-trip doesn't apply — but any interactive turn is governed by it.

## See also

- [`../skills/voice-agent-architecture-and-latency/SKILL.md`](../skills/voice-agent-architecture-and-latency/SKILL.md)
- Template: [`../templates/voice-latency-budget.md`](../templates/voice-latency-budget.md)

## Provenance

Codifies `voice-ai-architect` house opinion and the latency-budget triage tree. Per-hop targets: [`../knowledge/voice-ai-reference-2026.md`](../knowledge/voice-ai-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
