---
name: choose-audio-dsp-architecture
description: Pick the right audio-DSP architecture for a described product by traversing the audio-DSP architecture decision tree (latency tolerance → processing model → time-vs-frequency domain → fixed-vs-float + denormals → platform/plugin format + audio I/O), then return the recommended processing model, latency & buffer-size budget, sample rate/bit depth, numeric strategy, algorithm approach (IIR/FIR/FFT-STFT, oversampling), framework + plugin format + audio backend, and the conditions that would flip the choice. Reach for this when the user asks "block or sample-by-sample?", "what latency/buffer size?", "JUCE + VST3/AU/CLAP or Web Audio?", "fixed-point or float?", or "IIR biquad vs FIR vs FFT for this effect?". Used by `audio-dsp-architect` (primary).
---

# Skill: choose-audio-dsp-architecture

> **Invoked by:** `audio-dsp-architect` (primary). Also consulted by `dsp-implementation-engineer` when a build reveals the chosen architecture can't meet the latency/CPU budget.
>
> **When to invoke:** "block or sample-by-sample?"; "what latency / buffer size can we afford?"; "JUCE + VST3/AU/CLAP or Web Audio AudioWorklet?"; "fixed-point or floating-point?"; "IIR biquad vs FIR vs FFT/STFT for this effect?"; any "what audio-DSP architecture should we use?" question.
>
> **Output:** the processing model + latency/buffer budget + sample rate/bit depth + numeric strategy (fixed vs float + denormals) + algorithm approach + framework/plugin-format/audio-I/O + the 1-2 flip conditions.

## Procedure

1. **Restate the situation in the tree's terms.** Capture: the **use case** (live monitoring / mixing / mastering / game engine / embedded pedal / browser), the **latency tolerance** (single-digit ms for monitoring, tens of ms OK for mastering), the **platform** (desktop DAW, iOS/AUv3, web, an ARM DSP), the **signal** (mono/stereo/multichannel/ambisonic + sample rate), and the **CPU/power budget**.
2. **Set the latency budget first — it drives the processing model.** Ultra-low latency → small buffers, no lookahead, and sample-by-sample only where a tight feedback loop demands it; relaxed latency → block + lookahead (linear-phase FIR, large FFT) is allowed. Everything downstream is spent from this budget.
3. **Choose the domain from the effect.** Resonant EQ / filter / dynamics / delay → **time-domain** (IIR biquad or FIR); a spectral operation (linear-phase EQ, spectral gate, convolution reverb, pitch/time-stretch) → **frequency-domain** (FFT/STFT + overlap-add). For frequency-domain, pick the FFT size & hop for the resolution/latency you can afford.
4. **Traverse the decision tree** in [`../../knowledge/audio-dsp-decision-tree.md`](../../knowledge/audio-dsp-decision-tree.md) against those inputs:
   - ultra-low latency + tight feedback → **sample-by-sample**; otherwise → **block/buffer**; relaxed → **block + lookahead**,
   - minimum-phase cheap filter → **IIR biquad**; linear-phase / exact IR → **FIR / partitioned convolution**; spectral → **FFT/STFT overlap-add**,
   - any nonlinearity → wrap it in **oversampling** (2–8x) with band-limiting up/down filters,
   - target has an FPU → **32-bit float** (+ flush-to-zero); FPU-less/power-constrained → **fixed-point Q-format** (+ CMSIS-DSP),
   - desktop plugin → **JUCE/iPlug2** (VST3/AU/AAX/CLAP); browser → **Web Audio AudioWorklet**; iOS → **AUv3**; Linux pro-audio → **LV2/CLAP + JACK**; embedded → **bare-metal/RTOS + I2S**.
5. **Fix the numeric strategy and the denormal policy.** Float vs fixed per the FPU; name flush-to-zero/DAZ (or DC/dither injection) so denormals don't spike the CPU.
6. **Match the audio I/O backend** to the OS and latency target: CoreAudio (mac), ASIO (Windows low-latency), WASAPI (Windows), ALSA/JACK/PipeWire (Linux).
7. **State the flip conditions** — the 1-2 facts that, if different, change the answer (e.g., "if the target gains an FPU, float replaces fixed-point"; "if latency tolerance drops, the linear-phase FIR must become a minimum-phase IIR").

## Worked example

> User: "A guitar amp-sim plugin for live use on desktop DAWs. Distortion is the core of it. IIR or FIR, and what latency? JUCE?"

- The use case is **live monitoring** → **ultra-low latency**: small buffers (64–128), **no lookahead**, block processing (no tight feedback loop that forces per-sample).
- The tone stack is a set of resonant filters → **time-domain IIR biquads** (cheap, low latency, minimum-phase); the cabinet is an impulse response → a **short FIR / partitioned convolution** (accept its small latency, report it via PDC).
- Distortion is a **nonlinearity** → **oversample 4x** around the waveshaper with band-limiting up/down filters, or it aliases audibly.
- Desktop + FPU → **32-bit float** internal, **flush-to-zero** set on the audio thread. Platform → **JUCE**, formats **VST3 + AU (+ CLAP)**, backend **ASIO on Windows / CoreAudio on mac** for low latency.
- **Flip condition:** if they later want a *linear-phase* cabinet or a mastering-grade version, the latency budget relaxes and a longer FIR / larger oversampling becomes acceptable.

## Guardrails

- Never name a framework or algorithm before traversing the tree — constraint (latency/FPU/domain) before brand.
- Set the latency budget first; you can't retrofit low latency onto a lookahead-heavy chain.
- Any nonlinearity gets an **oversampling** plan at design time — an un-oversampled distortion is a defect, not a mix problem.
- Fixed vs float is decided by the FPU, not by habit; name the denormal policy either way.
- Report algorithmic latency to the host (PDC) — un-reported latency is a phase/timing bug downstream.
- Codec/delivery/streaming questions are **not** real-time DSP — route to `streaming-media-engineering`.
- Volatile claims (framework versions, plugin-format SDK revisions, host support) carry a **retrieval date** and are re-verified before a client commitment. See [`../../knowledge/audio-dsp-patterns-2026.md`](../../knowledge/audio-dsp-patterns-2026.md).
