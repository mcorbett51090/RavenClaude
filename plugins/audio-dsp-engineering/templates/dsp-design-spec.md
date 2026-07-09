# DSP design spec — <effect / product name>

> The one-page spec captured **before** writing DSP code. Pairs with
> [`realtime-audio-review-checklist.md`](realtime-audio-review-checklist.md) (the sign-off before the code ships).

**Owner:** <name> · **Date:** <YYYY-MM-DD> · **Platform/format:** <JUCE VST3/AU/CLAP · Web Audio · AUv3 · embedded> · **Status:** draft / approved / built

## Goal & signal
- **What this effect/product is:** <one line>
- **Signal:** <mono / stereo / multichannel / ambisonic> · **Sample rate (internal):** <e.g. host SR, 32-bit float> · **Bit depth / numeric:** <float32 / float64 / fixed Qm.n>
- **Use case:** <live-monitoring / mixing / mastering / game / embedded / web>

## Latency budget
- **Round-trip target:** <e.g. ≤ 5 ms for live monitoring>
- **Buffer size assumption:** <e.g. 64–256 samples>
- **Algorithmic latency (summed):** <FIR taps/2 · FFT frame · oversampling filters · look-ahead → total>
- **Reported to host (PDC)?** <yes — value · n/a>

## Signal chain (block diagram — order matters)
```
<in> → [stage 1] → [stage 2] → ... → [stage N] → <out>
        (note parallel/wet-dry/mid-side splits and sums)
```

| # | Stage | Algorithm | Domain | Per-stage latency | Notes |
|---|---|---|---|---|---|
| 1 | <e.g. high-pass> | IIR biquad (DF-II-T) | time | 0 | <coeffs recomputed on SR change> |
| 2 | <e.g. waveshaper> | nonlinearity | time | <OS filter> | **oversampled** — see below |
| 3 | <e.g. cabinet> | FIR / partitioned convolution | time | taps/2 | <IR length> |
| 4 | <e.g. spectral gate> | FFT-STFT overlap-add | freq | 1 frame | <FFT size · hop · Hann/COLA> |
| 5 | <e.g. limiter> | detector + gain-computer | time | look-ahead | <last in chain> |

## Oversampling (every nonlinearity)
- **Which stages:** <the nonlinear stages that alias>
- **Factor:** <2 / 4 / 8x> · **Up/down filters:** <polyphase FIR / half-band> · **Added latency:** <value>

## Gain-staging & headroom
- **Where gain is applied:** <per-stage trim · input/output>
- **Headroom / dither plan:** <keep below 0 dBFS until limiter · dither on bit-depth reduction>

## Parameters
| Parameter | Range | Mapping | Default | Per-sample smoothing? |
|---|---|---|---|---|
| <e.g. cutoff> | 20 Hz–20 kHz | log | 1 kHz | yes |
| <e.g. drive> | 0–24 dB | dB | 0 | yes |
| <e.g. mix> | 0–100% | linear | 50% | yes |

## State to pre-allocate (at prepareToPlay)
- <delay lines · filter memory · FFT scratch · oversampling buffers · smoothing state — all sized here, none in processBlock>

## Seams (not this team)
- **Codec / container / streaming delivery:** streaming-media-engineering
- **Conversational voice AI (ASR/TTS/turn-taking):** conversational-ai-voice-engineering
- **General MCU firmware / RTOS / peripherals:** embedded-iot-engineering
- **Game-engine audio middleware:** game-development

## Open questions / risks
- <list>

**Sign-off:** <reviewer> · <date>
