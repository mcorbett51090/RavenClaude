# audio-dsp-engineering

> The **real-time signal-processing layer** for Claude Code — the team that answers *"what processing architecture, at what latency, on what platform — and how do we make the audio callback real-time-safe and fast?"* and builds the DSP that proves the answer. Two agents: the **audio-dsp-architect** (chooses the architecture, latency budget, platform/plugin format, numeric strategy, and algorithm approach) and the **dsp-implementation-engineer** (writes real-time-safe DSP code, optimizes it with SIMD, and measures it).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Block-based or sample-by-sample, and what latency/buffer size?" | A decision-tree-driven processing model + latency & buffer-size budget grounded in the use case, with the conditions that would flip it |
| "JUCE + VST3/AU/CLAP, or Web Audio AudioWorklet — and which audio backend?" | A framework + plugin-format + audio-I/O choice (CoreAudio/ASIO/WASAPI/ALSA/JACK) with the host/OS trade-offs |
| "Fixed-point or floating-point for this target?" | A fixed vs float verdict (Q-format if fixed), the denormal/flush-to-zero policy, and the headroom/dither plan |
| "IIR biquad, FIR, or an FFT/STFT approach for this effect?" | An algorithm-family choice with the latency/CPU/aliasing trade-offs, plus the oversampling factor for any nonlinearity |
| "Write the real-time-safe processBlock for this effect." | Callback code with no locks/allocation/syscalls, block processing, denormal handling, and lock-free parameter smoothing |
| "This reverb/filter spikes CPU — optimize it." | A profiled, SIMD-vectorized (SSE/NEON) hot loop with flush-to-zero set, measured before/after and null-tested |
| "Prove this effect is correct." | A measurement harness: null test, THD+N, impulse/frequency response, and a real-time-safety audit — pass/fail with numbers |

**Two rules it never breaks:** *the audio callback is hard-real-time* (no locks, no allocation, no syscalls, no unbounded work — everything pre-allocated at prepare time), and *a DSP change isn't done until it's measured* (null test / THD+N / frequency response with numbers, not "sounds fine").

## What's inside

- **2 agents** — `audio-dsp-architect` (chooses the processing model, latency budget, platform/plugin format, fixed-vs-float, and algorithm approach) and `dsp-implementation-engineer` (writes real-time-safe DSP, handles denormals, passes parameters lock-free, vectorizes with SIMD, and measures).
- **3 skills** — `choose-audio-dsp-architecture`, `design-signal-processing-chain`, `implement-and-optimize-realtime-audio`.
- **2 knowledge files** — a Mermaid audio-DSP architecture decision tree (+ trade-off tables + time-vs-frequency sub-choice) and a 2026 audio-DSP-patterns reference (the callback contract, block processing, denormals, biquad/FIR/FFT overlap-add, lock-free params, oversampling, SIMD, the measurement suite, spatial audio, tooling map).
- **2 templates** — a DSP design spec and a real-time-audio review checklist.

## Where it sits in the audio stack

```
audio-dsp-engineering (HERE)   →  PROCESS the sample in real time          ("filters, FX, the callback, at latency")
streaming-media-engineering    →  encode / container / deliver the audio   ("how the audio is shipped")
conversational-ai-voice-eng    →  ASR / TTS / turn-taking voice agents      ("the voice AI")
embedded-iot-engineering       →  MCU firmware / RTOS / peripherals         ("the board around a DSP core")
game-development               →  engine audio middleware / mixer           ("the game's audio integration")
```

This plugin is the **real-time DSP layer**: it designs and builds the signal processing itself, and stays clear of the *delivery* pipeline (`streaming-media-engineering`), the *voice-AI* stack (`conversational-ai-voice-engineering`), and the *board bring-up* (`embedded-iot-engineering`) around a DSP core.

## Domain stance

Concept-first (the audio-callback real-time contract, block vs sample-by-sample, latency budgeting, time- vs frequency-domain, fixed-vs-float + denormals, oversampling/anti-aliasing, lock-free parameter passing + smoothing, the null-test/THD+N/frequency-response measurement suite), fluent across **JUCE / iPlug2 / Web Audio AudioWorklet**, the **VST3 / AU / AUv3 / AAX / CLAP / LV2** plugin formats, the **CoreAudio / ASIO / WASAPI / ALSA / JACK** audio backends, and embedded DSP (**ARM CMSIS-DSP**, TI). Framework versions, plugin-format SDK revisions, and host-support matrices carry retrieval dates — re-verify before pinning in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install audio-dsp-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
