# XR Project Architecture — <project / date>

> Output template for the target/engine/runtime decision and the architecture that follows. One per project (revisit on a target change). Every device/version/perf cell carries a source + date or `[verify-at-use]`; no PII.

## Header
- **Project / use-case:** _____
- **Audience & their device(s):** _____
- **Prepared:** 2026-__-__  · **Owner:** _____

## 1. Target platform
| Decision | Choice | Basis | Flag |
|---|---|---|---|
| Device class (standalone / PC-VR / WebXR / mobile-AR) | | use-case + audience device | _[verify-at-use]_ |
| Specific target device(s) | | | _[verify-at-use]_ |
| Distribution channel | | store / sideload / web / MDM | _[verify-at-use]_ |
| Multi-device reach? | | drives OpenXR seams | n/a |

## 2. Engine & runtime
| Decision | Choice | Basis | Flag |
|---|---|---|---|
| Engine (Unity / Unreal / native-OpenXR / WebXR) | | team + target | _[verify-at-use]_ |
| Runtime | | OpenXR-first? | _[verify-at-use]_ |
| Required extensions (hand-tracking / passthrough / foveation) | | supported on target? | _[verify-at-use]_ |

## 3. Perf & comfort envelope
| Constraint | Value | Flag |
|---|---|---|
| Target refresh -> per-eye budget (ms) | | _[verify-at-use]_ per device |
| Render path (single-pass / stereo) | | n/a |
| Locomotion scheme + comfort defaults | | n/a |
| Play space / guardian design (seated / standing / room-scale) | | n/a |

## 4. Per-device seams (OpenXR-first)
- **Shared core:** _____
- **Behind a seam (per-device):** _passthrough / hand-tracking / controller profiles / foveation_
- **Per-device optimization pass (last):** _____

## Headline + risks
- **Headline decision:** _the target + engine bet, in one line_
- **Top risks:** _the reversal-expensive assumptions + how they're verified_
- **Two things that would change the answer:** _____

---
_Plus the ravenclaude-core Structured Output block. All device/version/perf cells: verify-at-use before commitment. Seams: xr-interaction-engineer (input/locomotion), spatial-rendering-engineer (frame budget)._
