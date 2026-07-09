---
name: implement-twin-integration-and-simulation
description: Build a digital twin end to end — ingest the telemetry (MQTT / OPC-UA / Kafka, edge-vs-cloud) and bind it to the model (DTDL properties / AAS submodels), wire the physics or reduced-order/surrogate model, run simulation and what-if scenarios against live twin state, stand up 3D or dashboard visualization where it earns its keep, and — the step teams skip — validate fidelity against the real asset (predicted-vs-actual SLIs, error bounds, calibration) plus a drift monitor. Reach for this when the user asks "ingest our stream into the twin", "run a what-if simulation", "does the twin match the asset?", or "the twin has drifted". Used by `twin-integration-engineer` (primary).
---

# Skill: implement-twin-integration-and-simulation

> **Invoked by:** `twin-integration-engineer` (primary). Also consulted by `digital-twin-architect` to confirm the chosen platform can express the model + simulation before the design is finalized.
>
> **When to invoke:** "Ingest our telemetry into the twin"; "wire the model"; "run a what-if simulation"; "build the visualization"; "does the twin actually match the machine?"; "the twin has drifted / predictions are off"; any move from a chosen design to a live, validated twin.
>
> **Output:** wired telemetry + model, a runnable simulation/what-if, a visualization at the right level, and a fidelity-validation run (predicted-vs-actual, error bounds, calibration) + a drift monitor.

## Procedure

1. **Confirm the data + sync model is captured.** Use [`design-twin-data-and-sync-model`](../design-twin-data-and-sync-model/SKILL.md) + [`../../knowledge/digital-twin-patterns-2026.md`](../../knowledge/digital-twin-patterns-2026.md): the signal list, sampling rates, transport, edge-vs-cloud split, and the DTDL/AAS bindings. Don't wire ingestion without it.
2. **Ingest telemetry and bind to the model.** Stand up the MQTT/OPC-UA/Kafka path per the design, pre-aggregate at the edge where specified, and bind each signal to its **DTDL property / AAS submodel element**. Verify the twin's live state reflects the asset before going further.
3. **Wire the model per the chosen approach.** Physics/first-principles, reduced-order/surrogate, or hybrid — instantiate it so it consumes the bound properties. For a hybrid, keep clear which parameters are physics and which are calibrated from data.
4. **Run simulation & what-if from live twin state.** Drive the decision's scenarios ("throughput if we add a station?", "temperature if this fan fails?") starting from the *current* twin state — a simulation off stale or disconnected inputs is a model, not a twin. Surface results the decision can consume.
5. **Stand up visualization at the level the decision needs.** A 3D scene (Omniverse / Unity / Unreal) for spatial/operator-facing decisions; a dashboard or graph view for most predictive-maintenance signals. **Don't build a photoreal scene a gauge would answer.**
6. **VALIDATE fidelity against the real asset — not optional.** Follow [`../../templates/twin-fidelity-validation-report.md`](../../templates/twin-fidelity-validation-report.md): choose predicted-vs-actual SLIs on the decision-relevant outputs, compute **error bounds** (MAE/RMSE/% + a confidence interval on a hold-out or live window), **calibrate** to close the gap, and give a **fit-for-decision** verdict within the stated tolerance.
7. **Stand up a drift monitor and close the loop.** Monitor the predicted-vs-actual error; on drift, root-cause to **sensor / model / asset** before recalibrating, re-fit, and record it. Every validation + drift event yields a durable artifact (bounds, calibration, the monitor that catches the next divergence earlier).

## Worked example

> User: "The pump twin is built on Azure Digital Twins and the RUL predictions feel off lately. Wire it up properly and prove it matches the pumps."

- **Ingestion check:** vibration features + temperature stream over Kafka bind to the pump twin's DTDL properties; confirm live state tracks the asset (spot-check a known event).
- **Model:** the hybrid degradation ROM consumes the bound properties; physics sets the degradation structure, telemetry calibrates the rate parameters.
- **Simulation/what-if:** from current state, simulate RUL under "run 10% hotter" and "current load" — feed the maintenance decision.
- **Visualization:** a **dashboard** (RUL + confidence per pump + fleet roll-up), **not** a 3D scene — there's no spatial decision here.
- **Validation:** SLI = predicted vs realized time-to-failure on the last 12 months of pumps that did fail; error bounds RMSE = 1.8 days, 90% CI ±3 days. The **"feels off"** turns out to be **drift** — the pumps were re-impellered (an **asset** change), so the old calibration over-predicts life. **Recalibrate** the rate parameters on post-change data; RMSE drops to 0.9 days → **fit-for-decision** (clears the ±1-day "service within a week" tolerance).
- **Drift monitor:** predicted-vs-actual RUL error, tolerance ±10%, alert to the maintenance channel with a recalibration runbook link — so the next asset change is caught, not discovered.

## Guardrails

- Don't wire ingestion without the captured data + sync model — bind signals to model properties, not to a bare database.
- A simulation/what-if must start from **live twin state**; off disconnected inputs it's a model, not a twin.
- Visualization is earned — 3D where space matters, a dashboard/gauge where a number answers the question.
- **Never call a twin done without validating it against the real asset** with stated error bounds and a fit-for-decision verdict — an un-validated twin is a confident guess.
- On drift, root-cause to **sensor / model / asset** before recalibrating — "recalibrate and move on" is symptom-chasing.
- Every twin ships with a drift monitor; an un-monitored twin diverges silently as the asset wears.
- Robot control loops / real-time autonomy off a bidirectional twin leave this layer for `robotics-autonomous-systems-engineering`; volatile platform/SDK/spec facts carry a retrieval date — see [`../../knowledge/digital-twin-patterns-2026.md`](../../knowledge/digital-twin-patterns-2026.md).
