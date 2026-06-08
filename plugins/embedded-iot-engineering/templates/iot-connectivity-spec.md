# IoT Connectivity — Spec

> Output of `iot-connectivity-engineer` / the `iot-connectivity-and-provisioning` skill. A fleet with a shared
> secret, no secure boot, or `verify=false` is not ready to ship.

## 1. The connectivity budget

- **Power source:** <mains / battery / coin cell>
- **Range needed:** <m / km>
- **Data rate + cadence:** <bytes per send, sends per hour>
- **Topology:** <point-to-point / star / mesh>
- **Fleet size:** <units>

## 2. Radio + protocol choice

| Option | Power/range/bandwidth fit | Chosen? | Why / why not |
|---|---|---|---|
| BLE | | | |
| LoRa / LoRaWAN | | | |
| Wi-Fi | | | |
| Zigbee / Thread | | | |

- **Protocol on top:** <MQTT-over-TLS / CoAP-over-DTLS / LoRaWAN>
- **Dropped-link tolerance:** <QoS / store-and-forward / retries>
- **Radio duty-cycle (power):** <send burst + sleep between>

## 3. Telemetry contract (handed to the cloud-ingest layer)

| Field | Value |
|---|---|
| Topic / resource structure | |
| Payload schema | |
| Cadence | |
| QoS | |

## 4. Provisioning & identity (per-device, never shared)

- **Identity:** <X.509 cert / key in a secure element>
- **Provisioned when:** <manufacture / first boot>
- **Rotation / revocation:** <story>
- **Shared-secret shortcut rejected?** <yes — and why it's unsafe>

## 5. Secure boot & key storage

| Concern | Design |
|---|---|
| Root of trust | <secure element / TrustZone / fuses — hardware, not flash> |
| Boot chain verification | <each stage verifies the next> |
| Key storage | <secure storage, never plaintext flash> |
| Routed to security review? | <yes — crypto specifics> |

## 6. Fleet management

- **OTA transport:** <partition/boot shape → firmware-architect>
- **Device registry + lifecycle:** <onboard / suspend / decommission / revoke>

## 7. Build handoff

| What | Routed to |
|---|---|
| OTA partition / boot-chain shape | `firmware-architect` |
| Radio / peripheral driver | `embedded-engineer` |
| Key / trust-anchor posture | `security-engineering` / `security-reviewer` |
| Telemetry ingest pipeline | `data-streaming-engineering` / the cloud plugins |
| Companion app (pair/provision over BLE/Wi-Fi) | `mobile-engineering` |

---

```
Status: ...
Files changed: ...
Resource budget impact: ...
Safety & security posture: ...
Handoff to cloud/app teams: ...
Open questions: ...
Grounding checks performed: ...
```
