# OTA Rollback Plan

> **How to use this template:** fill in every `[PLACEHOLDER]` before this document is used
> as a design reference or reviewed for production readiness. Delete this instruction block.
> Produced by `iot-connectivity-engineer` via `/plan-ota-update`.

---

## Project

**Project name:** [PROJECT_NAME]
**MCU / SoC:** [MCU_FAMILY]
**OTA transport:** [MQTT / HTTPS / BLE / other]
**Cloud target:** [AWS IoT Core / Azure IoT Hub / custom broker]
**Date:** [YYYY-MM-DD]
**Author:** [NAME OR ROLE]
**Status:** Draft / Review / Approved

---

## 1. Flash partition layout

| Slot | Start address | Size (bytes) | Contents | Notes |
|---|---|---|---|---|
| Bootloader | `[0x08000000]` | `[16 KB]` | MCUboot / platform bootloader | Signed; read-protected |
| Slot 0 (active) | `[0x08004000]` | `[256 KB]` | Running firmware image | Verified at boot |
| Slot 1 (update) | `[0x08044000]` | `[256 KB]` | Incoming OTA image | Verified before swap |
| NVS / config | `[0x08084000]` | `[32 KB]` | Boot counter, OTA state, device config | Flash-encrypted |
| Factory image (opt.) | `[0x0808C000]` | `[128 KB]` | Fallback factory firmware | Read-only after production |

**Max firmware image size:** `[SIZE_IN_BYTES]` bytes.
**OTA strategy selected:** `[A/B full-image / delta / incremental]` — rationale: `[REASON]`.

---

## 2. OTA state machine

```
States:
  IDLE
  CHECKING_MANIFEST
  DOWNLOADING
  VERIFYING
  SWAPPING
  PENDING_REBOOT
  VALIDATING
  CONFIRMED
  ROLLING_BACK
  DOWNLOAD_FAILED
  VERIFICATION_FAILED

Transitions:
  IDLE               → CHECKING_MANIFEST  (trigger: scheduled check or server push)
  CHECKING_MANIFEST  → DOWNLOADING        (new version available, hash/sig verified on manifest)
  CHECKING_MANIFEST  → IDLE               (no update available)
  DOWNLOADING        → VERIFYING          (download complete, byte count matches manifest)
  DOWNLOADING        → DOWNLOAD_FAILED    (network error, timeout, or wrong byte count)
  DOWNLOAD_FAILED    → IDLE               (retry after back-off: [BACK_OFF_POLICY])
  VERIFYING          → SWAPPING           (SHA-256 and image signature valid)
  VERIFYING          → VERIFICATION_FAILED (hash or signature mismatch — discard slot)
  VERIFICATION_FAILED→ IDLE               (log event, alert fleet management)
  SWAPPING           → PENDING_REBOOT     (boot pointer set to Slot 1; NVS state = PENDING)
  PENDING_REBOOT     → VALIDATING         (device reboots into new image)
  VALIDATING         → CONFIRMED          (application calls ota_confirm() within [TIMEOUT_S] s)
  VALIDATING         → ROLLING_BACK       (watchdog fires OR boot counter ≥ [MAX_BOOT_ATTEMPTS=3])
  ROLLING_BACK       → IDLE               (boot pointer reverted to Slot 0; NVS state = ROLLED_BACK)
  CONFIRMED          → IDLE               (NVS state = CONFIRMED; Slot 1 is now the new active)
```

---

## 3. Image verification steps

| Step | Algorithm | Timing | Implementation |
|---|---|---|---|
| Manifest hash check | SHA-256 of manifest JSON | Before download starts | Verify manifest sig matches CA |
| Download integrity | SHA-256 of received image | After download complete | Compare to manifest `sha256` field |
| Image signature | [Ed25519 / RSA-PSS-2048] | After download integrity pass | MCUboot / custom verifier |
| Post-write read-back | SHA-256 of Slot 1 after write | Before SWAPPING state | Extra defence against flash write errors |

**Public key storage:** `[e.g. embedded in bootloader at 0x08000200, read-only section]`
**Signing key location:** `[e.g. CI/CD HSM — escalated to security-engineering]`

---

## 4. Watchdog and boot counter

| Parameter | Value | Notes |
|---|---|---|
| Watchdog timeout during validation window | `[30 s]` | Application must kick watchdog during startup |
| Boot counter NVS key | `[ota_boot_cnt]` | Incremented before each boot of a PENDING image |
| Rollback threshold | `[3]` failed boots | On third failure: revert to Slot 0 |
| `ota_confirm()` call deadline | `[within 30 s of boot]` | Application calls after all self-tests pass |
| Watchdog in production | **Always enabled** | Never disabled in production code |

**Rollback test procedure:**
1. Deploy a known-bad image (one that loops without calling `ota_confirm()`).
2. Confirm device boots, watchdog fires [N] times, boot counter reaches threshold.
3. Confirm device automatically boots back into the previous confirmed image.
4. Confirm rollback event is reported to the fleet management system.

---

## 5. Fleet manifest schema

```json
{
  "version": "1.2.3",
  "sha256": "<hex string, 64 chars>",
  "signature": "<base64 Ed25519 signature>",
  "size_bytes": 262144,
  "target_hardware": "[HARDWARE_ID, e.g. hw-rev-b]",
  "rollout_percentage": 10,
  "min_firmware_version": "1.0.0",
  "release_notes_url": "https://[HOST]/releases/1.2.3"
}
```

**Manifest delivery mechanism:** `[e.g. AWS IoT Jobs / Azure IoT Hub direct method / MQTT retained topic]`

---

## 6. Rollback procedure (manual / emergency)

1. **Remote rollback via fleet command:** send a `{"command": "ota_rollback"}` command to the
   device's command topic. Device calls `ota_abort_and_rollback()` and reboots to Slot 0.
2. **Local rollback via bootloader:** hold `[BUTTON_PIN]` during power-on for 5 seconds to
   force the bootloader to boot Slot 0 regardless of NVS state.
3. **Last resort (unrecoverable device):** `[JTAG/UART bootloader recovery procedure — link to
   service manual section X.Y]`

---

## 7. OTA security checklist

| Item | Status | Notes |
|---|---|---|
| Firmware image is signed before release | [ ] Yes / [ ] No | Ed25519 / RSA-PSS |
| Signing key is offline / HSM-protected | [ ] Yes / [ ] No | Escalated to security-engineering |
| Device verifies image signature before swap | [ ] Yes / [ ] No | MCUboot config |
| TLS certificate is verified on OTA download channel | [ ] Yes / [ ] No | No `insecure` flag in prod |
| Private key is stored in encrypted flash / secure element | [ ] Yes / [ ] No | |
| No hard-coded secrets in firmware source | [ ] Yes / [ ] No | Check with hook |
| Rollback tested in QA before production release | [ ] Yes / [ ] No | See §4 test procedure |

---

## 8. Open questions / risks

| # | Question | Owner | Status |
|---|---|---|---|
| 1 | [e.g. Signing key rotation procedure if key is compromised?] | security-engineering | Open |
| 2 | [e.g. What is the delta-OTA fallback policy if diff fails?] | [NAME] | Open |
| 3 | | | |

---

_Last updated: [YYYY-MM-DD] by [AUTHOR]._
