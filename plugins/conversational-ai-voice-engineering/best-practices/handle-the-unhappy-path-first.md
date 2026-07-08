# Handle the unhappy path first

**Status:** Absolute rule
**Domain:** Dialog / integration
**Applies to:** `conversational-ai-voice-engineering`

> Engineering rule. Provider/telephony specifics are `[verify-at-use]`. No PII; call audio/transcripts are sensitive.

---

## Why this exists

Demos show the happy path; real calls are mostly the unhappy path. Callers go silent, background noise triggers misrecognition, they say something off-topic, a tool call fails, or they get confused and repeat themselves. A voice agent that only handles the clean case falls apart the moment a real person calls — and unlike a screen, there's no visible menu to fall back on. The reprompt, confirmation, fallback, and human-handoff design is most of the actual engineering, so build it first.

## How to apply

- Enumerate the unhappy paths up front: no-input timeout, misrecognition, off-topic input, low confidence, tool failure, repeated confusion.
- Write **reprompts and confirmations** for each — and cap retries so the caller isn't stuck in a loop.
- Treat **tool failure as a dialog branch**, not an exception: say something graceful and offer an alternative or transfer.
- Define **escalation to a human** with a warm transfer (context handed over), triggered by low confidence, explicit request, or out-of-scope.
- Speak a natural acknowledgement during any wait (tool call, lookup) so silence never reads as a dropped call.

**Do:** design silence/error/failure handling before the happy path; test it deliberately.
**Don't:** leave tool failures as unhandled exceptions; dump the caller to a human with no context.

## Edge cases / when the rule does NOT apply

A tightly-scoped, single-purpose IVR replacement with one deterministic flow has a smaller unhappy-path surface — but it still needs no-input and misrecognition handling; the rule shrinks, it doesn't vanish.

## See also

- [`../skills/dialog-management-and-tool-calling/SKILL.md`](../skills/dialog-management-and-tool-calling/SKILL.md), [`../skills/telephony-and-call-flow-integration/SKILL.md`](../skills/telephony-and-call-flow-integration/SKILL.md)
- Template: [`../templates/voice-agent-architecture.md`](../templates/voice-agent-architecture.md)

## Provenance

Codifies `dialog-and-integration-engineer` and `voice-ai-architect` house opinion on fallback design. Telephony/transfer specifics: [`../knowledge/voice-ai-reference-2026.md`](../knowledge/voice-ai-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
