# Voice Latency Budget — <project / channel / date>

> Output template for the end-to-end latency budget allocated per hop and the ordered latency-reduction plan against it. One per pipeline/channel. Every latency number carries a source + date or `[verify-at-use]`; measure END-TO-END on the real path; no PII.

## Header
- **Project / channel:** _telephony / web / app_
- **Target end-to-end response latency (ms):** _user stops -> first audio; sub-second for conversational feel_
- **Prepared:** 2026-__-__  · **Owner:** _____

## 1. Per-hop budget vs measured
| Hop | Budget (ms) | Measured (ms) | Flag |
|---|---|---|---|
| VAD / endpointing decision | | | _[ESTIMATE]_ _[verify-at-use]_ |
| STT final result | | | _[verify-at-use]_ |
| LLM time-to-first-token | | | _[verify-at-use]_ |
| TTS time-to-first-byte | | | _[verify-at-use]_ |
| Network / carrier | | | _[verify-at-use]_ |
| **End-to-end** | | | must be under target |

## 2. Dominant hop
| Item | Value |
|---|---|
| Which hop dominates | |
| Instrumented end-to-end on the real path? | yes / no (must be yes) |
| Streaming enabled? (STT interim / LLM tokens / TTS) | |

## 3. Latency-reduction plan (ordered, highest leverage first)
| # | Action | Owner | Expected ms recovered | Hop it targets |
|---|---|---|---|---|
| 1 | Stream interim STT + LLM tokens + TTS-on-first-token | | | STT/LLM/TTS |
| 2 | Tune VAD/semantic endpointing (shorten trailing silence) | | | endpointing |
| 3 | Faster/smaller LLM or prompt trim for TTFT | | | LLM |
| 4 | Faster TTS voice/model for TTFB | | | TTS |
| 5 | Co-locate hops / closer region / fewer media round-trips | | | network |

## 4. Hide residual latency
- **Fillers / backchannel / speak-partial:** _what covers the wait so silence never reads as a dropped call_

## Headline + actions
- **Headline:** _budget vs measured end-to-end, and the dominant hop_
- **Top 2 actions:** _action — owner — expected ms recovered — by when_
- **Regression gate:** _how the budget is guarded against a model/prompt change blowing it_

---
_Plus the ravenclaude-core Structured Output block. Instrument every hop; the end-to-end round-trip is what the user feels. Seams: voice-ai-architect (budget/target), speech-pipeline-engineer (STT/TTS/endpointing), dialog-and-integration-engineer (orchestration/tool latency)._
