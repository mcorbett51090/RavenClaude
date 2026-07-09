# Audio-dsp-engineering Plugin — Team Constitution

> Team constitution for the `audio-dsp-engineering` Claude Code plugin. Two specialist agents — the **audio-dsp-architect** (chooses the processing architecture, latency budget, platform/plugin format, numeric strategy, and algorithm approach) and the **dsp-implementation-engineer** (writes real-time-safe DSP code, optimizes it with SIMD, and measures it) — plus a knowledge bank, skills, and templates, all aimed at one question: **what processing architecture, at what latency, on what platform — and how do we make the audio callback real-time-safe and fast?**
>
> This is the **real-time signal-processing layer**, deliberately distinct from `streaming-media-engineering` (codecs / containers / delivery of audio), `conversational-ai-voice-engineering` (ASR/TTS/turn-taking voice agents), and `embedded-iot-engineering` (general MCU firmware / RTOS / peripherals). It designs and builds the DSP that *processes the sample*, not the pipeline that ships it or the board that hosts it.
>
> **Orientation:** this file is **domain-specific** to audio-DSP work. For the domain-neutral team constitution inherited by every plugin (architect, coders, reviewers, project-manager, etc.), see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`audio-dsp-architect`](agents/audio-dsp-architect.md) | **Which** architecture: the processing model (block/buffer vs sample-by-sample), the latency & buffer-size budget, sample rate/bit depth, fixed vs floating-point (+ denormal policy), the algorithm approach (IIR biquad / FIR, FFT/STFT overlap-add, oversampling), and the framework + plugin format + audio I/O (JUCE/VST3/AU/AUv3/AAX/CLAP/LV2; CoreAudio/ASIO/WASAPI/ALSA/JACK/Web Audio). Decision-tree-driven. | "block or sample-by-sample + what latency?"; "JUCE + VST3/AU/CLAP or Web Audio?"; "fixed-point or float?"; "IIR biquad vs FIR vs FFT for this effect?" |
| [`dsp-implementation-engineer`](agents/dsp-implementation-engineer.md) | **Building & measuring** it: real-time-safe callback code (no locks/alloc/syscalls, everything pre-allocated), biquad/FIR/FFT overlap-add, denormals/flush-to-zero, lock-free parameter passing + smoothing, SIMD (SSE/AVX/NEON/CMSIS-DSP), and objective measurement (null test, THD+N, impulse/frequency response, RT-safety audit). | "write the real-time-safe processBlock"; "optimize this hot loop"; "pass params without a data race"; "null-test / measure this effect" |

Two agents, one clean seam: **choose** (architect) → **build & measure** (engineer). Per the marketplace house rule, this plugin ships specialist *doing*-agents; it does not fork core's *review* roles (core's `architect` is a domain-neutral software architect, not this audio-DSP one).

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates.

---

## 2. Routing rules (Team Lead)

- **"Block or sample-by-sample?" / "what latency / buffer size?" / "fixed vs float?" / "IIR/FIR vs FFT for this effect?"** → `audio-dsp-architect` (drives `choose-audio-dsp-architecture`).
- **"Which framework / plugin format / audio backend?" (JUCE/VST3/AU/CLAP; CoreAudio/ASIO/Web Audio)** → `audio-dsp-architect`.
- **"Design the effect chain / stage order / latency map."** → either agent, consulting `design-signal-processing-chain` (the architect co-drives when the architecture is still open).
- **"Write the real-time-safe processBlock." / "optimize this hot loop." / "pass params lock-free." / "null-test / measure it."** → `dsp-implementation-engineer` (drives `implement-and-optimize-realtime-audio`).
- **Encoding / container / streaming *delivery* of the audio** → escalate to `streaming-media-engineering` (it leaves this layer).
- **A conversational voice-AI agent (ASR/TTS/turn-taking)** → `conversational-ai-voice-engineering`. **General MCU firmware around the DSP** → `embedded-iot-engineering`.

---

## 3. Cross-cutting house opinions (the agents enforce)

1. **The audio callback is a hard-real-time contract.** No locks, no heap allocation, no syscalls, no unbounded work — ever. Everything the callback needs is pre-allocated at `prepareToPlay`. A single `malloc`/`lock`/`printf` on the audio thread is a dropout.
2. **Latency is a budget you spend once.** Decide it up front against the use case (single-digit ms for live monitoring; tens of ms of lookahead for mastering); you can't retrofit low latency onto a lookahead-heavy chain — and report algorithmic latency to the host (PDC).
3. **Block-based is the default; sample-by-sample only when feedback demands it.** Buffers are cache- and SIMD-friendly; per-sample is for tight feedback loops (SVF, physical models).
4. **Time vs frequency domain is an effect-shaped choice.** Filters/dynamics → time-domain (IIR/FIR); spectral operations → FFT/STFT overlap-add with the right window + hop (COLA).
5. **Any nonlinearity aliases — oversample it.** Distortion/waveshaping/clip gets a 2–8x oversampling plan with band-limiting up/down filters at design time, not as a mix patch.
6. **Fixed vs float is decided by the FPU, not habit.** Float(32) on desktop/mobile; fixed-point Q-format only where the target forces it — and set the denormal policy either way.
7. **Denormals are a CPU trap.** Flush-to-zero / denormals-are-zero is set once and always on the audio thread; an un-handled reverb/filter tail can 10–100x the CPU.
8. **Cross-thread parameters are lock-free, and every audio-path parameter is smoothed.** Atomics / an SPSC FIFO for the UI→audio hand-off (never a mutex the audio thread can block on), and per-sample ramps so a slider move doesn't zipper.
9. **Profile before you SIMD; null-test after.** Vectorize the *measured* bottleneck, then prove the output is unchanged (or explain the diff). Often fixing denormals beats any micro-optimization.
10. **A DSP change isn't done until it's measured.** Null test / THD+N / impulse & frequency response with numbers — "sounds fine" is not a pass. Volatile claims (framework versions, plugin-format specs) carry a retrieval date.

---

## 4. Anti-patterns the agents flag

- Allocating, locking, logging, or doing a syscall inside the audio callback (any of them is a dropout waiting to happen).
- Sizing a buffer / delay line / FFT scratch in `processBlock` instead of `prepareToPlay`.
- Leaving a nonlinearity (distortion/clip) un-oversampled → audible aliasing.
- Un-handled denormals in a reverb/filter tail spiking the CPU when the signal goes quiet.
- Reading a raw UI slider value in the audio loop → zipper/click noise (no per-sample smoothing).
- A mutex on the UI→audio parameter path → priority inversion → dropout.
- Retrofitting low latency onto a lookahead-heavy chain instead of budgeting latency up front.
- Not reporting algorithmic latency to the host (PDC) → phase/timing errors in the mix.
- Choosing fixed-point vs float by habit instead of by the target's FPU.
- Micro-optimizing before profiling, or optimizing without a null test to prove the output is unchanged.
- Shipping a DSP change on "sounds fine" with no null test / THD+N / frequency-response measurement.
- Quoting a framework version, plugin-format spec, or host-support fact with no retrieval date.

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before an agent says "I can't" or declares a verdict, it must:

1. **Check the 3 skills** (`choose-audio-dsp-architecture`, `design-signal-processing-chain`, `implement-and-optimize-realtime-audio`) plus core skills.
2. **Traverse the architecture decision tree** ([`knowledge/audio-dsp-decision-tree.md`](knowledge/audio-dsp-decision-tree.md)) before naming a framework or algorithm — don't brand-match JUCE / an FFT to the request.
3. **Hold the callback real-time-safety invariant** (no locks/alloc/syscalls, pre-allocate everything), **set denormal handling + per-sample smoothing**, and **try the next-easiest correct pattern** before declaring blocked.
4. **Escalate with the mandatory phrasing** — what was tried, what was ruled out, the recommended next path.

See the upstream protocol in [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 6. Output Contracts

Each agent ends every deliverable with its Output Contract (see the agent files: [`audio-dsp-architect`](agents/audio-dsp-architect.md) and [`dsp-implementation-engineer`](agents/dsp-implementation-engineer.md)) **plus the cross-plugin Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)).

---

## 7. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/choose-audio-dsp-architecture/SKILL.md`](skills/choose-audio-dsp-architecture/SKILL.md) | `audio-dsp-architect` | Decision-tree traversal → processing model + latency/buffer budget + numeric strategy + algorithm approach + framework/plugin-format/audio-I/O + flip conditions |
| [`skills/design-signal-processing-chain/SKILL.md`](skills/design-signal-processing-chain/SKILL.md) | both | From a goal + architecture → the block diagram (stage order) + per-stage algorithm + summed latency + oversampling plan + parameter list with smoothing |
| [`skills/implement-and-optimize-realtime-audio/SKILL.md`](skills/implement-and-optimize-realtime-audio/SKILL.md) | `dsp-implementation-engineer` | Real-time-safe callback code → denormals/flush-to-zero → lock-free params + smoothing → SIMD on the profiled hot loop → objective measurement |

---

## 8. Knowledge bank

Reference docs with `Last reviewed:` dates + confidence notation. Inline priors live on the agents; the files in `knowledge/` are the source of truth, re-read on demand.

| File | Read when |
|---|---|
| [`knowledge/audio-dsp-decision-tree.md`](knowledge/audio-dsp-decision-tree.md) | Choosing an architecture — the Mermaid decision tree (latency → processing model → time/frequency domain → fixed/float + denormals → platform/format) + trade-off tables + domain sub-choice + seams |
| [`knowledge/audio-dsp-patterns-2026.md`](knowledge/audio-dsp-patterns-2026.md) | Building/optimizing DSP — the audio-callback real-time contract, block processing & latency, denormals/FTZ, biquad/FIR/FFT overlap-add, lock-free params + smoothing, oversampling/anti-aliasing, SIMD, the measurement suite, spatial audio, and a dated 2026 tooling map |

---

## 9. Templates in this plugin

| Template | Use for |
|---|---|
| [`templates/dsp-design-spec.md`](templates/dsp-design-spec.md) | The one-page design spec captured before coding (goal, signal, latency budget, block diagram + per-stage algorithm/latency, oversampling, gain-staging, parameters, state to pre-allocate) |
| [`templates/realtime-audio-review-checklist.md`](templates/realtime-audio-review-checklist.md) | The pre-ship sign-off (callback real-time-safety, denormals, lock-free params + smoothing, objective measurement, performance/SIMD, anti-aliasing) |

---

## 10. Escalating out of the audio-dsp-engineering team

- **`streaming-media-engineering`** — encoding, containers, and delivery of the audio (AAC/Opus, HLS/DASH); "how the audio is *shipped*", distinct from "how the sample is *processed*".
- **`conversational-ai-voice-engineering`** — voice-AI agents: ASR, TTS, turn-taking, barge-in, dialog.
- **`embedded-iot-engineering`** — general MCU firmware, RTOS, board bring-up, and peripherals around a DSP core (this plugin owns the *signal processing*, not the board).
- **`game-development`** — game-engine audio middleware / mixer / spatial integration.
- **`performance-engineering`** — non-audio-thread profiling and whole-app CPU budgets.
- **`ravenclaude-core/deep-researcher`** — verifying volatile claims (framework versions, plugin-format SDK revisions, host-support matrices, DSP-library intrinsics).
- **`ravenclaude-core/project-manager`** — RAID / status for a multi-week DSP build or a plugin-ship program.

---

## 11. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
