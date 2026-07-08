# AR/VR/XR Engineering — Decision Trees

> Reference decision trees for the `ar-vr-xr-engineering` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Engineering judgment, not certification advice.** Anything touching a headset spec, runtime/engine version, per-eye perf number, or comfort claim is `[verify-at-use]` — confirm against the vendor/runtime/engine docs before it drives a build commitment. No PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Principles are durable; dated specifics live in [`xr-reference-2026.md`](xr-reference-2026.md)._

---

## Decision Tree: which target platform?

```mermaid
flowchart TD
    A[New XR project] --> B{Primary use-case + audience}
    B -- "mass-reach consumer/enterprise,<br/>untethered, mobile budget" --> C[Standalone headset<br/>mobile SoC — tight frame budget]
    B -- "max fidelity, seated/room,<br/>PC available or streamed" --> D[PC-VR<br/>desktop GPU — larger budget]
    B -- "zero-install, broadest reach,<br/>in-browser" --> E[WebXR<br/>tightest budget, browser support gates it]
    B -- "widest install base,<br/>phone/tablet AR" --> F[Mobile-AR<br/>handheld, world/plane tracking]
    C --> G{Must reach several<br/>headsets?}
    D --> G
    G -- yes --> H[OpenXR-first core<br/>+ per-device seams]
    G -- no --> I[Still target OpenXR;<br/>single-device optimize]
```

**Rule:** pick the device class on the **use-case and the audience's actual device**, not the newest headset. The class fixes the perf universe. Target OpenXR regardless; add per-device seams when reach spans headsets. All device specs `[verify-at-use]`.

---

## Decision Tree: which engine?

```mermaid
flowchart TD
    A[Target class chosen] --> B{Team skills + fidelity need}
    B -- "broad device reach,<br/>C# team, fast XR tooling" --> C[Unity<br/>XR Interaction Toolkit, wide device support]
    B -- "top fidelity, C++/Blueprint,<br/>cinematic" --> D[Unreal<br/>higher baseline cost/budget]
    B -- "max control, no engine tax,<br/>graphics-strong team" --> E[Native + OpenXR<br/>most effort, most control]
    B -- "browser reach, web team" --> F[WebXR<br/>three.js/Babylon/A-Frame — tightest budget]
    C --> G{OpenXR + needed extensions<br/>supported on target? verify-at-use}
    D --> G
    E --> G
    F --> G
    G -- no --> H[Re-check target or extension plan<br/>before committing]
    G -- yes --> I[Commit; isolate per-device concerns behind seams]
```

**Rule:** choose the engine on **team skills + the target**, not habit. Confirm OpenXR and the extensions you need (hand-tracking, passthrough, controller profiles) are supported on the target — `[verify-at-use]` — before committing.

---

## Decision Tree: locomotion scheme to reduce sim-sickness

```mermaid
flowchart TD
    A[Need to move the user] --> B{Does the user actually<br/>need to translate through space?}
    B -- no --> C[Teleport / snap-to-point<br/>+ snap turning — most comfortable]
    B -- yes --> D{Broad/mixed audience or<br/>long sessions?}
    D -- yes --> E[Dash/blink or teleport,<br/>snap turn, seated mode default]
    D -- "no — VR-experienced,<br/>short, comfort-tolerant" --> F{Use smooth locomotion?}
    F -- yes --> G[Smooth + comfort mitigations ON by default:<br/>vignette/tunneling, static reference frame]
    F -- no --> E
    C --> H[Ship a11y options:<br/>seated/standing, one-handed, dominant hand]
    E --> H
    G --> H
```

**Rule:** vection drives sim-sickness — default to the **comfortable** scheme (teleport/dash + snap turn) and make comfort mitigations defaults, not buried options. Smooth locomotion is opt-in for comfort-tolerant audiences. Comfort is a requirement; validate on real users. `[verify-at-use]` comfort research.

---

## Decision Tree: rendering perf-budget triage

```mermaid
flowchart TD
    A[Below frame budget / reprojection firing] --> B{Profiled ON DEVICE?}
    B -- no --> C[Capture on device first<br/>— editor numbers are not device numbers]
    B -- yes --> D{CPU-bound or GPU-bound?}
    D -- "CPU-bound" --> E[Cut draw calls: batch/instance,<br/>atlas, single-pass stereo;<br/>trim physics/scripting]
    D -- "GPU-bound" --> F[Cut overdraw/transparency,<br/>fill rate, shader cost; add foveated rendering]
    D -- "thermal-throttled" --> G[Lower sustained load;<br/>budget at throttled clock, not peak]
    E --> H{Inside budget now?}
    F --> H
    G --> H
    H -- no --> I[Reduce geometry/LOD, scene complexity;<br/>reprojection is a net, not a plan]
    H -- yes --> J[Lock budget; spend headroom deliberately]
```

**Rule:** profile **on device** before optimizing, fix to the **bound** (CPU vs GPU vs thermal), cut draw calls/overdraw first, and hold the budget at the **thermal-sustained** clock. Reprojection is a safety net, not a strategy. Per-eye targets `[verify-at-use]`.

---

## See also

- [`xr-reference-2026.md`](xr-reference-2026.md) — dated headset/runtime landscape + per-eye perf targets (verify-at-use).
- Skills: [`../skills/xr-target-and-engine-selection/SKILL.md`](../skills/xr-target-and-engine-selection/SKILL.md), [`../skills/xr-interaction-and-locomotion/SKILL.md`](../skills/xr-interaction-and-locomotion/SKILL.md), [`../skills/spatial-rendering-and-performance/SKILL.md`](../skills/spatial-rendering-and-performance/SKILL.md), [`../skills/comfort-safety-and-accessibility/SKILL.md`](../skills/comfort-safety-and-accessibility/SKILL.md).
