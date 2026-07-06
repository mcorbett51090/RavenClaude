---
name: telephony-and-call-flow-integration
description: "Integrate a voice agent with real telephony and validate it: SIP/PSTN trunking and media handling, WebRTC for web/app, DTMF capture (in-band vs RFC 2833/SIP INFO), IVR-vs-conversational per step, call routing and warm/cold human transfer with context, and a voice-agent eval harness scoring task success, WER, end-to-end latency, and interruption handling on representative recorded calls. Protocol/provider specifics verify-at-use."
---

# Telephony & Call-Flow Integration

The plumbing that connects the agent to real callers, and the harness that proves it works. Recognition and dialog don't matter if the call never connects, the keypad input is dropped, or the human transfer is a cold dump. And you only know the agent is good if you measure task success on real conversations.

> **Engineering judgment, not legal/compliance advice.** You wire telephony; you do not adjudicate call-recording consent, TCPA/robocall law, or PCI/HIPAA handling — route those to legal / `trust-and-safety`. Protocol/provider specifics carry a retrieval date + `[verify-at-use]`. No PII; call audio and transcripts are sensitive.

## Workflow

1. **Wire the channel.** SIP/PSTN trunking and media (RTP) for phone reach, or WebRTC for browser/app. Confirm the codec and sample rate so ASR/TTS get the right audio format (`[verify-at-use]`).
2. **Capture DTMF.** Keypad input still matters (menus, digits, confirmations). Confirm the DTMF path for your provider — in-band tones vs RFC 2833 vs SIP INFO differ.
3. **Decide IVR-vs-conversational per step.** Some steps (authentication, menu) are better as deterministic IVR/DTMF; others are conversational. Mix deliberately.
4. **Design routing and transfer.** Routing rules that fit the call flow, and a **warm** transfer (context handed to the human agent) rather than a cold dump. Define the escalation triggers up front.
5. **Handle call-control failures.** Dropped calls, no-answer, trunk failures, and mid-call transfer failures are branches, not surprises.
6. **Build the eval harness.** Score **task success** (did the caller's goal get met) alongside WER, end-to-end latency, and interruption/barge-in handling over representative recorded conversations — with a regression gate so changes don't quietly break the flow.

## Metrics table

| Metric | What it tells you | Flag |
|---|---|---|
| Task-success rate (eval set) | The agent's real quality score | primary |
| Call-connect / drop rate | Telephony plumbing health | `[verify-at-use]` per provider |
| DTMF capture reliability | Keypad path correctness | `[verify-at-use]` |
| Warm-transfer success + context carried | Clean human handoff | n/a |
| End-to-end latency + interruption handling | Conversational feel under load | `[ESTIMATE]` `[verify-at-use]` |

## Anti-patterns

- Cold-dumping a caller to a human with no context.
- Assuming one DTMF capture path works across every provider/trunk.
- Making every step conversational when a deterministic IVR/DTMF step is safer.
- Shipping without an eval set, so regressions surface as angry callers.

## See also

- Traverse the **channel choice** and **build-vs-platform** trees in [`../../knowledge/voice-ai-decision-trees.md`](../../knowledge/voice-ai-decision-trees.md).
- Dated telephony/protocol landscape: [`../../knowledge/voice-ai-reference-2026.md`](../../knowledge/voice-ai-reference-2026.md).
- Sibling skills: [`../dialog-management-and-tool-calling/SKILL.md`](../dialog-management-and-tool-calling/SKILL.md), [`../voice-agent-architecture-and-latency/SKILL.md`](../voice-agent-architecture-and-latency/SKILL.md).
- Best practices: [`../../best-practices/handle-the-unhappy-path-first.md`](../../best-practices/handle-the-unhappy-path-first.md), [`../../best-practices/measure-task-success-not-just-word-error-rate.md`](../../best-practices/measure-task-success-not-just-word-error-rate.md).
- Contact-center operations & CX: [`../../../customer-support-cx-operations/CLAUDE.md`](../../../customer-support-cx-operations/CLAUDE.md).
