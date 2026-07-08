# Conversational Voice-AI Engineering — Decision Trees

> Reference decision trees for the `conversational-ai-voice-engineering` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Engineering judgment, not legal/compliance advice.** Anything touching an ASR/TTS model version, provider price, platform feature, telephony protocol detail, or latency number is `[verify-at-use]` — confirm against the vendor/provider docs before it drives a build commitment. No PII; call audio/transcripts are sensitive.
>
> _Last reviewed: 2026-07-03 by `claude`. Principles are durable; dated specifics live in [`voice-ai-reference-2026.md`](voice-ai-reference-2026.md)._

---

## Decision Tree: cascade vs speech-to-speech?

```mermaid
flowchart TD
    A[New voice agent] --> B{Need transcripts, swappable<br/>components, or mid-turn tool calls?}
    B -- "yes — auditability,<br/>function calling, control" --> C[Cascade: STT -> NLU/LLM -> TTS]
    B -- "no — natural prosody +<br/>lowest latency dominate" --> D{Latency-critical, expressive,<br/>tolerant of less control?}
    D -- yes --> E[Speech-to-speech model<br/>lower latency, richer prosody]
    D -- "no / unsure" --> C
    C --> F{Per-hop latency stacking<br/>within budget? verify-at-use}
    F -- no --> G[Trim hops: streaming STT/TTS,<br/>faster LLM, or reconsider S2S]
    F -- yes --> H[Commit cascade;<br/>allocate budget per hop]
    E --> I{Need mid-call tools<br/>or transcripts?}
    I -- yes --> J[Hybrid: S2S + tool/transcript<br/>side-channel, or fall back to cascade]
    I -- no --> K[Commit S2S; watch<br/>observability + control gaps]
```

**Rule:** choose on the **use-case**, not the hype. Cascade buys transcripts, swappable components, and mid-turn tool calling at the cost of stacked per-hop latency; speech-to-speech buys latency and prosody at the cost of control and observability. If you need tools/transcripts, default cascade; reach for S2S when latency and expressiveness dominate and control can give. All model/latency specifics `[verify-at-use]`.

---

## Decision Tree: build-vs-platform?

```mermaid
flowchart TD
    A[Voice agent to ship] --> B{Time-to-market vs<br/>control priority?}
    B -- "fastest to production,<br/>standard call flows" --> C[Managed platform<br/>Vapi / Retell — verify-at-use]
    B -- "need custom media/orchestration,<br/>own the stack" --> D{Have real-time media +<br/>speech engineering capacity?}
    D -- "yes — strong team" --> E[Framework: LiveKit / Pipecat<br/>self-orchestrated, more control]
    D -- "telephony primitives only" --> F[Twilio / telephony provider<br/>+ your own orchestration]
    C --> G{Platform supports the channel,<br/>tools, and latency you need? verify-at-use}
    F --> G
    E --> G
    G -- no --> H[Re-scope: change platform,<br/>self-host a hop, or hybrid]
    G -- yes --> I[Commit; isolate provider<br/>behind seams for portability]
```

**Rule:** trade time-to-market against control. A managed platform ships fastest for standard flows; a framework (LiveKit/Pipecat) gives control at the cost of engineering; raw telephony primitives (Twilio) mean you own orchestration. Whatever you pick, isolate the provider behind seams so a later swap is a change, not a rebuild. Feature/price specifics `[verify-at-use]`.

---

## Decision Tree: channel choice (telephony vs web/app)?

```mermaid
flowchart TD
    A[Where does the agent live?] --> B{How do users reach it?}
    B -- "dial a phone number,<br/>legacy reach" --> C[Telephony: SIP/PSTN<br/>8 kHz narrowband, DTMF, carrier latency]
    B -- "in a browser" --> D[WebRTC in the browser<br/>wideband, lower transport latency]
    B -- "in a native/mobile app" --> E[SDK / WebRTC in-app<br/>wideband, device audio control]
    B -- "several of the above" --> F[Shared streaming core<br/>+ per-channel media seams]
    C --> G{Codec + sample rate handled?<br/>µ-law 8 kHz — verify-at-use}
    D --> H{Codec + sample rate handled?<br/>Opus wideband — verify-at-use}
    E --> H
    F --> G
    G --> I[Commit; ASR/TTS chosen for<br/>the channel's audio]
    H --> I
```

**Rule:** the channel fixes the media constraints. Telephony (SIP/PSTN) is 8 kHz narrowband with DTMF and carrier latency; WebRTC (browser/app) is wideband with lower transport latency. For multi-surface, build a shared streaming core with per-channel media seams and pick ASR/TTS for the channel's actual audio. Codec/sample-rate specifics `[verify-at-use]`.

---

## Decision Tree: latency-budget triage

```mermaid
flowchart TD
    A[Awkward pause / agent feels slow] --> B{Measured the round-trip<br/>per hop? end-to-end}
    B -- no --> C[Instrument every hop first:<br/>VAD/endpoint, STT final, LLM TTFT, TTS TTFB, network]
    B -- yes --> D{Which hop dominates?}
    D -- "endpointing waits too long" --> E[Tune VAD/semantic endpointing;<br/>shorten silence threshold — speech-pipeline]
    D -- "STT final too slow" --> F[Stream interim results;<br/>faster/streaming ASR — speech-pipeline]
    D -- "LLM time-to-first-token" --> G[Smaller/faster model, prompt trim,<br/>stream tokens, speak-while-thinking]
    D -- "TTS time-to-first-byte" --> H[Streaming TTS, start on first token;<br/>faster voice/model]
    D -- "network / carrier" --> I[Co-locate hops, closer region,<br/>reduce media round-trips]
    E --> J{Under end-to-end target now?}
    F --> J
    G --> J
    H --> J
    I --> J
    J -- no --> K[Hide residual latency: fillers,<br/>backchannel, speak partial]
    J -- yes --> L[Lock budget; guard with a regression gate]
```

**Rule:** instrument **every hop** before optimizing, fix the **dominant** hop (endpointing, STT, LLM TTFT, TTS TTFB, network), and stream wherever possible. When latency can't be removed, hide it with natural fillers/backchannel rather than dead silence. Per-hop targets `[verify-at-use]`.

---

## See also

- [`voice-ai-reference-2026.md`](voice-ai-reference-2026.md) — dated ASR/TTS/platform/telephony landscape + per-hop latency targets (verify-at-use).
- Skills: [`../skills/voice-agent-architecture-and-latency/SKILL.md`](../skills/voice-agent-architecture-and-latency/SKILL.md), [`../skills/speech-recognition-and-synthesis/SKILL.md`](../skills/speech-recognition-and-synthesis/SKILL.md), [`../skills/dialog-management-and-tool-calling/SKILL.md`](../skills/dialog-management-and-tool-calling/SKILL.md), [`../skills/telephony-and-call-flow-integration/SKILL.md`](../skills/telephony-and-call-flow-integration/SKILL.md).
