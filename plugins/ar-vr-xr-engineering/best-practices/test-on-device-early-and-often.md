# Test on device early and often

**Status:** Absolute rule
**Domain:** Performance / QA
**Applies to:** `ar-vr-xr-engineering`

> Engineering rule. Device perf numbers are `[verify-at-use]`. No PII.

---

## Why this exists

Editor framerate is a comforting lie. A build that runs at hundreds of frames per second on a desktop editor can drop frames and overheat within minutes on a mobile-SoC headset, because the real SoC, thermal envelope, optics, and tracking only exist on the device. Comfort, frame budget, readability, and physical safety are all properties you can only truly measure on the target hardware — so the device test is not a final gate, it is a continuous loop.

## How to apply

- Profile on the target device from early in the project, not just before ship — capture the CPU/GPU/thermal bound on device.
- Playtest comfort and readability through the actual optics, with a range of real users and session lengths.
- Run a **sustained** session to catch thermal throttling, not a 30-second demo.
- Close the loop often: every significant scene or system change gets a device pass.

**Do:** treat the on-device capture as the source of truth; test sustained, not peak.
**Don't:** trust editor framerate; defer the first device test until the end.

## Edge cases / when the rule does NOT apply

Very early prototyping and tooling work can iterate in the editor — but any claim about performance, comfort, or safety must be confirmed on device before it's trusted.

## See also

- [`../skills/spatial-rendering-and-performance/SKILL.md`](../skills/spatial-rendering-and-performance/SKILL.md), [`../skills/comfort-safety-and-accessibility/SKILL.md`](../skills/comfort-safety-and-accessibility/SKILL.md)
- Template: [`../templates/xr-perf-budget-plan.md`](../templates/xr-perf-budget-plan.md)

## Provenance

Codifies `spatial-rendering-engineer` house opinion and the perf-budget triage tree. Device numbers: [`../knowledge/xr-reference-2026.md`](../knowledge/xr-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
