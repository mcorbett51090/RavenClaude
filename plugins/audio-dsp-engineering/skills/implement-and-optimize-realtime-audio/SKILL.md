---
name: implement-and-optimize-realtime-audio
description: Implement a DSP stage as real-time-safe code in the audio callback (no locks, no allocation, no syscalls, no unbounded work — everything pre-allocated at prepare time), handle denormals with flush-to-zero, pass parameters lock-free (atomic / SPSC FIFO) with per-sample smoothing, then optimize the profiled hot loop with SIMD (SSE/AVX/NEON/CMSIS-DSP) and verify with objective measurement (null test, THD+N, impulse/frequency response, RT-safety audit). Reach for this when the user asks "write the real-time-safe processBlock", "optimize this hot loop", "pass params without a data race", or "null-test / measure this effect". Used by `dsp-implementation-engineer` (primary).
---

# Skill: implement-and-optimize-realtime-audio

> **Invoked by:** `dsp-implementation-engineer` (primary). Also consulted by `audio-dsp-architect` to sanity-check that a chosen architecture is real-time-safe and implementable.
>
> **When to invoke:** "Write the real-time-safe `processBlock` for <effect>"; "optimize this DSP hot loop (SIMD/denormals)"; "pass parameters from the UI thread without a data race or a click"; "null-test / measure THD+N / plot the frequency response"; any move from a spec to running, measured DSP code.
>
> **Output:** real-time-safe DSP code (or an optimization/measurement) with the callback invariants held, denormals handled, lock-free parameters + smoothing, SIMD where profiling justifies it, and objective pass/fail measurements.

## Procedure

1. **Hold the callback real-time-safety invariant first.** Before any effect logic, confirm the plan has **no lock, no heap allocation, no syscall/file/log I/O, no unbounded work** inside the audio callback (`processBlock` / `AudioWorkletProcessor.process`). Everything is **pre-allocated at `prepareToPlay(sampleRate, blockSize)`** — delay lines, FFT scratch, smoothing state, ring buffers. See the contract in [`../../knowledge/audio-dsp-patterns-2026.md`](../../knowledge/audio-dsp-patterns-2026.md).
2. **Implement the DSP from the right primitive.** Biquad (Direct Form II transposed) for IIR; FIR / partitioned convolution for linear-phase/IR; FFT + windowed (Hann/COLA) overlap-add for spectral; ring-buffer delay lines for time effects. Size all state at prepare time; wrap ring buffers without allocating.
3. **Kill denormals.** Set **flush-to-zero / denormals-are-zero** on the audio thread (once per callback entry), or inject a tiny DC/dither into feedback paths, so decaying tails don't 10–100x the CPU.
4. **Pass parameters lock-free with smoothing.** UI/message thread → audio thread via `std::atomic<float>` (scalars) or a **lock-free SPSC FIFO** (events) — never a mutex the audio thread can block on. **Smooth every audio-path parameter per-sample** (one-pole ramp) so a slider move doesn't zipper; never read a raw UI value in the loop.
5. **Profile before you optimize.** Measure the actual hot loop as a fraction of the buffer deadline. Process in blocks for cache locality. Only then **vectorize** the bottleneck with SIMD (SSE/AVX on x86, **NEON** on ARM, **CMSIS-DSP** on Cortex-M) — mind alignment and the scalar remainder. Often the biggest real win is just fixing denormals (step 3).
6. **Verify bit-safety and correctness with numbers.** After any optimization, a **null test** against the scalar reference must still pass (residual at the noise floor) or the diff must be explained. Then measure the stage objectively: **THD+N** (nonlinear stages), **impulse & frequency response** (filters), and a **RT-safety audit** (no allocation/lock on the audio thread — an RT-safety assertion or tool). Report pass/fail with numbers, not "sounds fine".
7. **Capture the measurement result** against the [`../../templates/realtime-audio-review-checklist.md`](../../templates/realtime-audio-review-checklist.md) so the callback-safety, denormal, parameter-passing, and measurement checks are all signed off.

## Worked example

> User: "Our plate-reverb spikes CPU and a slider move clicks. Fix it and prove the sound is unchanged."

- **RT-safety audit:** confirm `processBlock` allocates nothing — the reverb's delay lines and all-pass buffers are sized in `prepareToPlay`. (Found a `std::vector` resize on a size change in the callback → moved it to a lock-free "new size ready" hand-off from the UI thread.)
- **Denormals:** the reverb tail decays into the denormal range → set **flush-to-zero / DAZ** at callback entry (and add a `1e-20` DC to the feedback). CPU on quiet tails drops ~8x — that was the spike.
- **The click:** the "size"/"mix" sliders were read raw in the loop → add **per-sample one-pole smoothing** (~20 ms); the zipper is gone.
- **Optimize:** profile shows the all-pass loop is the hot spot → vectorize it with **NEON** (target is Apple Silicon), 4 samples/instruction.
- **Prove it:** **null test** the vectorized build against the scalar reference → residual at −140 dBFS (bit-safe). **Frequency/impulse response** unchanged; **RT-safety audit** clean. Pass.

## Guardrails

- The callback is hard-real-time: **no lock, no allocation, no syscall, no unbounded loop** — ever. Pre-allocate at `prepareToPlay`.
- **Flush-to-zero is always on** on the audio thread — denormals are a CPU trap, not a rounding curiosity.
- Cross-thread parameters are **lock-free** (atomic / SPSC FIFO) — a mutex the audio thread can block on is a priority inversion.
- **Smooth every audio-path parameter** per-sample or ship zipper noise.
- **Profile before you SIMD; null-test after** — vectorize the measured bottleneck and prove the output is unchanged (or explain the diff).
- A DSP change isn't done until **measured** — null test / THD+N / frequency response with numbers.
- Volatile framework/intrinsic claims carry a **retrieval date**; re-verify before shipping. See [`../../knowledge/audio-dsp-patterns-2026.md`](../../knowledge/audio-dsp-patterns-2026.md).
