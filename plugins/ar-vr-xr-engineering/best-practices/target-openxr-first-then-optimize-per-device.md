# Target OpenXR first, then optimize per device

**Status:** Pattern
**Domain:** Architecture / portability
**Applies to:** `ar-vr-xr-engineering`

> Engineering pattern. Runtime/extension support is `[verify-at-use]` per device. No PII.

---

## Why this exists

OpenXR is the Khronos vendor-neutral runtime API that lets one codebase address multiple headsets. Building to it first is the cheap hedge against a volatile hardware market: it buys multi-device reach without three codebases, and it isolates the parts that genuinely differ per device (passthrough, hand-tracking extensions, controller interaction profiles) behind seams. Hard-wiring one vendor's SDK feels faster on day one and turns into a re-port when the target changes.

## How to apply

- Build the shared core against OpenXR actions/interaction profiles and the standard render loop.
- Put per-device concerns (passthrough, hand-tracking, foveated rendering, controller profiles) behind abstraction seams — confirm the extension is supported on the target (`[verify-at-use]`).
- Do the device-specific optimization pass **last**, once the shared experience works.
- When reach spans several headsets, this is the default; even single-device builds target OpenXR so the door stays open.

**Do:** isolate vendor extensions behind interfaces; verify OpenXR + extension support on the target before committing.
**Don't:** scatter one vendor's SDK calls through gameplay code; optimize per-device before the shared core runs.

## Edge cases / when the rule does NOT apply

A device with a distinct first-party SDK (some MR/spatial computers) may warrant native APIs for features OpenXR doesn't yet expose — isolate that behind the same seam and document the trade.

## See also

- [`../skills/xr-target-and-engine-selection/SKILL.md`](../skills/xr-target-and-engine-selection/SKILL.md)
- Decision trees: [`../knowledge/xr-decision-trees.md`](../knowledge/xr-decision-trees.md)

## Provenance

Codifies `xr-architect-lead` house opinion and the target/engine decision trees. Runtime/engine landscape: [`../knowledge/xr-reference-2026.md`](../knowledge/xr-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
