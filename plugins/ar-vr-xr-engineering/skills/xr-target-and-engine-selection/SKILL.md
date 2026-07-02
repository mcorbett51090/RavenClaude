---
name: xr-target-and-engine-selection
description: "Choose the XR target platform (standalone headset vs PC-VR vs WebXR vs mobile-AR) and engine (Unity / Unreal / native-OpenXR / WebXR) on the use-case, audience device, and distribution channel — then commit to an OpenXR-first architecture and derive the per-eye perf budget the target implies. Device/version specifics verify-at-use."
---

# XR Target & Engine Selection

The first and most expensive XR decision: what device class you target and what you build it on. Everything downstream — frame budget, available input, comfort ceiling — is fixed by this choice, so make it deliberately.

> **Engineering judgment, device landscape is volatile.** Headset specs, runtime/OpenXR support, and engine XR-feature parity change with every SDK release. Every device/version specific here is `[verify-at-use]` — confirm against the vendor/runtime docs before it drives a build commitment. No PII.

## Workflow

1. **State the use-case and audience.** Training, location-based entertainment, design review, consumer game, and enterprise AR have different fidelity, session-length, and distribution needs.
2. **Pick the device class on the use-case.** Standalone (mobile SoC, untethered, mass reach) vs PC-VR (tethered/streamed, high fidelity) vs WebXR (browser, zero-install, tight budget) vs mobile-AR (phone/tablet, widest install base). The class fixes the perf universe.
3. **Choose the engine on team + target.** Unity (broad XR device reach, C#, mature XR Interaction Toolkit), Unreal (fidelity, C++/Blueprint), native/OpenXR (max control, no engine tax), WebXR (reach, tightest budget). Name the trade — don't default to what the team last used without checking it fits the target.
4. **Commit OpenXR-first.** Build to the vendor-neutral runtime, isolate per-device concerns (passthrough, hand-tracking, controller profiles) behind seams, and schedule the device-specific optimization pass last.
5. **Derive the perf budget.** The target's refresh rate fixes a per-eye ms budget — hand it to `spatial-rendering-and-performance` as a hard constraint.

## Metrics table

| Decision input | What it tells you | Flag |
|---|---|---|
| Target refresh rate (Hz) | Per-eye frame budget (fps -> ms) | `[verify-at-use]` per device |
| Compute class (mobile SoC vs desktop GPU) | Realistic scene/draw-call ceiling | `[verify-at-use]` |
| Distribution channel (store / sideload / web / MDM) | Reach and update model | `[verify-at-use]` |
| OpenXR + extension support on target | Multi-device portability, hand-tracking/passthrough availability | `[verify-at-use]` |
| Engine XR feature parity for the target | Build cost and risk | `[verify-at-use]` |

## Anti-patterns

- Choosing the newest headset instead of the one the audience owns.
- Picking the engine on team habit without checking XR-feature parity for the target.
- Treating OpenXR as optional and hard-wiring one vendor's SDK, then re-porting.
- Deferring the perf budget until after the scene is built.

## See also

- Traverse the **target platform choice** and **engine choice** trees in [`../../knowledge/xr-decision-trees.md`](../../knowledge/xr-decision-trees.md).
- Dated landscape: [`../../knowledge/xr-reference-2026.md`](../../knowledge/xr-reference-2026.md).
- Sibling skills: [`../spatial-rendering-and-performance/SKILL.md`](../spatial-rendering-and-performance/SKILL.md), [`../comfort-safety-and-accessibility/SKILL.md`](../comfort-safety-and-accessibility/SKILL.md).
- Best practices: [`../../best-practices/target-openxr-first-then-optimize-per-device.md`](../../best-practices/target-openxr-first-then-optimize-per-device.md), [`../../best-practices/hold-the-frame-budget-above-all-else.md`](../../best-practices/hold-the-frame-budget-above-all-else.md).
- Template: [`../../templates/xr-project-architecture.md`](../../templates/xr-project-architecture.md).
