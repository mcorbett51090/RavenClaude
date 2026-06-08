---
description: "Design and implement the device-to-cloud connectivity stack (MQTT/CoAP over TLS, device provisioning, certificate storage) and the OTA firmware update pipeline (A/B partition swap, signature verification, watchdog-guarded first-boot validation, rollback) for constrained IoT devices."
---

# IoT Connectivity and OTA Update Design

**Purpose:** produce a complete, device-side connectivity and OTA design — from credential
storage and MQTT connection lifecycle through to the OTA state machine with a tested rollback
path and secure boot chain.

---

## Entry point

1. **Connectivity requirements inventory.** Protocol (MQTT vs CoAP), transport security (TLS),
   cloud target (AWS IoT Core / Azure IoT Hub / custom broker), message frequency, payload size,
   and link type (cellular / Wi-Fi / BLE mesh / LoRa).
2. **Traverse the OTA strategy tree** in
   [`../../knowledge/embedded-iot-firmware-decision-trees.md`](../../knowledge/embedded-iot-firmware-decision-trees.md)
   to select A/B vs delta vs incremental. Land on a leaf before proceeding.
3. **Flash budget check.** Confirm the MCU flash supports A + B + factory + NVS partition slots.
   If not, escalate to `embedded-architect` before continuing.

---

## MQTT connection lifecycle design

### TLS stack selection for constrained MCUs

| Stack | Flash footprint | RAM | Notes |
|---|---|---|---|
| mbedTLS (Mbed-TLS 3.x) | ~60–100 KB | ~20–40 KB | Standard on STM32/ESP-IDF; configurable to trim size |
| wolfSSL | ~20–80 KB (config-dependent) | ~10–30 KB | Smaller footprint, FIPS cert available |
| ATECC608 offload | Tiny (driver only) | Minimal | Hardware crypto chip handles TLS key ops; key never exposed |

Configure only the cipher suites you need (`MBEDTLS_KEY_EXCHANGE_ECDHE_RSA`, etc.) to save flash.

### Connection state machine

```
DISCONNECTED → CONNECTING → CONNECTED → SUBSCRIBING → READY
     ↑                                                  |
     └─────── back-off timer (exponential + jitter) ←──┘
                  on any disconnect / error
```

Back-off formula: `delay = min(cap, base * 2^attempt) + rand(0, base * 2^attempt)`

Recommended: base = 1 s, cap = 300 s. This prevents reconnect storms in a fleet.

### Keep-alive and session

- Set MQTT keep-alive to the maximum the broker allows (typically 60–3600 s).
- Use a persistent session (clean=0) on brokers that support QoS 1 subscription persistence.
- Publish device availability with a Last-Will-and-Testament message (LWT) so the cloud detects
  an ungraceful disconnect.

---

## Device provisioning design

### Certificate provisioning at manufacturing

1. At factory: generate a unique key pair per device (ideally on a secure element — key never
   leaves the device).
2. Inject the device certificate (signed by the product CA) and the CA trust anchor.
3. Store in flash-encrypted partition (ESP32 NVS encrypted, STM32 RDP-protected flash,
   nRF `trusted_storage`).

### Zero-touch provisioning options

| Mechanism | Cloud | Device requirement |
|---|---|---|
| AWS IoT Fleet Provisioning (claim certs) | AWS IoT Core | Claim cert embedded at manufacturing |
| AWS JITR/JITP | AWS IoT Core | CA cert registered with AWS |
| Azure DPS (X.509 attestation) | Azure IoT Hub | Device cert with DPS enrollment group |
| Azure DPS (TPM attestation) | Azure IoT Hub | TPM 2.0 chip on device |

---

## OTA update state machine

### Partition layout (A/B scheme)

```
┌─────────────────┬─────────────────┬─────────┬─────────────────┐
│  Bootloader     │  Slot 0 (active)│  NVS    │  Slot 1 (update)│
│  (MCUboot etc.) │  Firmware A     │  Config │  Firmware B      │
└─────────────────┴─────────────────┴─────────┴─────────────────┘
```

Both Slot 0 and Slot 1 must fit the maximum firmware image size.

### OTA state machine

```
IDLE → CHECKING_MANIFEST → DOWNLOADING → VERIFYING → SWAPPING → PENDING_REBOOT
                                              ↓ (fail)
                                          DOWNLOAD_FAILED → IDLE (retry after back-off)

PENDING_REBOOT → (watchdog-guarded first boot) → VALIDATING
    ↓ success                                          ↓ fail (3 attempts)
  CONFIRMED                                        ROLLING_BACK → IDLE
```

### Mandatory validation steps

1. **Manifest check:** version > current, SHA-256 hash of expected binary matches manifest.
2. **Signature verification:** verify Ed25519 or RSA-PSS signature on the image binary before
   writing to the inactive partition.
3. **Write integrity:** after writing, re-read the slot and verify the SHA-256.
4. **Watchdog-guarded first boot:** set a boot counter in NVS. On first boot of new image,
   increment counter. If counter ≥ 3 without a confirmed-good write, roll back.
5. **Application-level confirmation:** the application must call `ota_confirm()` after all
   startup self-tests pass; absent confirmation → rollback on next reboot.

---

## Secure boot chain (MCUboot-centric)

1. **Root of trust:** device-fused hardware key (OTP / eFuse) or dedicated secure element.
2. **Bootloader verification:** ROM verifies MCUboot signature using the fused key.
3. **Firmware verification:** MCUboot verifies the active slot's signature using the embedded
   public key before jump.
4. **Key hierarchy:** root key (offline, hardware-secured) → signing key (CI-accessible,
   rotatable). Escalate key lifecycle decisions to `security-engineering`.

---

## Fleet telemetry schema design

- Topic pattern: `devices/{device_id}/telemetry` (publish) / `devices/{device_id}/commands` (subscribe).
- Payload: prefer CBOR or MessagePack over JSON on bandwidth-constrained links (≥30% smaller).
- Include `device_id`, `firmware_version`, `timestamp_utc`, and `uptime_s` in every telemetry
  message for fleet-wide traceability.
- Device shadow / digital twin: sync reported state at startup + on change; use desired state
  for configuration push.

---

## Anti-patterns

- OTA with no image signature verification before writing to flash.
- OTA with no rollback and no watchdog boot counter.
- Hard-coded private key or certificate in source code.
- MQTT reconnect with no back-off (instant retry → broker flood).
- TLS certificate verification disabled in production.
- Fleet provisioning with a single shared private key across all devices.
- Telemetry published at maximum frequency without batching — drains battery and bandwidth.

---

## Output

An **OTA partition layout** (addresses + sizes) + an **OTA state machine diagram** + a
**provisioning flow** + the **TLS stack selection with flash-cost estimate**. Reference
[`../../templates/ota-rollback-plan.md`](../../templates/ota-rollback-plan.md) for the rollback
plan template. Escalate cloud-side routing to `aws-cloud` / `azure-cloud`; escalate crypto policy
to `security-engineering`.
