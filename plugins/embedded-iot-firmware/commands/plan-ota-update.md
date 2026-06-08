---
description: "Design a complete OTA firmware update pipeline — A/B partition layout, download-verify-swap state machine, watchdog-guarded first-boot validation, rollback trigger, image signing, and fleet manifest schema."
argument-hint: "[context, e.g. 'ESP32, 4 MB flash, MQTT over Wi-Fi, AWS IoT Core, current firmware 512 KB, 10k device fleet']"
---

You are running `/embedded-iot-firmware:plan-ota-update`. Use the `iot-connectivity-engineer`
discipline, the `iot-connectivity-and-ota` skill, and the OTA strategy decision tree in
`knowledge/embedded-iot-firmware-decision-trees.md`.

## Steps

1. **Flash budget check.** Confirm the target MCU's flash can accommodate: bootloader + Slot 0
   (active) + Slot 1 (update) + NVS. If it cannot, stop and escalate to `embedded-architect`
   for a flash-layout decision before continuing.

2. **OTA strategy selection.** Traverse the `OTA strategy: A/B vs delta vs incremental` tree in
   `knowledge/embedded-iot-firmware-decision-trees.md`. State the leaf. A/B full-image is the
   baseline; delta may supplement but must not replace the full-image fallback path.

3. **Partition layout.** Produce a partition map with byte addresses, slot names, and sizes:
   - `bootloader` (MCUboot / ESP-IDF bootloader / nRF SPE)
   - `slot_0` (active firmware)
   - `slot_1` (update target / passive slot)
   - `nvs` (OTA state, boot counter, config, provisioning data)
   Note the maximum firmware image size the slot permits.

4. **OTA state machine.** Document each state and transition:
   `IDLE → CHECKING_MANIFEST → DOWNLOADING → VERIFYING → SWAPPING → PENDING_REBOOT →
   VALIDATING → CONFIRMED / ROLLING_BACK`
   For every failure transition: what triggers it, what state it goes to, and how many retries.

5. **Image verification.** Specify:
   - Hash algorithm (SHA-256 over the full image binary)
   - Signature scheme (Ed25519 recommended; RSA-PSS-2048 minimum)
   - Verification timing (before writing to slot, and after writing as a read-back check)
   - Public key storage location in firmware

6. **Watchdog and rollback.** Define:
   - The boot counter NVS key and the rollback threshold (default: 3 failed boots)
   - The watchdog timeout during the validation window
   - How the application confirms a good boot (`ota_confirm()` call site and timing)

7. **Fleet manifest schema.** Define the JSON/CBOR manifest fields:
   `version`, `sha256`, `signature`, `size_bytes`, `target_hardware`, `rollout_percentage`.

8. **Output.** Fill `templates/ota-rollback-plan.md` with the above design. Emit the Structured
   Output block with handoffs to:
   - `aws-cloud` / `azure-cloud` for cloud-side OTA job and manifest distribution
   - `security-engineering` for key management and signing key lifecycle
   - `embedded-architect` if the flash budget requires a partition-layout change
