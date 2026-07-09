---
name: design-twin-data-and-sync-model
description: From a physical asset and its telemetry, derive the twin's data and synchronization model — the signal list and sampling rates, the transport protocol (MQTT / OPC-UA / Kafka), the edge-vs-cloud split, the sync-latency budget the decision tolerates, the binding of each signal to the twin's model properties (DTDL properties / AAS submodel elements), and the drift-detection + recalibration policy. Reach for this when the user asks "what data does this twin need and how often?", "map our sensor stream to the twin model", or "how fresh must the twin be?". Used by `twin-integration-engineer` and `digital-twin-architect`.
---

# Skill: design-twin-data-and-sync-model

> **Invoked by:** `twin-integration-engineer` (primary, to design the ingestion) and `digital-twin-architect` (to confirm the telemetry can feed the chosen fidelity before the design is fixed).
>
> **When to invoke:** "What data does this twin need, and at what rate?"; "map our OPC-UA / MQTT stream to the twin model"; "how fresh must the twin be?"; "edge or cloud for this signal?"; any move from an asset's raw telemetry to the twin's data + sync contract.
>
> **Output:** the signal list + sampling rates, the transport (MQTT/OPC-UA/Kafka), the edge-vs-cloud split, the sync-latency budget, the DTDL/AAS model binding, and the drift-detection + recalibration policy — captured in the design spec.

## Procedure

1. **Start from the decision and the model, not the sensors.** The chosen twin scope + fidelity (from `choose-digital-twin-architecture`) tell you which model properties exist. Work backward: which *signals* feed those properties? A signal the model doesn't consume is ingestion cost with no payoff.
2. **List the signals and their required sampling rate.** For each signal, name the rate the **decision** needs — vibration for bearing failure may need kHz; a tank temperature may need one sample a minute. **Over-sampling is cost, under-sampling is blindness** — justify each rate by the decision, not by the sensor's max.
3. **Choose the transport per source.** **OPC-UA** for plant/PLC machine data (rich information model), **MQTT** for lightweight device pub/sub over constrained links, **Kafka** as the stream backbone once data is off the edge (buffering, replay, fan-out to twin + warehouse). Name which, and why.
4. **Design the edge-vs-cloud split.** Pre-aggregate/filter at the **edge** where bandwidth, latency, or intermittent connectivity demand it (send features — an RMS, an FFT band — not every raw sample); do the heavy modeling in the **cloud**. State what computes where.
5. **Set the sync-latency budget.** How stale may the twin be and still serve the decision? Minutes/hours for a maintenance decision; sub-second for a control decision. This budget drives the cadence (periodic vs streaming) and the edge decision.
6. **Bind each signal to the model — not to a database.** Map signal → **DTDL property** / **AAS submodel element**. A twin is a live model of the asset, so ingested data lands on model properties; raw history can *also* flow to `data-platform`, but the twin binding is the point.
7. **Define the drift-detection + recalibration policy.** Which predicted-vs-actual error you monitor for drift, the tolerance, and how you recalibrate (parameter re-fit / data assimilation) when it fires. Capture the whole design in [`../../templates/digital-twin-design-spec.md`](../../templates/digital-twin-design-spec.md).

## Worked example

> User: "We have a CNC machine on OPC-UA and want a twin for spindle-health prediction. What data, how often, edge or cloud?"

- **Model properties (from the design):** spindle temperature, spindle load, vibration (bearing bands), and a derived degradation index → the twin's DTDL properties.
- **Signals & rates:** vibration at **~10 kHz** (bearing-fault frequencies need it); spindle temperature at **1 Hz**; spindle load at **10 Hz**. Justified by the failure physics, not the sensor's ceiling.
- **Transport:** **OPC-UA** off the machine controller; **Kafka** as the backbone into the cloud twin.
- **Edge-vs-cloud:** compute **vibration features at the edge** (RMS + FFT bands) — streaming raw 10 kHz to the cloud is bandwidth waste; send the features. Temperature/load stream raw (cheap). The degradation model runs in the **cloud**.
- **Sync-latency budget:** minutes — spindle-health is a maintenance decision, not a control loop; streaming features at a minute cadence suffices.
- **Binding:** each feature → a DTDL property on the spindle twin; raw history also lands in `data-platform` for retraining.
- **Drift policy:** monitor predicted-vs-actual degradation index; tolerance ±10%; recalibrate the ROM parameters on a rolling window when it drifts (root-cause first: sensor vs model vs real wear).

## Guardrails

- Design from the model's properties backward to signals — don't ingest a signal the twin doesn't consume.
- Sample to the **decision**: over-sampling is cost, under-sampling is blindness; justify every rate.
- Pre-aggregate at the edge where bandwidth/latency/connectivity demand it — don't stream raw high-rate data to the cloud by reflex.
- Bind signals to **model properties** (DTDL / AAS), not to a bare database — a data lake of readings is not a twin.
- The sync-latency budget follows the decision's timescale, not "as fast as possible."
- Every twin gets a drift-detection + recalibration policy at design time — an un-monitored twin drifts silently.
- Firmware / sensor drivers / edge gateways themselves are `embedded-iot-engineering`; the warehouse the raw history lands in is `data-platform`. See [`../../knowledge/digital-twin-patterns-2026.md`](../../knowledge/digital-twin-patterns-2026.md).
