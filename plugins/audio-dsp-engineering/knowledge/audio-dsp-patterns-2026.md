# Knowledge — Audio-DSP patterns (2026)

> **Last reviewed:** 2026-07-09 · **Confidence:** High on the durable concepts (the audio-callback real-time contract, block processing, denormals/flush-to-zero, biquad/FIR/FFT overlap-add, lock-free parameter passing, oversampling/anti-aliasing, the measurement suite); **Medium on the dated tooling/framework map — versions and intrinsics change and carry retrieval dates below.**
> The reference the `dsp-implementation-engineer` reads when building and optimizing DSP: the callback contract, block/buffer processing, numeric handling, the core algorithms, thread-safe parameters, optimization, and objective measurement — plus a 2026 tooling snapshot.

The team's discipline: **the audio callback is hard-real-time (no locks, no allocation, no syscalls, no unbounded work); pre-allocate everything at prepare time; kill denormals; smooth every parameter; pass cross-thread data lock-free; profile before you SIMD and null-test after; and prove correctness with numbers, not ears.**

---

## The audio-callback real-time contract — the one rule everything serves

The audio callback (`processBlock`, `AudioWorkletProcessor.process`, the render callback) runs on a **hard-real-time thread** with a deadline: it must fill the next buffer before the DAC needs it, or the user hears a **click/dropout** (an xrun). That deadline is unforgiving, so inside the callback there is:

| Forbidden in the callback | Why | Do instead |
|---|---|---|
| **Locks / mutexes** | The audio thread can block on a lower-priority thread → priority inversion → dropout | Lock-free atomics / SPSC FIFO |
| **Heap allocation** (`new`/`malloc`/`std::vector` resize) | Allocation can take a lock and is unbounded in time | Pre-allocate all buffers at `prepareToPlay` |
| **Syscalls / file / network / logging** | Unbounded latency; may block | Queue events to a non-RT thread |
| **Unbounded loops / recursion** | No time bound → missed deadline | Bounded, block-sized work only |
| **Exceptions / `std::cout` / GC** | Non-deterministic timing | Error-code paths; no allocation |

**Everything the callback needs is allocated before it runs.** `prepareToPlay(sampleRate, blockSize)` sizes every delay line, FFT scratch buffer, and smoothing state; `processBlock` only *computes*. This is the invariant every other pattern below exists to uphold.

---

## Block/buffer processing & latency

Audio is processed in **blocks** (buffers) of N samples (typically 64–1024; Web Audio's render quantum is 128). Bigger blocks amortize per-call overhead and vectorize better but add latency; smaller blocks lower latency but raise CPU per sample.

- **Round-trip latency** ≈ input buffer + processing + output buffer, plus any **algorithmic latency** (FIR taps/2, FFT frame, oversampling filters, look-ahead).
- **Report algorithmic latency to the host** (plugin delay compensation, PDC) so the DAW time-aligns tracks. Un-reported latency = phase/timing errors in a mix.
- **Sample rate & bit depth:** process internally in 32-bit float (or 64-bit for feedback-heavy IIR); the host's SR can change — re-derive coefficients on `prepareToPlay`, never hard-code 44.1/48k.

---

## Numeric handling: fixed vs float, and denormals

- **Floating-point (32-bit)** is the desktop/plugin default; **64-bit** for feedback-heavy IIR where error accumulates. **Fixed-point (Qm.n)** is for FPU-less/power-constrained DSPs — choose the Q-format for headroom, watch overflow and quantization noise.
- **Denormals are a real-time trap.** When a filter/reverb tail decays toward zero, values enter the denormal range and many CPUs handle them via microcode — a **10–100x** slowdown that spikes right when the signal goes quiet. Fixes:
  - Set **flush-to-zero (FTZ)** and **denormals-are-zero (DAZ)** on the audio thread (via the FPU control/`MXCSR` on x86, FPSCR on ARM) — the standard, cheapest fix.
  - Or inject a tiny **DC offset / dither** (e.g. `1e-20`) into feedback paths so values never reach the denormal range.
- Set FTZ/DAZ **once per callback entry** (thread-local); don't assume the host set it.

---

## Core algorithms

**IIR biquad** — the workhorse EQ/filter. A second-order section: `y = b0*x + b1*x1 + b2*x2 − a1*y1 − a2*y2`. Prefer **Direct Form II transposed** for float (better numerical behavior); cascade biquads for higher-order filters. Recompute coefficients on parameter change (smoothed) and on SR change.

**FIR / convolution** — linear-phase filters and exact impulse responses (cabinet sims, convolution reverb). Latency = (taps−1)/2. For long IRs, **partitioned convolution** (uniform or non-uniform partitions) keeps it real-time by doing the FFT convolution in blocks.

**FFT / STFT + overlap-add** — spectral effects. Frame the signal, window it (**Hann** is the default), FFT, process the spectrum, IFFT, and overlap-add with a **hop** that satisfies the **COLA** (constant-overlap-add) constraint (e.g. Hann at 50%/75% overlap) so the reconstruction has no amplitude modulation. FFT size trades frequency resolution vs time resolution *and* adds latency = one frame.

**Delay/reverb** — pre-sized **ring buffers**; interpolate fractional delays (linear/all-pass) for modulation. Reverb = networks of delays + all-pass/comb filters (Schroeder/FDN); feedback paths need denormal handling.

**Dynamics** — a level detector (peak/RMS, attack/release smoothing) drives a gain-computer; a **look-ahead** limiter delays the signal so the gain can react before the peak (adds reported latency).

---

## Oversampling & anti-aliasing

Any **nonlinearity** (distortion, waveshaping, saturation, hard clip, some compressors) creates harmonics above Nyquist that **fold back** as aliasing — an un-oversampled distortion is a design bug. Pattern:

1. **Upsample** 2–8x with a band-limiting (polyphase FIR / half-band) filter.
2. Apply the nonlinearity at the higher rate.
3. **Downsample** with a band-limiting filter that removes everything above the original Nyquist.

Higher oversampling = less aliasing but 2–8x the CPU on that stage and more latency from the filters. Choose the factor by how aggressive the nonlinearity is.

---

## Thread-safe parameter passing (lock-free)

UI/message thread → audio thread must **never** cross a mutex the audio thread could block on. Patterns:

- **Scalar parameters:** `std::atomic<float>` — the audio thread reads the latest value, no lock.
- **Events / structured changes:** a **lock-free SPSC FIFO / ring buffer** (single-producer/single-consumer) so the UI thread pushes and the audio thread pops without blocking.
- **Parameter smoothing:** never use the raw value in the loop — ramp it per-sample (a one-pole `current += (target − current) * coeff`) so a slider move doesn't produce **zipper noise**. Smoothing time ~5–50 ms typical.

The audio thread only ever reads **smoothed, race-free** values.

---

## Optimization: profile, block, vectorize

1. **Profile first** — find the actual hot loop; don't guess. Audio CPU is measured as a fraction of the buffer deadline.
2. **Process in blocks** for cache locality and to enable vectorization.
3. **SIMD** the bottleneck: SSE/AVX (x86), **NEON** (ARM), or **CMSIS-DSP** on Cortex-M. Process 4/8 samples per instruction; watch alignment and the scalar remainder.
4. **Verify bit-safety:** after any optimization, a **null test** against the scalar reference must still pass (residual at the noise floor) — or the numerical diff must be explained.

Denormals (above) are often the single biggest real-world CPU win — check FTZ before micro-optimizing.

---

## Measurement — prove it with numbers, not ears

| Measurement | What it proves | Pass criterion |
|---|---|---|
| **Null test** | The implementation matches a reference (or a refactor didn't change output) | Invert-and-sum residual is silence / at the noise floor |
| **THD+N** | Harmonic distortion + noise of a (non)linear stage | Within the target spec for the design |
| **Impulse response** | The filter's exact behavior (linearity, ringing, length) | Matches the designed response |
| **Frequency response** | Magnitude/phase vs frequency (EQ/filter correctness) | Matches the target curve; phase as designed |
| **RT-safety audit** | No allocation/lock/syscall on the audio thread | Zero flagged calls (RT-safety assertion / tooling) |

A DSP change is **not done until measured** — "sounds fine" is not a pass.

---

## Spatial / immersive audio (when in scope)

- **Binaural / HRTF** — convolve each source with a head-related transfer function pair for headphone 3D; interpolate HRTFs across positions to avoid clicks.
- **Ambisonics** — encode sources to a B-format (spherical-harmonic) scene, rotate/manipulate, then decode to the speaker/headphone layout; order trades spatial resolution vs channel count.
- These are convolution/matrix operations under the same callback contract — pre-allocate the HRTF/decoder matrices; keep the per-block work bounded.

---

## 2026 tooling map (dated — volatile, re-verify before quoting)

- **Frameworks:** **JUCE** (cross-platform C++, VST3/AU/AAX/CLAP/standalone), **iPlug2** (lighter-weight plugin framework), **Web Audio API / AudioWorklet** (browser, 128-sample quantum, WASM+SIMD for hot loops). _(Retrieved 2026-07-09.)_
- **Plugin formats:** VST3, AU/AUv3, AAX, **CLAP** (modern open format), LV2 — host-support matrices vary; check the target hosts. _(Retrieved 2026-07-09.)_
- **Audio I/O backends:** CoreAudio (mac/iOS), ASIO (Windows low-latency), WASAPI (Windows), ALSA/JACK/PipeWire (Linux). _(Retrieved 2026-07-09.)_
- **DSP libraries:** **ARM CMSIS-DSP** (Cortex-M fixed/float), **TI DSPLIB**, FFT libs (FFTW, PFFFT, KissFFT, Apple vDSP/Accelerate, Intel IPP). Intrinsics/APIs change across versions — treat as a 2026-07 snapshot. _(Retrieved 2026-07-09.)_

---

## Provenance

- Durable concepts (the audio-callback real-time contract, pre-allocation, block processing, denormals/FTZ/DAZ, biquad/FIR/FFT overlap-add/COLA, oversampling/anti-aliasing, lock-free SPSC parameter passing + smoothing, the null-test/THD+N/frequency-response measurement suite, HRTF/ambisonics basics) are consensus practice across the real-time-audio and DSP literature, reviewed 2026-07-09 — **High confidence**.
- The tooling map is a **2026-07 snapshot**; framework versions, plugin-format SDK revisions, host-support matrices, and DSP-library intrinsics are volatile and carry the retrieval dates above — re-verify with `ravenclaude-core/deep-researcher` before pinning in a deliverable.
