# Secure boot and signed firmware images

**Status:** Absolute rule
**Domain:** Embedded firmware — security
**Applies to:** `embedded-iot-firmware`

---

## Why this exists

A network-connected device that accepts unsigned firmware updates has an unauthenticated remote
code execution path. Any attacker who can reach the OTA channel — or intercept the download
traffic — can replace the firmware with malicious code. At IoT scale, a fleet of compromised
devices can be weaponised as a botnet, used for lateral network movement, or turned into a
physical-world attack vector if the device controls actuators.

Secure boot establishes the chain of trust: the hardware verifies the bootloader signature
before executing it; the bootloader verifies the application firmware signature before jumping.
Signed OTA images mean the device verifies the update's provenance before writing it to flash.
Together, they mean that code running on the device was authorized by the key holder — which
should be the firmware team, not anyone who can reach the update endpoint.

This is not a "nice to have" for connected devices. It is the minimum bar for shipping
responsibly.

---

## How to apply

**Do:**

- Enable secure boot at the hardware level (eFuse / OTP trust anchor) before shipping any
  device. On ESP32: `CONFIG_SECURE_BOOT_V2_ENABLED`. On nRF: NSIB/SPE with `CONFIG_TRUSTED_EXECUTION_NONSECURE`. On STM32: RDP level 2 + OPTBOOT with signed image verification.
- Use MCUboot or the platform bootloader in signing mode. Generate a key pair for signing.
  The private signing key must never be embedded in firmware — it lives in a HSM or CI/CD secret
  store.
- Sign every firmware image binary before it is published to the OTA distribution channel.
  Use Ed25519 (compact signature, fast verification) or RSA-PSS-2048 (minimum; RSA-PSS-3072
  preferred for long-lived devices).
- Verify the signature on the device before writing the image to the passive OTA slot. Reject
  any image that fails verification.
- Store device private keys (TLS client cert key) in a flash-encrypted partition, or in a
  secure element (ATECC608, SE050) that never exposes the raw key material.
- Escalate key lifecycle decisions (root CA, signing key rotation, key revocation) to
  `security-engineering`. The firmware team designs the boot chain; the security team owns the
  cryptographic policy.

**Don't:**

```
DON'T ship a device with secure boot disabled ("we'll enable it in production" ships as disabled)
DON'T embed the firmware signing private key in source code or in the firmware image
DON'T disable TLS certificate verification on the OTA download channel in production
DON'T store device private keys (TLS, provisioning) in unencrypted flash
DON'T use a self-signed dev cert in production — use your product CA
DON'T skip image signature verification to save flash space — the verification code is ~2–5 KB
```

---

## Edge cases / when the rule does NOT apply

- **Air-gapped / physically-secured devices with no network update path:** if a device cannot
  accept remote updates and is updated only via JTAG/UART under physical supervision, the remote
  attack surface is absent. Secure boot is still recommended for tamper resistance, but the
  urgency is lower.
- **Development hardware / pre-production units:** disable secure boot only on explicitly
  designated dev hardware. Never disable it on hardware that is in the field or could end up
  there. A clear physical marking distinguishes dev from prod units.

---

## See also

- [`./design-ota-with-a-b-partitions-and-rollback.md`](./design-ota-with-a-b-partitions-and-rollback.md)
- `iot-connectivity-engineer` agent — secure boot chain design and provisioning.
- `security-engineering` plugin — cryptographic policy, key lifecycle, HSM.
- MCUboot documentation (key generation with `imgtool.py`).
- ESP32 Security Guide; nRF TrustZone documentation; STM32 Security Reference Manual.

## Provenance

Reflects OWASP IoT Top 10 (I3: Insecure Ecosystem Interfaces), NIST SP 800-193 (Platform
Firmware Resilience Guidelines), the MCUboot security model, and the security guidance from
Espressif, Nordic, and ST for their respective platforms. The "no embedded private keys" and
"verify before write" principles are consistent across all of these sources.

---

_Last reviewed: 2026-06-08 by `claude`._
