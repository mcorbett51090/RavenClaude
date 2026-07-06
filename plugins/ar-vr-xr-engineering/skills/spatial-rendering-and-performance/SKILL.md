---
name: spatial-rendering-and-performance
description: "Hold the XR frame budget: derive the per-eye ms target from the device refresh rate, profile on device to find the CPU-vs-GPU-vs-thermal bound, cut draw calls / overdraw / fill rate in order, and use foveated rendering and reprojection as headroom not a crutch — budgeting for the thermal-sustained clock, not peak. Device numbers verify-at-use."
---

# Spatial Rendering & Performance

The discipline of holding the frame. In XR a dropped frame is discomfort, so the frame budget is the top constraint and everything else is spent against it.

> **Engineering judgment.** Per-device ms budgets, draw-call ceilings, render-feature support, and thermal limits move with hardware and SDK versions — every number here is `[verify-at-use]`. No PII.

## Workflow

1. **Derive the per-eye budget.** Refresh rate fixes frame time (e.g., 72/90/120 Hz -> the matching ms). That is the hard ceiling.
2. **Profile on device to find the bound.** CPU-bound (draw calls, physics, scripting) vs GPU-bound (fill rate, overdraw, shader cost) vs thermal-throttled demand opposite fixes. Editor numbers are not device numbers.
3. **Cut in order.** Draw calls (batching/instancing, atlasing, single-pass stereo), then overdraw/transparency, then shader cost, then geometry/LOD. Highest leverage first.
4. **Spend headroom deliberately.** Foveated rendering (fixed or eye-tracked) buys GPU headroom; reprojection (ASW/spacewarp-style) covers occasional misses. Constant reprojection means you are over budget — fix the budget, don't lean on the net.
5. **Budget for thermal-sustained.** Test a sustained session and hold the budget at the throttled clock, not the 30-second-demo peak.

## Metrics table

| Metric | Target/read | Flag |
|---|---|---|
| Per-eye frame time vs budget (ms) | At or under the device's refresh-derived budget | `[verify-at-use]` per device |
| Reprojection / dropped-frame rate | Near zero in sustained use | `[verify-at-use]` |
| Draw calls / batches per eye | Under the target's ceiling | `[verify-at-use]` |
| GPU fill / overdraw factor | Bounded; transparency controlled | `[ESTIMATE]` |
| Sustained thermal frame time | Held at throttled clock | `[verify-at-use]` |

## Anti-patterns

- Optimizing before profiling — guessing the bound.
- Trusting editor framerate instead of on-device capture.
- Relying on reprojection to mask a chronically over-budget build.
- Passing a 30-second demo and shipping a build that throttles after ten minutes.

## See also

- Traverse the **rendering perf-budget triage** tree in [`../../knowledge/xr-decision-trees.md`](../../knowledge/xr-decision-trees.md).
- Dated per-eye targets and feature support: [`../../knowledge/xr-reference-2026.md`](../../knowledge/xr-reference-2026.md).
- Sibling skills: [`../xr-target-and-engine-selection/SKILL.md`](../xr-target-and-engine-selection/SKILL.md), [`../xr-interaction-and-locomotion/SKILL.md`](../xr-interaction-and-locomotion/SKILL.md).
- Best practices: [`../../best-practices/hold-the-frame-budget-above-all-else.md`](../../best-practices/hold-the-frame-budget-above-all-else.md), [`../../best-practices/test-on-device-early-and-often.md`](../../best-practices/test-on-device-early-and-often.md).
- Template: [`../../templates/xr-perf-budget-plan.md`](../../templates/xr-perf-budget-plan.md).
- Deep profiling methodology: [`../../../performance-engineering/CLAUDE.md`](../../../performance-engineering/CLAUDE.md).
