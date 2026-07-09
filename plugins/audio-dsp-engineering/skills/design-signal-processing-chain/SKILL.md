---
name: design-signal-processing-chain
description: From an effect or product goal and its architecture, derive the signal-processing chain — the block diagram (stage order), the per-stage algorithm (IIR biquad / FIR / FFT-STFT / delay / dynamics), the per-stage and total latency, the sample rate and gain-staging/headroom, the oversampling plan for any nonlinearity, and the parameter list with smoothing needs — captured in the DSP design spec. Reach for this when the user asks "design the effect chain for this", "what order should these processors go in?", or "map out the DSP stages and their latency". Used by `dsp-implementation-engineer` and `audio-dsp-architect`.
---

# Skill: design-signal-processing-chain

> **Invoked by:** `dsp-implementation-engineer` (primary, to spec before coding) and `audio-dsp-architect` (to shape the chain before the architecture is fixed).
>
> **When to invoke:** "Design the signal chain for <effect/product>"; "what order should these stages run in?"; "map the DSP stages, their latency, and gain-staging"; any move from a goal to a concrete, ordered processing chain.
>
> **Output:** the block diagram (stage order), per-stage algorithm + latency, sample rate + gain-staging/headroom, the oversampling plan for nonlinearities, and the parameter list with smoothing — captured in the design spec.

## Procedure

1. **Name the goal, the signal, and the latency budget.** What is the effect/product? Mono/stereo/multichannel? What round-trip latency can it spend (from the architecture)? The budget constrains every stage's latency.
2. **Draft the block diagram — stage order matters.** Sequence the processors and justify the order: e.g. **filter → nonlinearity → tone/EQ → dynamics → space (delay/reverb)** is common, but gating usually precedes distortion, and a limiter goes last. State where the signal splits/sums (parallel paths, wet/dry, mid-side).
3. **Assign a per-stage algorithm.** For each stage pick the primitive from [`../../knowledge/audio-dsp-patterns-2026.md`](../../knowledge/audio-dsp-patterns-2026.md): IIR biquad (resonant EQ/filter), FIR / partitioned convolution (linear-phase / IR), FFT-STFT overlap-add (spectral), ring-buffer delay, or a detector+gain-computer (dynamics).
4. **Sum the latency.** Add each stage's algorithmic latency (FIR taps/2, FFT frame, oversampling filters, look-ahead) plus the buffer latency; check it against the budget; flag the total to **report to the host (PDC)**. If it blows the budget, kick back to `choose-audio-dsp-architecture`.
5. **Plan oversampling for every nonlinearity.** Any waveshaper/clip/saturation stage gets an oversampling factor (2–8x) with band-limiting up/down filters — mark it on the diagram; it also adds latency (step 4).
6. **Set sample rate, gain-staging, and headroom.** Internal SR (re-derive coefficients on SR change), where gain is applied, and the headroom/dither plan so no stage clips internally.
7. **List the parameters and their smoothing.** Every user-facing control: its range, mapping (linear/log/dB), default, and whether it needs **per-sample smoothing** (any parameter in the audio path that would zipper). Capture the whole design in [`../../templates/dsp-design-spec.md`](../../templates/dsp-design-spec.md) so the chain, latency, oversampling, and parameters live in one reviewable page.

## Worked example

> User: "Design the chain for a stereo vocal channel-strip: gate, EQ, compressor, de-esser, limiter."

- **Order:** gate → EQ → compressor → de-esser → limiter. Gate first (don't compress up the noise floor); limiter last (catch the final peaks). De-esser after the compressor (compression can raise sibilance).
- **Per-stage algorithm:** gate = RMS detector + gain-computer; EQ = cascade of **IIR biquads** (low-cut + bell + high-shelf); compressor = peak/RMS detector + gain-computer with attack/release smoothing; de-esser = a band-split (biquad) feeding a fast compressor on the sibilant band; limiter = **look-ahead** peak limiter.
- **Latency:** gate/EQ/comp = ~0 (minimum-phase, no lookahead); de-esser ~0; **limiter look-ahead = e.g. 1.5 ms** → total algorithmic latency ~1.5 ms, **reported to the host via PDC**.
- **Nonlinearity:** the limiter's clip stage → **oversample 4x** to tame aliasing on hard peaks.
- **SR/gain/headroom:** 32-bit float internal, unity gain-staging with a dB trim per stage, headroom kept below 0 dBFS until the limiter.
- **Parameters:** threshold/ratio/attack/release (comp), frequencies/gains/Q (EQ), gate threshold — all **per-sample smoothed** so automation doesn't zipper; frequencies mapped log, gains in dB.

## Guardrails

- Stage order is a design decision with audible consequences — justify it, don't default it.
- Every stage's latency is summed and the **total is reported to the host (PDC)** — silent latency is a phase/timing bug downstream.
- Any nonlinear stage carries an **oversampling** plan on the diagram — never leave a waveshaper un-band-limited.
- Every audio-path parameter that would zipper gets **per-sample smoothing** noted in the spec (the engineer implements it; the spec must call it out).
- Re-derive filter coefficients on sample-rate change — never hard-code 44.1/48k.
- If the summed latency or CPU blows the budget, kick back to [`choose-audio-dsp-architecture`](../choose-audio-dsp-architecture/SKILL.md) rather than silently over-spending.
- See the patterns reference for the algorithm primitives and the callback contract the implementation must honor: [`../../knowledge/audio-dsp-patterns-2026.md`](../../knowledge/audio-dsp-patterns-2026.md).
