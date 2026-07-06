---
description: "Choose the XR target platform (standalone / PC-VR / WebXR / mobile-AR) and engine (Unity / Unreal / native-OpenXR / WebXR) on the use-case and audience device, with an OpenXR-first architecture and the perf/comfort envelope named (device specifics verify-at-use)."
argument-hint: "[use-case + audience device(s) + distribution channel]"
---

You are running `/ar-vr-xr-engineering:choose-xr-stack`. Use `xr-architect-lead` + the `xr-target-and-engine-selection` skill.

> Engineering judgment, not certification advice. Every headset spec, runtime/OpenXR-support claim, and engine-version detail is `[verify-at-use]`. No PII.

## Steps
1. Capture the use-case, the audience's actual device(s), and the distribution channel (not the newest headset).
2. Traverse the **target platform choice** and **engine choice** trees in `knowledge/xr-decision-trees.md`.
3. Decide the target class + engine + runtime, commit OpenXR-first, and name the per-eye perf budget and comfort envelope the target implies — each device/version specific flagged `[verify-at-use]`.
4. Identify the per-device seams (passthrough, hand-tracking, controller profiles) and defer per-device optimization to last.
5. Emit using `templates/xr-project-architecture.md` + the Structured Output block, handing input/locomotion to `xr-interaction-engineer` and the frame budget to `spatial-rendering-engineer`.
