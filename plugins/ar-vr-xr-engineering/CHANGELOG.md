# Changelog — ar-vr-xr-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-02

Initial release.

### Added

- **3 agents** — `xr-architect-lead` (target selection, engine choice, OpenXR strategy, perf-budget & comfort architecture), `xr-interaction-engineer` (hand/controller/gaze input, locomotion, 3D UI, grab/physics, accessibility), `spatial-rendering-engineer` (frame budget, reprojection, foveated rendering, occlusion/anchors/passthrough, draw-call batching, thermal budget).
- **4 skills** — `xr-target-and-engine-selection`, `xr-interaction-and-locomotion`, `spatial-rendering-and-performance`, `comfort-safety-and-accessibility`.
- **Knowledge bank** — `xr-decision-trees.md` (4 Mermaid trees: target platform choice, engine choice, locomotion scheme to reduce sim-sickness, rendering perf-budget triage) and `xr-reference-2026.md` (dated reference: headset/device-class landscape, runtime/API landscape, engine landscape, per-eye perf-budget targets `[ESTIMATE]`, comfort/safety concepts — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — hold the frame budget above all else, comfort is a requirement not a setting, design for the tracking volume and guardian, target OpenXR first then optimize per-device, test on device early and often.
- **2 templates** — xr-project-architecture, xr-perf-budget-plan.
- **2 commands** — `/choose-xr-stack`, `/plan-xr-perf-budget`.

### Scope & verify-at-use

- **Engineering judgment, not legal, medical, or safety-certification advice.** The agents store no PII.
- The headset / runtime / engine landscape is volatile — every device spec, OpenXR/WebXR support claim, engine version, per-eye perf number, and comfort mitigation in `xr-reference-2026.md` carries a retrieval date + `[verify-at-use]`; re-confirm against the vendor/runtime/engine docs before quoting or committing.
- Seams to `game-development` (engine gameplay/assets), `frontend-engineering` (WebXR in a web app), `performance-engineering` (deep profiling), and `accessibility-engineering` (general accessibility standards).
