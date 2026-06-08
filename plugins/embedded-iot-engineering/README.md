# Embedded & IoT Engineering

The **embedded-iot-engineering** plugin — the constrained-device craft: the firmware and IoT/edge layer that runs *on the metal* (microcontrollers, sensors, radios) and *below* the cloud, then emits telemetry up to the data and cloud plugins — distinct from the ingest pipeline, the backend, and the companion app themselves.

## Agents

- **`firmware-architect`** — Firmware shape and operating constraints: RTOS vs bare-metal, MCU selection against memory/power/BOM budgets, HAL/driver layering, boot & OTA-update strategy, and flash partitioning. Treats flash, RAM, clock, power, and cost as first-class design inputs, not afterthoughts.
- **`embedded-engineer`** — Low-level implementation on the metal: C/C++/Rust on MCU, interrupts/ISRs (flag-and-defer), DMA, peripheral drivers (I2C/SPI/UART), real-time constraints, watchdogs, and JTAG/SWD debugging. Writes drivers that fit the budget and bounds the worst case, not just the happy path.
- **`iot-connectivity-engineer`** — Fleet connectivity and trust: device protocols (MQTT/CoAP/BLE/LoRa/Zigbee/Wi-Fi) chosen by the power/range/bandwidth budget, per-device provisioning & identity, fleet management, secure boot & key storage, and telemetry. Per-device identity and a hardware root of trust are the floor, not a v2.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install embedded-iot-engineering@ravenclaude
```

## Seams

- **Ingesting the telemetry stream (the event pipeline, the backend)** → `data-streaming-engineering` + `aws-cloud` / `azure-cloud` / `gcp-cloud`; this team emits the telemetry contract (topics, payload schema, cadence), they ingest it.
- **The mobile companion app** → `mobile-engineering`; we define the on-device BLE/Wi-Fi provisioning + control contract, they build the app against it.
- **The device threat model, key-management policy, and "secure boot done right"** → `security-engineering`; we implement it on the metal, they own the policy.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `data-streaming-engineering`, the cloud plugins, and `mobile-engineering`.
