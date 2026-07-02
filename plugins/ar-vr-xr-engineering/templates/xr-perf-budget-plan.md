# XR Perf-Budget Plan — <project / target device / date>

> Output template for the per-eye frame budget and the optimization plan against it. One per target device. Every device number carries a source + date or `[verify-at-use]`; profile ON DEVICE; no PII.

## Header
- **Project / target device:** _____
- **Refresh rate (Hz):** _____  · **Per-eye budget (ms = 1000 / Hz):** _____
- **Prepared:** 2026-__-__  · **Owner:** _____

## 1. Budget & bound
| Item | Value | Flag |
|---|---|---|
| Per-eye frame budget (ms) | | _[verify-at-use]_ per device |
| Measured frame time (on-device capture) | | on-device only |
| Bound type (CPU / GPU / thermal) | | from profiler |
| Reprojection / dropped-frame rate | | near zero target |

## 2. Cost breakdown (on-device profile)
| Cost | Current | Ceiling | Flag |
|---|---|---|---|
| Draw calls / batches per eye | | | _[verify-at-use]_ |
| Overdraw / transparency | | | _[ESTIMATE]_ |
| Shader / fill cost | | | _[verify-at-use]_ |
| Physics / scripting (CPU) | | | n/a |
| Sustained thermal frame time | | budget @ throttled clock | _[verify-at-use]_ |

## 3. Optimization plan (ordered, highest leverage first)
| # | Action | Owner | Expected ms recovered | Bound it targets |
|---|---|---|---|---|
| 1 | Batch/instance, atlas, single-pass stereo | | | CPU draw calls |
| 2 | Cut overdraw / transparency | | | GPU fill |
| 3 | Foveated rendering (fixed / eye-tracked) | | | GPU |
| 4 | Shader / geometry / LOD reduction | | | GPU |
| 5 | Reduce sustained load for thermal | | | thermal |

## Headline + actions
- **Headline:** _budget vs measured, and the bound_
- **Top 2 actions:** _action — owner — expected ms recovered — by when_
- **Reprojection note:** _is the net a safety margin or a crutch?_

---
_Plus the ravenclaude-core Structured Output block. Reprojection is a net, not a plan. Test sustained, not peak. Seams: xr-architect-lead (target/budget), xr-interaction-engineer (content cost)._
