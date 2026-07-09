# Knowledge — Audio-DSP architecture decision tree

> **Last reviewed:** 2026-07-09 · **Confidence:** Medium-High (consensus on the latency→processing-model, time-vs-frequency-domain, fixed-vs-float, and oversampling framings, and on where JUCE / Web Audio / CLAP / the plugin formats each fit; **specific framework versions, plugin-format spec revisions, and host-support claims are volatile — re-verify before a client commitment**).
> The most-asked audio-DSP question is "what architecture — block or per-sample, what latency, what platform/format, fixed or float, and which algorithm family?". This is the decision tree the `audio-dsp-architect` traverses **before** naming a framework or algorithm, plus the trade-off tables, the domain sub-choice, and the seams to adjacent plugins.

The agent's discipline: **name the constraint first (latency tolerance, target FPU, the effect's domain), name the framework/algorithm second.** Codec/delivery questions — how the audio is *encoded and shipped* — are **not** real-time DSP; they leave this layer for `streaming-media-engineering`.

---

## Decision Tree: choosing an audio-DSP architecture

Traverse top-to-bottom. Gate on **latency tolerance** first (it sets the processing model and how much lookahead you can spend), then **the effect's domain**, then **the numeric strategy**, then **the platform/format**.

```mermaid
graph TD
  Start([What are you building?]) --> LAT{Latency tolerance?}

  LAT -->|Ultra-low<br/>live monitoring / amp-sim / instrument| PM_SAMPLE{Feedback loop in the algorithm?}
  LAT -->|Moderate<br/>mixing / real-time FX| PM_BLOCK[Block/buffer processing<br/>· small buffers 64-256<br/>· no or minimal lookahead]
  LAT -->|Relaxed<br/>mastering / offline / linear-phase| PM_LOOK[Block processing + lookahead<br/>· linear-phase FIR / large FFT OK<br/>· report latency to host PDC]

  PM_SAMPLE -->|Yes, tight feedback<br/>SVF, physical model| SBS[Sample-by-sample<br/>· per-sample state update<br/>· accept lower SIMD efficiency]
  PM_SAMPLE -->|No| PM_BLOCK

  PM_BLOCK --> DOMAIN
  PM_LOOK --> DOMAIN
  SBS --> DOMAIN

  DOMAIN{Time-domain or frequency-domain effect?} -->|Resonant EQ / filter / dynamics / delay| TIME{Phase / ring-length need?}
  DOMAIN -->|Spectral: linear-phase EQ, spectral gate,<br/>convolution reverb, pitch/time-stretch| FREQ[FFT / STFT + overlap-add<br/>· pick FFT size & hop for<br/>freq/time resolution vs latency<br/>· windowed (Hann/COLA)]

  TIME -->|Minimum-phase, cheap| IIR[IIR biquads<br/>· Direct Form II transposed<br/>· cascade for higher order]
  TIME -->|Linear-phase / exact impulse| FIR[FIR / convolution<br/>· partitioned convolution for long IRs<br/>· latency = taps/2]

  IIR --> NONLIN
  FIR --> NONLIN
  FREQ --> NONLIN

  NONLIN{Any nonlinearity?<br/>distortion / waveshaping / clip} -->|Yes| OS[Oversample 2-8x<br/>· band-limit before downsampling<br/>· polyphase up/down filters]
  NONLIN -->|No| NUM

  OS --> NUM
  NUM{Target has an FPU?} -->|Yes, desktop / mobile| FLOAT[32-bit float internal<br/>· flush-to-zero for denormals<br/>· 64-bit for feedback-heavy IIR]
  NUM -->|No / power-constrained DSP| FIXED[Fixed-point Q-format<br/>· choose Qm.n for headroom<br/>· watch overflow + quantization<br/>· CMSIS-DSP on Cortex-M]

  FLOAT --> PLAT
  FIXED --> PLAT
  PLAT{Delivery platform?} -->|Desktop DAW plugin| DESK[JUCE / iPlug2<br/>· VST3 / AU / AAX / CLAP<br/>· ASIO / CoreAudio / WASAPI]
  PLAT -->|Browser| WEB[Web Audio AudioWorklet<br/>· render quantum 128<br/>· WASM SIMD for hot loops]
  PLAT -->|iOS / macOS app| APPLE[AUv3 / AVAudioEngine<br/>· CoreAudio backend]
  PLAT -->|Linux pro-audio| LINUX[LV2 / CLAP<br/>· JACK / ALSA / PipeWire]
  PLAT -->|Embedded pedal / hardware| EMB[Bare-metal / RTOS DSP<br/>· CMSIS-DSP / TI DSPLIB<br/>· I2S codec I/O]
```

---

## Trade-off table — processing model

| Model | Sweet spot | Watch out for |
|---|---|---|
| **Block/buffer** | Most effects; cache- and SIMD-friendly; the plugin default | Introduces block-boundary latency; parameter changes must be smoothed across the block |
| **Sample-by-sample** | Tight feedback loops (state-variable filters, physical models, some compressors' detectors) | Poor SIMD utilization; more per-sample overhead; only where feedback truly needs it |
| **Block + lookahead** | Linear-phase EQ, look-ahead limiters, mastering | Adds latency that MUST be reported to the host (PDC); not for live monitoring |

## Trade-off table — algorithm family

| Family | Sweet spot | Watch out for |
|---|---|---|
| **IIR biquad** | Cheap resonant EQ/filters, minimum-phase; low latency, few coefficients | Phase distortion; can go unstable with bad coefficients; denormals in the feedback tail |
| **FIR / convolution** | Linear-phase, exact impulse responses (cab sims, convolution reverb) | Latency = taps/2; long IRs need partitioned convolution to stay real-time |
| **FFT / STFT overlap-add** | Spectral operations (spectral gate, phase vocoder pitch/time, linear-phase EQ) | Latency = FFT frame; needs correct window + hop (COLA) or you get modulation artifacts |
| **Oversampling wrapper** | Any nonlinearity — tames aliasing | 2-8x the CPU on the wrapped stage; needs good up/down band-limiting filters |

## Trade-off table — plugin format & audio I/O (2026-07 snapshot — volatile)

| Format / backend | Sweet spot | Watch out for |
|---|---|---|
| **VST3** | Broadest desktop DAW support (Win/mac/Linux) | Steinberg SDK licensing; more complex than VST2/CLAP |
| **AU / AUv3** | macOS/iOS hosts (Logic, GarageBand); AUv3 for app-extension sandboxing | Apple-only; AUv3 sandbox constraints |
| **AAX** | Pro Tools | Avid-only SDK + signing; niche outside Pro Tools |
| **CLAP** | Modern open format, good threading/param model, growing host support | Younger; not every host yet — check target hosts _(retrieved 2026-07-09)_ |
| **LV2** | Linux/open-source pro-audio | Sparser commercial-host support |
| **Web Audio AudioWorklet** | Browser DSP; 128-sample render quantum on the audio render thread | No arbitrary threads; keep the process() callback allocation-free; WASM+SIMD for speed |
| **CoreAudio / ASIO / WASAPI / ALSA·JACK·PipeWire** | mac / Win-pro / Win / Linux low-latency I/O respectively | Buffer-size & exclusive-mode differ per backend; ASIO needed for low-latency on Windows |

> **Volatile:** framework versions (JUCE, iPlug2), plugin-format SDK revisions (VST3, CLAP, AUv3), and host-support matrices change frequently. Treat the rows above as a 2026-07 snapshot and re-verify with `ravenclaude-core/deep-researcher` before a client commitment.

---

## Domain sub-choice (time vs frequency) — after the processing model

- **Time-domain** — the effect is a filter, dynamics processor, or delay whose output depends on recent samples. IIR biquads (minimum-phase, cheap, low latency) or FIR (linear-phase, exact). The natural home for EQ, compression, gating, chorus/flanger, and delay.
- **Frequency-domain** — the effect operates on the spectrum: linear-phase EQ, spectral gating/de-noise, convolution reverb, and phase-vocoder pitch/time-stretch. FFT/STFT with a window (Hann) and a hop that satisfies COLA for artifact-free reconstruction. The FFT size trades frequency resolution against time resolution *and* latency.

Cross-cut both with **oversampling**: any nonlinear stage (distortion, waveshaping, hard clip) must be oversampled 2-8x with band-limiting up/down filters, or it aliases.

---

## Seams (real-time DSP is the processing layer, not the whole audio pipeline)

- **Codec / container / streaming delivery** → `streaming-media-engineering` (how audio is *encoded and shipped* — AAC/Opus, HLS/DASH — distinct from "how the sample is *processed* in real time").
- **Conversational voice AI** (ASR, TTS, turn-taking, barge-in) → `conversational-ai-voice-engineering`.
- **General MCU firmware / RTOS / peripherals** around a DSP core → `embedded-iot-engineering` (this plugin owns the *signal processing*, not the board bring-up).
- **Game-engine audio middleware / spatial mixer integration** → `game-development`.
- **Non-audio-thread profiling / whole-app CPU budgets** → `performance-engineering`.

---

## Provenance

- Durable framings (latency→processing-model, block vs per-sample, time vs frequency domain, IIR/FIR/FFT trade-offs, oversampling for nonlinearity, fixed vs float + denormals, overlap-add/COLA) are consensus practice across the DSP and real-time-audio literature, reviewed 2026-07-09 — **High confidence**.
- Plugin-format and framework positioning (VST3, AU/AUv3, AAX, CLAP, LV2, JUCE, Web Audio AudioWorklet, and the CoreAudio/ASIO/WASAPI/ALSA/JACK backends) as of 2026-07; **SDK revisions, framework versions, and host-support matrices are volatile, re-verify before quoting.** _(Retrieved 2026-07-09.)_
