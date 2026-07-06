# Voice-Agent Architecture — <project / date>

> Output template for the pipeline/channel/platform decision and the turn-taking + fallback architecture that follows. One per project (revisit on a pipeline/channel change). Every model/version/platform/latency cell carries a source + date or `[verify-at-use]`; no PII, and call audio/transcripts are sensitive.

## Header
- **Project / use-case:** _____
- **Channel(s) & how users reach it:** _phone (SIP/PSTN) / web (WebRTC) / app (SDK)_
- **Target end-to-end response latency (ms):** _____
- **Prepared:** 2026-__-__  · **Owner:** _____

## 1. Pipeline shape
| Decision | Choice | Basis | Flag |
|---|---|---|---|
| Cascade (STT->LLM->TTS) vs speech-to-speech | | need for transcripts / mid-call tools vs latency/prosody | _[verify-at-use]_ |
| Reason it won | | | n/a |

## 2. Channel & platform
| Decision | Choice | Basis | Flag |
|---|---|---|---|
| Channel (telephony / WebRTC / SDK) | | how users reach it; media constraints | _[verify-at-use]_ |
| Build-vs-platform (Twilio / Vapi / Retell / LiveKit / Pipecat / scratch) | | speed vs control | _[verify-at-use]_ |
| Provider isolation seam | | so a later swap is a change, not a rebuild | n/a |

## 3. Latency budget (per hop)
| Hop | Target (ms) | Flag |
|---|---|---|
| VAD / endpointing | | _[ESTIMATE]_ _[verify-at-use]_ |
| STT final | | _[verify-at-use]_ |
| LLM time-to-first-token | | _[verify-at-use]_ |
| TTS time-to-first-byte | | _[verify-at-use]_ |
| Network / carrier | | _[verify-at-use]_ |
| **End-to-end (user stops -> first audio)** | | must sum under target |

## 4. Turn-taking & fallback
- **Barge-in:** _how the user interrupts; TTS-stop behavior_
- **Endpointing model:** _energy VAD / semantic; silence threshold_
- **Unhappy path:** _no-input / misrecognition / tool failure / confusion reprompts_
- **Human transfer:** _trigger + warm-transfer context_
- **Guardrails:** _off-script / confidence / disclosure handling_

## Headline + risks
- **Headline decision:** _the pipeline + channel + platform bet, in one line_
- **Top risks:** _the reversal-expensive assumptions + how they're verified_
- **Two things that would change the answer:** _____

---
_Plus the ravenclaude-core Structured Output block. All model/version/platform/latency cells: verify-at-use before commitment. Seams: speech-pipeline-engineer (ASR/TTS + endpointing), dialog-and-integration-engineer (dialog/telephony/eval)._
