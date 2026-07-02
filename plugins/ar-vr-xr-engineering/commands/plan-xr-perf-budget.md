---
description: "Derive the per-eye XR frame budget for a target device, triage the CPU-vs-GPU-vs-thermal bound from an on-device profile, and produce an ordered optimization plan that holds the budget at the thermal-sustained clock (device numbers verify-at-use)."
argument-hint: "[target device + render path + profiling capture or frame-time symptom]"
---

You are running `/ar-vr-xr-engineering:plan-xr-perf-budget`. Use `spatial-rendering-engineer` + the `spatial-rendering-and-performance` skill.

> Engineering judgment. Every per-eye ms budget, draw-call ceiling, and device number is `[verify-at-use]`. Profile ON DEVICE, not the editor. No PII.

## Steps
1. Derive the per-eye budget from the target's refresh rate (frame time = 1000 / refresh_hz) and confirm the target device number `[verify-at-use]`.
2. Traverse the **rendering perf-budget triage** tree in `knowledge/xr-decision-trees.md` — confirm an on-device profile exists, then identify the bound (CPU / GPU / thermal).
3. Build the ordered optimization plan (draw calls/batching -> overdraw -> foveated rendering -> shaders/geometry -> thermal), with expected ms recovered and an owner per item.
4. Check reprojection is a safety net, not a crutch, and budget at the thermal-sustained clock, not peak.
5. Emit using `templates/xr-perf-budget-plan.md` + the Structured Output block, taking the target from `xr-architect-lead` and the content cost from `xr-interaction-engineer`.
