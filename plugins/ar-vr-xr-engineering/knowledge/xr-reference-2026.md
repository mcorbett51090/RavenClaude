# AR/VR/XR Engineering — 2026 Reference

> Dated reference for the `ar-vr-xr-engineering` team: the device/runtime/engine landscape and the perf targets agents reach for. The durable reasoning lives in [`xr-decision-trees.md`](xr-decision-trees.md); this file is the freshness-anchored "what the landscape and numbers are."
>
> **Engineering judgment, not certification advice.** The XR hardware/runtime/engine landscape moves fast. Every headset spec, runtime/OpenXR support claim, engine version, and per-eye perf number below is **volatile** and carries a **source placeholder + retrieval date + `[verify-at-use]`** — re-confirm against the vendor/runtime/engine docs before it drives a build commitment. Estimates are marked `[ESTIMATE]`. No PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Treat every specific as `[verify-at-use]` unless re-confirmed this session._

---

## 1. Headset / device-class landscape

| Class | Examples (names change) | Compute | Notes | Source / retrieved | Flag |
|---|---|---|---|---|---|
| Standalone headset | Quest-family and other all-in-one HMDs | Mobile SoC | Untethered, mass reach, tight frame budget | _<vendor spec sheet>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Spatial computer / MR headset | visionOS-class devices | On-device SoC | Passthrough-first MR, own SDK + OpenXR varies by device | _<vendor docs>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| PC-VR | Headsets driven by a desktop GPU (SteamVR/OpenXR) | Desktop GPU | Highest fidelity; tethered or streamed | _<vendor/runtime docs>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| WebXR | Any WebXR-capable headset/browser | Varies | Zero-install; support gated by browser + device | _<caniuse / WebXR support>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Mobile-AR | ARKit / ARCore phones & tablets | Phone SoC | Widest install base; handheld world/plane tracking | _<platform AR docs>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> Device names, generations, and their exact specs change frequently. Confirm the current model and its capabilities before committing an architecture to it.

---

## 2. Runtime / API landscape

| Layer | What it is | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| OpenXR | Khronos vendor-neutral XR runtime API | The portability layer — target it first; extension support varies per runtime | _<khronos.org/openxr>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| SteamVR / vendor runtimes | Platform runtimes exposing OpenXR + native APIs | Per-device features (passthrough, hand-tracking) often via extensions | _<runtime docs>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| WebXR Device API | Browser XR API (immersive-vr / immersive-ar) | Support and feature flags vary by browser + device | _<w3c WebXR / caniuse>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| ARKit / ARCore | Apple / Google mobile-AR frameworks | Plane/world/anchor tracking, occlusion, depth | _<platform AR docs>_ — retrieved 2026-07-02 | `[verify-at-use]` |

---

## 3. Engine landscape

| Engine | Fit | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| Unity | Broad device reach, C# | XR Interaction Toolkit, OpenXR plugin; wide standalone/PC/mobile support | _<unity XR docs>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Unreal | High fidelity, C++/Blueprint | Higher baseline budget; strong rendering | _<unreal XR docs>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Native + OpenXR | Max control, no engine tax | Most effort; graphics-strong teams | _<openxr sdk docs>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| WebXR frameworks | Browser reach | three.js / Babylon.js / A-Frame; tightest budget | _<framework docs>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> Engine XR-feature parity for a given target changes release to release. Verify the feature you depend on (hand-tracking, passthrough, foveated rendering) is supported on the target before committing.

---

## 4. Per-eye performance budget targets `[ESTIMATE]`

| Refresh rate | Per-eye frame budget (concept) | Note | Flag |
|---|---|---|---|
| 72 Hz | ~13.9 ms/frame | Common standalone floor | `[ESTIMATE]` `[verify-at-use]` |
| 90 Hz | ~11.1 ms/frame | Common comfortable target | `[ESTIMATE]` `[verify-at-use]` |
| 120 Hz | ~8.3 ms/frame | High-refresh target | `[ESTIMATE]` `[verify-at-use]` |

> Frame time = 1000 / refresh_hz (the math is durable). The **achievable** scene complexity, draw-call ceiling, and thermal-sustained clock for a given device are `[verify-at-use]` against the device profiler. Budget for sustained (throttled) performance, not a peak demo. Reprojection (ASW/spacewarp-style) is a safety net, not budget.

---

## 5. Comfort / safety concepts (durable, mitigations verify-at-use)

| Concept | What it is | Flag |
|---|---|---|
| Vection | Visually-induced self-motion — the main sim-sickness driver | durable |
| Comfort mitigations | Vignette/tunneling, snap turning, static reference frame, seated mode | `[verify-at-use]` current guidance |
| Guardian / boundary / play-space | Physical-safety boundary + passthrough cues | `[verify-at-use]` per runtime |
| Foveated rendering | Fixed or eye-tracked; renders periphery cheaper | `[verify-at-use]` per device |

---

## 6. How to use this file

1. Find the device/runtime/engine/target you need.
2. Read its retrieval date — if stale or unconfirmed this session, **re-verify** against the cited source type before quoting.
3. Quote it with its flag (`[ESTIMATE]` / `[verify-at-use]`) intact when it informs an architecture or budget commitment.
4. For anything that gates a build decision: confirm against the vendor/runtime/engine docs first.

---

## See also

- [`xr-decision-trees.md`](xr-decision-trees.md) — the durable target/engine/locomotion/perf-triage trees.
- Deep profiling methodology: [`../../performance-engineering/CLAUDE.md`](../../performance-engineering/CLAUDE.md).
