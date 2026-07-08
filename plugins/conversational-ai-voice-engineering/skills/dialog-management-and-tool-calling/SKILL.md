---
name: dialog-management-and-tool-calling
description: "Design the dialog layer of a voice agent: explicit dialog-state modeling, LLM orchestration, context/window management over a long call, and mid-call function/tool calling that hides latency with natural fillers and treats tool failure as a first-class branch. Design the unhappy path (silence, misrecognition, tool failure, confusion) before the happy path. Provider/SDK specifics verify-at-use."
---

# Dialog Management & Tool Calling

What happens between the ear and the mouth. Recognition and speech are necessary but not sufficient — the conversation only works if the agent tracks state, calls the right tool at the right moment without a dead pause, and handles the confusion and failure that fill real calls. Build the unhappy path first.

> **Engineering judgment.** LLM/provider/SDK behavior and tool-calling APIs move; specifics carry a retrieval date + `[verify-at-use]`. No PII; call audio and transcripts are sensitive.

## Workflow

1. **Model the dialog state explicitly.** Track where the conversation is, what's collected, and what's pending; manage the LLM context window so long calls don't drift or overflow. A voice agent that loses the thread is worse than an IVR.
2. **Orchestrate the LLM for voice.** Stream tokens so TTS can start early, keep prompts tight for time-to-first-token, and decide what the agent says while it thinks.
3. **Call tools mid-call without a dead pause.** Decide when the LLM invokes a function (lookup, booking, payment), speak a natural filler/acknowledgement while it runs, and handle tool failure as a first-class branch, not an exception.
4. **Design the unhappy path first.** No-input timeouts, misrecognition, off-topic input, tool failure, and repeated confusion are the common case — write the reprompts, confirmations, and fallbacks before the happy path.
5. **Define escalation to a human.** Low confidence, explicit request, and out-of-scope trigger a warm transfer with context (see `telephony-and-call-flow-integration`).
6. **Keep it measurable.** Every change is checked against task success and interruption handling, not just whether it sounds fine once.

## Metrics table

| Metric | What it tells you | Flag |
|---|---|---|
| Task-success / completion rate | Whether the caller's goal was met | primary score |
| Mid-call tool latency (hidden vs felt) | Whether fillers cover the tool call | `[ESTIMATE]` `[verify-at-use]` |
| Context/window overflow on long calls | Whether the agent keeps the thread | `[verify-at-use]` per model |
| Reprompt / fallback coverage | Unhappy-path robustness | n/a |
| Escalation-trigger correctness | Clean handoff vs stuck loop | n/a |

## Anti-patterns

- Letting the call go silent during a tool call instead of speaking an acknowledgement.
- Treating tool failure as an unhandled exception instead of a dialog branch.
- Building the happy path first and bolting on reprompts later.
- Measuring the transcript's cleanliness instead of whether the goal was met.

## See also

- Traverse the **channel choice** and **build-vs-platform** trees in [`../../knowledge/voice-ai-decision-trees.md`](../../knowledge/voice-ai-decision-trees.md).
- Dated platform/provider landscape: [`../../knowledge/voice-ai-reference-2026.md`](../../knowledge/voice-ai-reference-2026.md).
- Sibling skills: [`../telephony-and-call-flow-integration/SKILL.md`](../telephony-and-call-flow-integration/SKILL.md), [`../speech-recognition-and-synthesis/SKILL.md`](../speech-recognition-and-synthesis/SKILL.md).
- Best practices: [`../../best-practices/handle-the-unhappy-path-first.md`](../../best-practices/handle-the-unhappy-path-first.md), [`../../best-practices/measure-task-success-not-just-word-error-rate.md`](../../best-practices/measure-task-success-not-just-word-error-rate.md).
- Building the LLM/agent app on Claude: [`../../../claude-app-engineering/CLAUDE.md`](../../../claude-app-engineering/CLAUDE.md).
