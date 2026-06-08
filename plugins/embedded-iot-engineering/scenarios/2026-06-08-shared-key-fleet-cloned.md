---
scenario_id: 2026-06-08-shared-key-fleet-cloned
contributed_at: 2026-06-08
plugin: embedded-iot-engineering
product: esp32
product_version: "unknown"
scope: likely-general
tags: [provisioning, identity, secure-boot, keys, tls, mqtt]
confidence: high
reviewed: false
---

## Problem

An ESP32-based consumer device connected to a cloud MQTT broker using a single TLS client certificate and private key baked into the firmware image — the same key on every unit. A researcher dumped the flash off one device (no flash encryption, no secure boot), extracted the key, and could impersonate any device in the fleet and publish forged telemetry. Because the key was shared, there was no way to revoke one device without breaking all of them.

## Constraints context

- ~50k devices already in the field on the shared key.
- The firmware was a single image flashed identically at manufacture; no per-device provisioning step existed.
- Flash encryption and secure boot were available on the SoC but had not been enabled.

## Attempts

- Tried: rotating the shared key via OTA. This only moved the problem — the new key was still shared, still extractable, and now there were two compromised keys.
- Tried: obfuscating the key in the binary. Useless against a flash dump; security by obscurity bought nothing.
- Tried: per-device identity — provision a unique key/cert per device into the SoC's secure storage at first boot (talking to a provisioning service that issued a per-device cert), enable flash encryption + secure boot so the key couldn't be read off or the image swapped, and switch the broker to require mutual TLS with per-device certs so a single extracted key only ever compromised one device and could be revoked individually. This was the durable fix.

## Resolution

New units shipped with per-device identity in encrypted secure storage and a verified boot chain; the broker enforced mutual TLS and per-device revocation. Fielded units were migrated over OTA to a per-device cert where the hardware allowed (and flagged for replacement where flash encryption couldn't be retrofitted safely). A cloned device could now be revoked on its own without touching the rest of the fleet, and a flash dump no longer yielded a usable key.

## Lesson

Per-device identity is the floor, never a shared fleet secret — one extraction of a shared key compromises every device and is unrevocable. Anchor the key in hardware-backed secure storage with flash encryption + secure boot so it can't be read off or the image swapped, and use mutual TLS with per-device certs so compromise and revocation are per-device. `verify=false` or a baked-in shared key is a cloned fleet waiting to happen.
