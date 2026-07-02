# ar-vr-xr-engineering — best-practice docs

Named, citable rules for the `ar-vr-xr-engineering` team's specialists. Each file is **one rule**. Engineering judgment, not certification advice; device/runtime/engine specifics are `[verify-at-use]`; no PII.

---

## Index

_5 rules across the frame budget, comfort, physical safety, the OpenXR-first strategy, and on-device testing._

| Doc | Status | Use when |
|---|---|---|
| [`hold-the-frame-budget-above-all-else.md`](./hold-the-frame-budget-above-all-else.md) | Absolute rule | Any XR build — the per-eye frame budget is the top constraint; a dropped frame is a comfort bug. |
| [`comfort-is-a-requirement-not-a-setting.md`](./comfort-is-a-requirement-not-a-setting.md) | Absolute rule | Locomotion, framerate, and interaction — ship the comfortable, accessible choice as the default. |
| [`design-for-the-tracking-volume-and-guardian.md`](./design-for-the-tracking-volume-and-guardian.md) | Absolute rule | Room-scale / standing builds — design for the play space, guardian/boundary, and passthrough so users stay safe. |
| [`target-openxr-first-then-optimize-per-device.md`](./target-openxr-first-then-optimize-per-device.md) | Pattern | Architecture — build to OpenXR, isolate per-device concerns behind seams, optimize per-device last. |
| [`test-on-device-early-and-often.md`](./test-on-device-early-and-often.md) | Absolute rule | Any XR build — profile and playtest on the target hardware, not the editor. |

---

Each rule cites its provenance and carries a `Last reviewed` date. Volatile device/runtime/engine/perf specifics live (dated, verify-at-use) in [`../knowledge/xr-reference-2026.md`](../knowledge/xr-reference-2026.md).
