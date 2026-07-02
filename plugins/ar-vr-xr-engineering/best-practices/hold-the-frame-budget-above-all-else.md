# Hold the frame budget above all else

**Status:** Absolute rule
**Domain:** Rendering / performance
**Applies to:** `ar-vr-xr-engineering`

> Engineering rule. Per-eye budgets and device numbers are `[verify-at-use]`. No PII.

---

## Why this exists

In XR a dropped frame is not a stutter — it is discomfort, and sustained drops make users sick. The target device's refresh rate fixes a per-eye time budget (frame time = 1000 / refresh_hz), and that budget is the top constraint every other decision serves. A build that misses it is not "a bit slow"; it is uncomfortable, which for XR is a shipping-blocker.

## How to apply

- Derive the per-eye ms budget from the target's refresh rate and treat it as a hard ceiling handed down from architecture (`[verify-at-use]` per device).
- Design scene complexity, draw calls, physics, and effects to finish inside the budget — don't build first and optimize later.
- Budget for the **thermal-sustained** clock on mobile-SoC headsets, not the peak demo.
- Keep reprojection headroom: if the net (ASW/spacewarp-style) is always firing, the build is over budget — fix the budget.

**Do:** treat a frame-budget miss at the severity of a crash; profile the bound before cutting.
**Don't:** rely on reprojection to mask chronic over-budget; ship a build that only passes a 30-second demo.

## Edge cases / when the rule does NOT apply

Seated, low-motion, mostly-static experiences tolerate a wider comfort margin, but the frame budget is still the ceiling — it just buys you slightly more slack in how you spend it.

## See also

- [`../skills/spatial-rendering-and-performance/SKILL.md`](../skills/spatial-rendering-and-performance/SKILL.md)
- Template: [`../templates/xr-perf-budget-plan.md`](../templates/xr-perf-budget-plan.md)

## Provenance

Codifies `spatial-rendering-engineer` house opinion and the rendering perf-budget triage tree. Per-eye targets: [`../knowledge/xr-reference-2026.md`](../knowledge/xr-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
