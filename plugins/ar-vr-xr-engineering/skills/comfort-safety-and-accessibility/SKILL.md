---
name: comfort-safety-and-accessibility
description: "Treat XR comfort, physical safety, and accessibility as requirements: hold a sustained framerate, choose comfortable locomotion, design for the tracking volume / guardian / play-space and passthrough so users don't hit walls, and ship accessibility options (seated mode, one-handed paths, snap turn, captions, adjustable text) as defaults. Comfort research verify-at-use."
---

# Comfort, Safety & Accessibility

The non-negotiable layer. A technically excellent XR experience that makes users sick, lets them hit a wall, or excludes people has shipped nothing usable. Comfort, physical safety, and accessibility are acceptance criteria across every agent's work.

> **Engineering judgment, not medical or safety-certification advice.** Comfort research, guardian/boundary APIs, and accessibility guidance evolve; specifics carry a retrieval date + `[verify-at-use]`. These agents do not certify a device for medical or safety-critical use. No PII.

## Workflow

1. **Protect the framerate first.** Sustained, stable framerate is the single biggest comfort factor — a chronic frame-budget miss is a comfort failure (hand to `spatial-rendering-and-performance`).
2. **Choose comfortable locomotion and turning.** Prefer teleport/dash and snap turning for broad audiences; ship comfort mitigations (vignette, static reference frame, seated mode) as defaults when using smooth motion.
3. **Design for the physical space.** Respect the tracking volume, guardian/boundary, and play-space size; use passthrough and boundary cues so users don't punch a wall or trip. Room-scale, standing, and seated are different safety designs.
4. **Build in accessibility.** Seated/standing modes, one-handed and dominant-hand paths, adjustable height, snap-turn options, captions/subtitles, adjustable text size and contrast, and colorblind-safe cues — as defaults and options, not afterthoughts.
5. **Validate with real users on device.** Comfort and accessibility are measured in playtests across a range of people and session lengths, not asserted from the editor.

## Metrics table

| Metric | Read | Flag |
|---|---|---|
| Sustained framerate vs budget | Comfort floor held | `[verify-at-use]` per device |
| Comfort rating (playtest, sustained session) | Broad audience tolerates it | `[verify-at-use]` |
| Guardian/boundary + passthrough coverage | Physical-safety design present | `[verify-at-use]` |
| Accessibility options shipped as defaults | Reach and inclusion | n/a |

## Anti-patterns

- Burying comfort options in a menu and defaulting to the intense mode.
- Designing for a large play space a headset user may not have.
- Skipping the boundary/passthrough safety design in a standing/room-scale build.
- Deferring accessibility to a post-launch backlog.

## See also

- Traverse the **locomotion scheme to reduce sim-sickness** tree in [`../../knowledge/xr-decision-trees.md`](../../knowledge/xr-decision-trees.md).
- Dated comfort/safety specifics: [`../../knowledge/xr-reference-2026.md`](../../knowledge/xr-reference-2026.md).
- Sibling skills: [`../xr-interaction-and-locomotion/SKILL.md`](../xr-interaction-and-locomotion/SKILL.md), [`../spatial-rendering-and-performance/SKILL.md`](../spatial-rendering-and-performance/SKILL.md).
- Best practices: [`../../best-practices/comfort-is-a-requirement-not-a-setting.md`](../../best-practices/comfort-is-a-requirement-not-a-setting.md), [`../../best-practices/design-for-the-tracking-volume-and-guardian.md`](../../best-practices/design-for-the-tracking-volume-and-guardian.md).
- General accessibility standards: [`../../../accessibility-engineering/CLAUDE.md`](../../../accessibility-engineering/CLAUDE.md).
