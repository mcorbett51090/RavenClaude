# Design for barge-in and interruption

**Status:** Absolute rule
**Domain:** Turn-taking / interaction
**Applies to:** `conversational-ai-voice-engineering`

> Engineering rule. Endpointing/barge-in tuning specifics are `[verify-at-use]`. No PII.

---

## Why this exists

Real human conversation is full of interruption: people cut in, correct, and change their minds mid-sentence. An agent that must finish its full utterance before it will listen again is not a conversation — it's a voicemail menu. Barge-in (letting the user interrupt the agent's speech) and good endpointing (knowing when the user is actually done) are what make a voice agent feel like a partner rather than a recording. They are load-bearing turn-taking, not polish.

## How to apply

- **Support barge-in:** when the user starts speaking, stop TTS playback promptly and start listening — don't talk over them.
- **Tune endpointing to the conversation, not a single silence threshold.** Too eager cuts users off mid-sentence; too slow adds a dead pause. Use semantic endpointing where it helps, and measure against real audio.
- **Gate barge-in against false triggers** (backchannel "mm-hm", background noise) so the agent doesn't stop every time it hears a cough — coordinate VAD sensitivity with the speech pipeline.
- **Recover gracefully after an interruption:** drop or re-plan the interrupted utterance instead of resuming a now-stale sentence.

**Do:** treat barge-in as a first-class turn-taking requirement; validate it in playtests.
**Don't:** lock the user out until the agent finishes; tune endpointing once and never against real callers.

## Edge cases / when the rule does NOT apply

Compliance-mandated disclosures (legal notices, recording disclosure) may need to play in full — but flag those explicitly; they are the exception, not the default.

## See also

- [`../skills/voice-agent-architecture-and-latency/SKILL.md`](../skills/voice-agent-architecture-and-latency/SKILL.md), [`../skills/speech-recognition-and-synthesis/SKILL.md`](../skills/speech-recognition-and-synthesis/SKILL.md)
- Decision tree: [`../knowledge/voice-ai-decision-trees.md`](../knowledge/voice-ai-decision-trees.md) (latency-budget triage)

## Provenance

Codifies `voice-ai-architect` and `speech-pipeline-engineer` house opinion on turn-taking. Endpointing specifics: [`../knowledge/voice-ai-reference-2026.md`](../knowledge/voice-ai-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
