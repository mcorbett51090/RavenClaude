# Real-time audio review checklist — <effect / plugin>

> The sign-off before DSP code ships. Reached from the
> [`dsp-design-spec.md`](dsp-design-spec.md). The order matters:
> **callback-safety → numerics → parameters → correctness → performance.**
> A DSP change is **not done** until the measurement rows below are green with numbers.

**Reviewed:** <YYYY-MM-DD> · **Effect/stage:** <name> · **Reviewer:** <name> · **Verdict:** pass / fail

## 1. Callback real-time-safety (the hard invariant)
- [ ] **No heap allocation** in the callback (`processBlock` / `process`) — everything sized at `prepareToPlay`
- [ ] **No locks / mutexes** on the audio thread (no path can block on a lower-priority thread)
- [ ] **No syscalls / file / network / logging** on the audio thread
- [ ] **No unbounded loops / recursion / exceptions** — bounded, block-sized work only
- [ ] **State pre-allocated:** <delay lines · FFT scratch · smoothing state — where sized>
- **How verified:** <RT-safety assertion · tool · code review>

## 2. Numerics & denormals
- [ ] **Flush-to-zero / denormals-are-zero** set on the audio thread (or DC/dither in feedback paths)
- [ ] Numeric type matches the design (**float32 / float64 / fixed Qm.n**); no overflow/quantization surprise
- [ ] Coefficients **re-derived on sample-rate change** (no hard-coded 44.1/48k)

## 3. Parameter passing & smoothing
- [ ] UI/message thread → audio thread is **lock-free** (`std::atomic` / SPSC FIFO) — no mutex on the audio thread
- [ ] **Every audio-path parameter is smoothed per-sample** (one-pole ramp) — no zipper/click on a slider move
- [ ] No raw UI value read directly inside the loop

## 4. Correctness (objective — numbers, not ears)
| Measurement | Target | Result | Pass? |
|---|---|---|---|
| **Null test** (vs reference / pre-refactor) | residual at noise floor | <e.g. −140 dBFS> | ☐ |
| **THD+N** (nonlinear stages) | <spec> | <value> | ☐ |
| **Impulse response** (filters) | matches design | <plot/notes> | ☐ |
| **Frequency response** (magnitude/phase) | matches target curve | <plot/notes> | ☐ |
| **Latency** | matches spec + reported (PDC) | <value> | ☐ |

## 5. Performance
- [ ] **Profiled** — hot loop identified as a fraction of the buffer deadline (<CPU %>)
- [ ] Processed in **blocks** for cache locality
- [ ] **SIMD** where profiling justified it (<SSE/AVX/NEON/CMSIS-DSP>) — alignment + scalar remainder handled
- [ ] **Null test still passes** after every optimization (bit-safe, or the diff is explained)
- [ ] Denormals checked as a CPU win **before** micro-optimizing

## 6. Anti-aliasing
- [ ] Every nonlinearity is **oversampled** (<factor>) with band-limiting up/down filters
- [ ] No audible aliasing on a sweep test

## Seams (not this team)
- **Codec / delivery:** streaming-media-engineering · **Voice AI:** conversational-ai-voice-engineering · **MCU firmware:** embedded-iot-engineering · **Game middleware:** game-development

## Open issues / follow-ups
- <list>

**Signed off:** <reviewer> · <date>
