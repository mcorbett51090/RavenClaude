---
name: choose-digital-twin-architecture
description: Scope and architect a digital twin for a described asset and decision by traversing the digital-twin architecture decision tree (decision it informs → twin type → shadow-vs-bidirectional → descriptive/predictive/prescriptive → modeling approach → fidelity → sync → platform), then return the twin scope/type, the fidelity level (only as much as the decision needs), the modeling approach (physics vs data-driven/surrogate/reduced-order vs hybrid), the platform (DTDL+Azure Digital Twins / AAS / Eclipse Ditto / Omniverse / Unity-Unreal / Bentley-Siemens), the state-sync strategy, and the conditions that would flip the choice. Reach for this when the user asks "we want a twin of <X> — where do we start?", "physics vs data-driven vs hybrid?", "how much fidelity?", "which twin platform?", or "shadow or bidirectional?". Used by `digital-twin-architect` (primary).
---

# Skill: choose-digital-twin-architecture

> **Invoked by:** `digital-twin-architect` (primary). Also consulted by `twin-integration-engineer` when a build reveals the chosen fidelity/platform can't express a required behavior.
>
> **When to invoke:** "We want a digital twin of <asset/process> — where do we start?"; "physics model, data-driven surrogate, or hybrid?"; "how much fidelity do we need?"; "Azure Digital Twins, Ditto, AAS, or Omniverse?"; "digital shadow or a true bidirectional twin?"; any "what should this twin be?" question.
>
> **Output:** the twin scope/type + shadow-vs-bidirectional + maturity + fidelity level + modeling approach + platform + state-sync strategy + the 1-2 flip conditions that would change the answer.

## Procedure

1. **Name the decision the twin must inform — first.** "Should we service this pump this week?" (predictive maintenance), "what throughput if we add a station?" (what-if/prescriptive), "is the line running to spec right now?" (descriptive/monitoring). Everything below is scoped by this. **A twin that answers no question is a rendering — say so and stop.**
2. **Classify the twin type.** Asset/component (one pump), process (a line/batch), or system-of-systems (a plant/fleet/grid). The type sets how many sub-twins and relationships you're modeling.
3. **Decide shadow vs bidirectional.** One-way **digital shadow** (monitor/predict) unless the twin genuinely **actuates back** (closed-loop control). Bidirectional inherits safety/latency/control-authority burden — flag the seam to `robotics-autonomous-systems-engineering`. Default to shadow; earn bidirectional.
4. **Set the maturity.** Descriptive/informative ("what's happening"), predictive ("what will happen"), or prescriptive ("what should we do") — the highest the decision actually needs, no more.
5. **Choose the modeling approach.** Physics/first-principles (equations known, data scarce, must extrapolate), data-driven/surrogate/reduced-order (rich history, need speed), or **hybrid** (physics for structure, data to calibrate — the default in practice). State why.
6. **Right-size the fidelity to the decision's error tolerance.** Find the *lowest* fidelity that clears the tolerance; escalate to full physics + 3D only where spatial/dynamic behavior is what the decision hinges on. Name what more fidelity would buy and cost.
7. **Traverse the decision tree** in [`../../knowledge/digital-twin-decision-tree.md`](../../knowledge/digital-twin-decision-tree.md) to the **platform**:
   - standards-based twin graph on an Azure estate → **DTDL + Azure Digital Twins**,
   - open-source, vendor-neutral device-twin state → **Eclipse Ditto**,
   - cross-vendor interoperability / Industrie 4.0 → **AAS / Asset Administration Shell** (ISO 23247-aligned),
   - physics-accurate 3D / spatial / operator-facing → **NVIDIA Omniverse / Unity / Unreal**,
   - BIM/CAD-anchored plant or built-asset lifecycle → **Bentley / Siemens**.
8. **Design the state-sync strategy:** cadence (periodic vs streaming), edge-vs-cloud split, the sync-latency budget the decision tolerates, and the **drift-detection + recalibration** policy.
9. **State the flip conditions** — the 1-2 facts that, if different, change the answer (e.g., "if closed-loop actuation enters scope, bidirectional + the robotics seam replace the shadow").

## Worked example

> User: "We run a fleet of industrial pumps and keep getting surprised by failures. We have 2 years of vibration + temperature telemetry. Do we need Omniverse? Azure Digital Twins? How much fidelity?"

- **Decision:** "service a pump *before* it fails" → **predictive maintenance** (predictive maturity), a **digital shadow** (no actuation back).
- **Type:** an **asset twin** per pump, rolled up into a **system-of-systems** fleet view.
- **Modeling approach:** **hybrid** — a reduced-order vibration/thermal degradation model calibrated on the 2 years of telemetry; not full CFD (the decision doesn't need it).
- **Fidelity:** **low-to-medium** — a ROM predicting remaining-useful-life within ±1 day clears the "service within a week" tolerance. **Omniverse is not justified** — there's no spatial decision; a dashboard + RUL signal answers it.
- **Platform:** **DTDL + Azure Digital Twins** for the twin graph (a twin per pump + the fleet relationships) and telemetry routing; the ROM runs alongside. Hold Omniverse for a future scenario that needs 3D.
- **Sync:** streaming vibration features pre-aggregated at the **edge**, minutes-cadence cloud sync (maintenance is a human-timescale decision); a **drift monitor** on predicted-vs-actual RUL.
- **Flip condition:** if the fleet later needs closed-loop speed control off the twin, re-scope to **bidirectional** and open the `robotics-autonomous-systems-engineering` seam.

## Guardrails

- Never scope a twin from the asset ("model everything") — scope from the decision it informs; a purpose-less twin is a rendering.
- Only as much fidelity as the decision's error tolerance needs — photoreal 3D and full physics are costs, not defaults.
- Default to a digital shadow; go bidirectional only when actuation is genuinely in scope, and name the safety/latency/control-authority cost + the robotics seam.
- Never name a platform before traversing the tree — approach and fidelity before brand.
- Design drift detection + recalibration in from the start; an un-validated, un-monitored twin manufactures false confidence.
- Device firmware / edge drivers / robot control loops are **not** twin work — route to `embedded-iot-engineering` / `robotics-autonomous-systems-engineering`.
- Volatile claims (platform features, pricing, ISO 23247 / AAS / DTDL revisions) carry a **retrieval date** and are re-verified before a client commitment. See [`../../knowledge/digital-twin-patterns-2026.md`](../../knowledge/digital-twin-patterns-2026.md).
