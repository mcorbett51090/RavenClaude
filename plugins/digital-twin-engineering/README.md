# digital-twin-engineering

> The **model-of-the-physical-asset layer** for Claude Code — the team that answers *"what should this twin model, at what fidelity, and does it actually match the real asset?"* and builds the telemetry-fed, simulated, **validated** twin that makes the answer defensible. Two agents: the **digital-twin-architect** (chooses scope/type, fidelity, modeling approach, sync strategy, and platform) and the **twin-integration-engineer** (ingests telemetry, wires the model, runs simulation, and validates fidelity).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "We want a digital twin of our pump / line / plant — where do we start?" | A twin scope + type anchored to the decision it must inform, with the fidelity ceiling that decision needs — not a photoreal replica for its own sake |
| "Physics model, data-driven surrogate, or hybrid?" | A modeling-approach verdict (first-principles vs reduced-order/surrogate vs hybrid) + the fidelity level, justified by the decision |
| "Azure Digital Twins + DTDL, Eclipse Ditto, an AAS shell, or Omniverse?" | A decision-tree-driven platform + sync-strategy choice + the conditions that would flip it |
| "Do we need the twin to actuate back, or just mirror the asset?" | A digital-shadow-vs-true-bidirectional decision with the safety, latency, and control-authority implications named |
| "Ingest our OPC-UA / MQTT stream into the twin." | A telemetry ingestion path (protocol, sampling, edge-vs-cloud, sync latency) bound to the DTDL/AAS model |
| "Does the twin actually match the machine?" | A fidelity-validation run: predicted-vs-actual on the decision SLIs, error bounds, calibration, and a drift monitor |

**Two rules it never breaks:** *a twin serves a decision or it's a rendering* (scope from the question, only as much fidelity as the decision needs), and *an un-validated twin is a liability* (the predicted-vs-actual error bounds are the deliverable, not the pretty 3D scene).

## What's inside

- **2 agents** — `digital-twin-architect` (chooses scope/type, shadow-vs-bidirectional, fidelity, modeling approach, sync, and platform) and `twin-integration-engineer` (ingests telemetry, wires the model, runs simulation/what-if, builds visualization, and validates fidelity + reconciles drift).
- **3 skills** — `choose-digital-twin-architecture`, `design-twin-data-and-sync-model`, `implement-twin-integration-and-simulation`.
- **2 knowledge files** — a Mermaid architecture decision tree (twin type → shadow-vs-bidirectional → maturity → modeling approach → fidelity → sync → platform, + trade-off table) and a 2026 digital-twin-patterns reference (taxonomy, the fidelity principle, modeling approaches, telemetry & sync, standards, simulation, drift/calibration, validation, platform map).
- **2 templates** — a digital-twin design spec and a twin-fidelity validation report.

## Where it sits in the physical-systems stack

```
embedded-iot-engineering              →  device firmware / sensors / edge / connectivity   ("get the signal off the machine")
robotics-autonomous-systems-eng.      →  robot control loops / motion / autonomy           ("make it move / decide in real time")
data-platform                         →  warehouse / lakehouse / BI                         ("store & serve the history")
manufacturing-operations              →  MES / OEE / production scheduling                  ("run the shop floor")
digital-twin-engineering (HERE)       →  MODEL, SIMULATE & VALIDATE the physical asset      ("does the model match reality, and what if…")
```

This plugin is the **twin layer** *over* the others: it consumes the telemetry `embedded-iot-engineering` gets off the asset, models and simulates it, stores its history in `data-platform`, informs `manufacturing-operations`, and hands real-time actuation to `robotics-autonomous-systems-engineering` when a twin goes bidirectional.

## Tooling stance

Concept-first (twin taxonomy, the fidelity-to-the-decision principle, shadow-vs-bidirectional, physics-vs-data-driven-vs-hybrid modeling, state sync & drift/calibration, fidelity validation), fluent across the standards — **DTDL + Azure Digital Twins**, **ISO 23247**, **AAS / Asset Administration Shell**, **Eclipse Ditto** — and the simulation/visualization stack — **NVIDIA Omniverse**, **Unity / Unreal**, and the **Bentley / Siemens** engineering platforms — with telemetry over **MQTT / OPC-UA / Kafka**. Platform feature sets, pricing, and standards revisions carry retrieval dates — re-verify before pinning in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install digital-twin-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
