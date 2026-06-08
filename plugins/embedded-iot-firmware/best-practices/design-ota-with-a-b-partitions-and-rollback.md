# Design OTA with A/B partitions and rollback

**Status:** Absolute rule
**Domain:** Embedded firmware — OTA firmware update
**Applies to:** `embedded-iot-firmware`

---

## Why this exists

An OTA update that can fail without a recovery path turns every failed update into a bricked
device. At fleet scale, even a 0.1% failure rate means hundreds of unrecoverable devices. The
only way to guarantee recoverability is to never overwrite the running image: keep the current
firmware in Slot 0 (active), write and verify the new firmware in Slot 1 (passive), and only
swap the boot pointer after verification passes. If the new image fails to boot or fails its
startup self-test, the watchdog-guarded boot counter triggers a revert to Slot 0.

A device that cannot roll back is a device that can be permanently disabled by a bad update —
whether that bad update is a bug, a power failure mid-download, or an image corruption. For
network-connected devices that cannot be physically accessed, an irreversible brick is a product
failure, a support cost, and potentially a safety incident.

---

## How to apply

**Do:**

- Allocate flash for A + B partition slots at architecture time, before any code is written.
  (Retrofitting A/B OTA into an existing flash layout is a breaking change.)
- Use MCUboot or the platform-native bootloader (ESP-IDF, nRF Connect SDK) in A/B mode.
- Implement the OTA state machine with explicit states: DOWNLOADING, VERIFYING, SWAPPING,
  PENDING_REBOOT, VALIDATING, CONFIRMED, ROLLING_BACK.
- Set a watchdog timeout during the validation window (default: 30 s after reboot into new image).
- Use an NVS-stored boot counter. Increment before each boot of a PENDING image. Threshold ≥ 3
  failed boots → automatic rollback.
- Require the application to call an explicit `ota_confirm()` after all startup self-tests pass.
  Absent confirmation → rollback on next power cycle.
- Verify the image signature (Ed25519 or RSA-PSS) before writing to Slot 1, and verify the
  SHA-256 of Slot 1 after writing and before swapping.

**Don't:**

```
DON'T overwrite the running image in place (no A/B — any interruption bricks the device)
DON'T swap without verifying the image signature
DON'T disable the watchdog during the OTA validation window
DON'T mark an update "successful" before the application has confirmed it
DON'T ship a delta-only OTA scheme with no full-image fallback path
```

---

## Edge cases / when the rule does NOT apply

- **Devices with no network connectivity** (air-gapped, JTAG-only update): the rollback concern
  is reduced because updates are supervised and the device is physically accessible. A/B is still
  recommended, but a supervised single-slot update with a known-good backup on a programmer is
  an acceptable substitute if flash budget is the hard constraint.
- **MCUs with ≤ 256 KB flash where A/B cannot physically fit:** the constraint is real. In this
  case: (a) use a supervised update (device in a dock/jig), (b) use incremental OTA on a
  carefully partitioned image, or (c) upgrade to a larger flash MCU. Document the risk
  explicitly; this is not a "the rule doesn't apply" situation — it's a "we accept this risk
  because the alternative is infeasible" situation.

---

## See also

- [`./secure-boot-and-signed-firmware-images.md`](./secure-boot-and-signed-firmware-images.md)
- [`./watchdog-and-fail-safe-defaults.md`](./watchdog-and-fail-safe-defaults.md)
- `iot-connectivity-engineer` agent — OTA state machine and rollback design.
- `/embedded-iot-firmware:plan-ota-update` command — guided OTA design workflow.
- [`../templates/ota-rollback-plan.md`](../templates/ota-rollback-plan.md) — the rollback plan template.

## Provenance

Reflects the design of MCUboot (the canonical open-source embedded bootloader), ESP-IDF OTA
documentation, AWS IoT OTA best practices, and the Nordic FOTA design guide. The A/B + watchdog
+ boot-counter + explicit-confirm pattern is the industry consensus for recoverable OTA.

---

_Last reviewed: 2026-06-08 by `claude`._
