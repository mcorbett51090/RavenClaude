# Measure task success, not just word error rate

**Status:** Absolute rule
**Domain:** Evaluation
**Applies to:** `conversational-ai-voice-engineering`

> Engineering rule. Eval-metric specifics are `[verify-at-use]`. No PII; call audio/transcripts are sensitive.

---

## Why this exists

Word error rate (WER) tells you how well the ASR transcribed the audio — not whether the agent accomplished what the caller called for. An agent can have a beautiful transcript and a 0% completion rate: it heard every word and still failed to book the appointment, look up the order, or resolve the issue. WER, latency, and interruption handling are necessary component metrics, but the score that decides whether the agent is good is **task success** — did the caller's goal get met. Optimize the transcript and ignore the outcome and you'll ship a fluent failure.

## How to apply

- Define **task success** per use-case (goal met / not met) and make it the headline metric.
- Build an **eval harness over representative recorded conversations** — real accents, noise, channels, and unhappy paths — not a handful of clean clips.
- Track WER, end-to-end latency, and interruption/barge-in handling **alongside** task success as diagnostics that explain a failure.
- Put a **regression gate** on the eval set so a model, prompt, or flow change that drops task success is caught before it ships.
- Re-run the eval on every meaningful change; a voice flow is easy to break silently.

**Do:** lead with task success; use WER/latency to explain *why* a call failed.
**Don't:** declare success from a clean transcript; eval only on clean demo audio.

## Edge cases / when the rule does NOT apply

Pure transcription products (captioning, dictation) legitimately optimize WER as the primary metric — there's no downstream "task" beyond the transcript. Interactive agents are governed by task success.

## See also

- [`../skills/dialog-management-and-tool-calling/SKILL.md`](../skills/dialog-management-and-tool-calling/SKILL.md), [`../skills/telephony-and-call-flow-integration/SKILL.md`](../skills/telephony-and-call-flow-integration/SKILL.md)
- Decision tree: [`../knowledge/voice-ai-decision-trees.md`](../knowledge/voice-ai-decision-trees.md)

## Provenance

Codifies `dialog-and-integration-engineer` house opinion on eval. Metric specifics: [`../knowledge/voice-ai-reference-2026.md`](../knowledge/voice-ai-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
