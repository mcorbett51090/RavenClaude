---
description: "Choose the radio/protocol by the power/range/bandwidth budget and design per-device provisioning, secure boot + key storage, and the telemetry contract."
argument-hint: "[device + power source + range + data rate/cadence + fleet size]"
---

You are running `/embedded-iot-engineering:design-connectivity`. Use `iot-connectivity-engineer` + the `iot-connectivity-and-provisioning` skill.

## Steps
1. State the power/range/bandwidth/topology budget; choose the radio (BLE/LoRa/Zigbee/Thread/Wi-Fi) against it and name the rejected options and why.
2. Pick the protocol (MQTT/CoAP/LoRaWAN) and confirm it tolerates a dropped link (QoS / store-and-forward / retries); duty-cycle the radio for the power budget.
3. Define the telemetry contract: topic/resource structure, payload schema, cadence, QoS — for handoff to the cloud-ingest layer.
4. Design per-device provisioning & identity (X.509 cert / key in a secure element, manufacture vs first-boot flow, rotation/revocation); reject any shared-fleet-secret or `verify=false` shortcut.
5. Design secure boot + key storage against a hardware root of trust; route the cryptographic specifics to security review.
6. Route the rest: OTA partition/boot shape → firmware-architect; radio driver → embedded-engineer; telemetry ingest → data-streaming-engineering; companion app → mobile-engineering.
7. Emit the IoT-connectivity spec + the Structured Output block (with `Resource budget impact:` and `Handoff to cloud/app teams:`).
