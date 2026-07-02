# ar-vr-xr-engineering

A RavenClaude plugin: an **AR/VR/XR (spatial computing) engineering** specialist team for the three engines of an XR build — system architecture, interaction, and spatial rendering & performance.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Engineering judgment — not legal, medical, or safety-certification advice.** The headset / runtime / engine landscape is volatile: every device spec, OpenXR/WebXR support claim, engine version, and per-eye perf number carries a retrieval date + `[verify-at-use]` and must be confirmed against the vendor/runtime/engine docs before it drives a build commitment. The agents store no PII.

## What it's for

Building XR well: picking the platform and engine bet you won't have to reverse, targeting OpenXR so one codebase reaches several headsets, interaction that feels natural and locomotion that doesn't make users sick, and holding the per-eye frame budget at a sustained thermal state so the experience stays comfortable and safe.

## Agents

| Agent | Use for |
|---|---|
| **xr-architect-lead** | Target selection (standalone / PC-VR / WebXR / mobile-AR), engine choice (Unity / Unreal / native-OpenXR / WebXR), OpenXR strategy, perf-budget & comfort architecture |
| **xr-interaction-engineer** | Hand / controller / gaze input, locomotion, 3D UI, grabbing/physics, accessibility |
| **spatial-rendering-engineer** | Frame budget, reprojection, foveated rendering, occlusion/anchors/passthrough (AR), draw-call batching, thermal budget |

## What's inside

- **4 skills** — xr-target-and-engine-selection, xr-interaction-and-locomotion, spatial-rendering-and-performance, comfort-safety-and-accessibility.
- **Knowledge bank** — [`xr-decision-trees.md`](knowledge/xr-decision-trees.md) (4 Mermaid trees: target platform choice, engine choice, locomotion scheme to reduce sim-sickness, rendering perf-budget triage) + [`xr-reference-2026.md`](knowledge/xr-reference-2026.md) (dated device/runtime/engine landscape + per-eye perf targets, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — XR project architecture, XR perf-budget plan.
- **2 commands** — `/choose-xr-stack`, `/plan-xr-perf-budget`.

## Seams

Engine gameplay/asset pipeline → [`game-development`](../game-development/) · WebXR in a broader web app → [`frontend-engineering`](../frontend-engineering/) · deep profiling → [`performance-engineering`](../performance-engineering/) · general accessibility standards → [`accessibility-engineering`](../accessibility-engineering/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install ar-vr-xr-engineering@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the scope, routing rules, house opinions, and the output contract.
