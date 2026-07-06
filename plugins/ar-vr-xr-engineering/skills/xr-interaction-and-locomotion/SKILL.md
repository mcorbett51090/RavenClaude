---
name: xr-interaction-and-locomotion
description: "Design and implement XR interaction: hand / controller / gaze input on an OpenXR action abstraction, locomotion chosen for comfort (teleport / dash / snap-turn vs smooth + vignette), reachable and readable 3D UI, and intentional grab/physics — with accessibility built in as a requirement. Input-API specifics verify-at-use."
---

# XR Interaction & Locomotion

How the user reaches into the experience and moves through it. This is where XR feels natural or feels wrong, and where comfort is won or lost.

> **Engineering judgment.** Input APIs, interaction profiles, and comfort research evolve; specifics carry a retrieval date + `[verify-at-use]`. Comfort and accessibility are acceptance criteria, not preferences. No PII.

## Workflow

1. **Abstract the input source.** Target OpenXR actions/interaction profiles so a single interaction binds across hands, controllers, and gaze and degrades gracefully when a modality is missing.
2. **Choose locomotion for comfort.** Match the scheme to the audience and session: teleport/dash + snap turning for broad/seated audiences; smooth locomotion only with comfort mitigations (vignette/tunneling, static reference frame, seated mode) shipped as defaults.
3. **Lay out 3D UI for reach and readability.** Comfortable depth and angular size, world/head/hand anchoring by task, hit targets sized for ray vs poke, text sized and contrasted for headset optics.
4. **Make grab/physics intentional.** Decide kinematic vs physics grab, attach transforms, two-hand manipulation, and haptics — don't inherit "floaty" and "clippy" by default.
5. **Bake in accessibility.** Seated/standing modes, one-handed and dominant-hand paths, snap-turn options, captions, adjustable text — designed in, not retrofitted.

## Metrics table

| Metric | What it watches | Flag |
|---|---|---|
| Sim-sickness / comfort rating in playtests | Whether locomotion + framerate are comfortable | `[verify-at-use]` per audience |
| Interaction success rate (grab/target hit) | Whether input feels responsive and hittable | n/a |
| Input-modality coverage (hands + controllers + gaze) | Portability of the interaction layer | `[verify-at-use]` per device |
| Accessibility options shipped as defaults | Audience reach | n/a |

## Anti-patterns

- Hard-coding a controller and breaking on hand-tracking-only devices.
- Smooth locomotion with no comfort mitigations, on by default.
- UI placed too close/far or with text too small to read through the optics.
- Treating accessibility as a post-launch backlog item.

## See also

- Traverse the **locomotion scheme to reduce sim-sickness** tree in [`../../knowledge/xr-decision-trees.md`](../../knowledge/xr-decision-trees.md).
- Dated input/comfort specifics: [`../../knowledge/xr-reference-2026.md`](../../knowledge/xr-reference-2026.md).
- Sibling skills: [`../comfort-safety-and-accessibility/SKILL.md`](../comfort-safety-and-accessibility/SKILL.md), [`../xr-target-and-engine-selection/SKILL.md`](../xr-target-and-engine-selection/SKILL.md).
- Best practices: [`../../best-practices/comfort-is-a-requirement-not-a-setting.md`](../../best-practices/comfort-is-a-requirement-not-a-setting.md), [`../../best-practices/design-for-the-tracking-volume-and-guardian.md`](../../best-practices/design-for-the-tracking-volume-and-guardian.md).
