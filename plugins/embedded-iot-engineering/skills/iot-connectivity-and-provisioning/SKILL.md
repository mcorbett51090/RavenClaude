---
name: iot-connectivity-and-provisioning
description: "Connect a device fleet and keep it trustworthy: choose the radio (BLE/LoRa/Zigbee/Thread/Wi-Fi) by the power/range/bandwidth budget, design the protocol (MQTT/CoAP) + telemetry contract, model per-device provisioning & identity (never a shared secret), and design secure boot + key storage against a hardware root of trust."
---

# IoT Connectivity and Provisioning

## The budget picks the radio
BLE for short-range low-power (phone-paired), LoRa/LoRaWAN for long-range low-bandwidth (km scale), Wi-Fi for real bandwidth at mains power, Zigbee/Thread for low-power mesh. State the power/range/bandwidth/topology budget and let it decide; name the rejected options. The radio dominates the battery budget — duty-cycle it (send in bursts, sleep between).

## Protocol + telemetry contract
MQTT-over-TLS for pub/sub telemetry with QoS, CoAP-over-DTLS for REST-like on constrained UDP, LoRaWAN for the long-range link. Define the topic/resource structure, payload schema, cadence, and QoS as an explicit contract — and pick a protocol that tolerates a dropped link (QoS / store-and-forward / retries). Hand the contract to `data-streaming-engineering`; don't build the pipeline here.

## Per-device provisioning & identity
Each device gets a unique identity (X.509 cert / key in a secure element), provisioned at manufacture or first boot, with rotation/revocation. Never a shared fleet secret — one extraction compromises every device. Never a hardcoded TLS/PSK key or `verify=false`; use mutual TLS/DTLS or a named, reviewed exception.

## Secure boot & key storage
The root of trust lives in hardware (secure element / TrustZone / fuses); the boot chain verifies each stage; keys never sit in plaintext flash. Secure boot anchored only in mutable flash is theater. Route the cryptographic specifics to security review.

## Fleet management
The OTA partition/boot shape comes from `firmware-architect`; here, design the update transport, the device registry, lifecycle (onboard / suspend / decommission), and revocation.

## Output
A connectivity spec: the radio + protocol chosen by the budget (and the rejected options), the telemetry contract, the provisioning/identity model, the secure-boot/key-storage design, and the cloud-ingest handoff. Route the OTA partition shape to `firmware-architect`, the radio driver to `embedded-engineer`, the key/trust posture to `security-reviewer`.
