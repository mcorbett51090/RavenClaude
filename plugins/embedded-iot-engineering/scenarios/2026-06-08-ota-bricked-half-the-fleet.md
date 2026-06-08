---
scenario_id: 2026-06-08-ota-bricked-half-the-fleet
contributed_at: 2026-06-08
plugin: embedded-iot-engineering
product: stm32
product_version: "unknown"
scope: likely-general
tags: [ota, bootloader, flash, rollback, mcuboot]
confidence: high
reviewed: false
---

## Problem

A connected HVAC controller on an STM32L4 shipped with a single-bank OTA scheme: the application erased itself and wrote the new image in place, then jumped to it. A routine OTA push went out to ~4k devices. A subset lost power or dropped the link during the in-place write — exactly while the old image was already erased and the new one incomplete — and came up with no valid application and no path back. Half the fleet was field-bricked and needed a truck roll with a JTAG probe to recover.

## Constraints context

- 512 KB flash, but the application image was ~300 KB, so two full banks "didn't fit" under the original layout — that was the excuse for single-bank.
- No verify-before-swap and no rollback: the bootloader jumped to whatever was at the application base, valid or not.
- Power was unreliable in the field (mains, but in buildings with brownouts), and the link was lossy Wi-Fi, so an interrupted write was not an edge case — it was guaranteed at fleet scale.

## Attempts

- Tried: making the OTA "more reliable" — retries, a CRC check after write. This shrank the failure rate but didn't change the failure *mode*: any interruption mid-write still left no valid image and no fallback. A lower probability of a brick is still a brick.
- Tried: a minimal recovery bootloader that could re-download over the link. Better, but it still trusted a single image slot and had no way to roll back a bad-but-valid image that bricked on boot.
- Tried: re-budgeting the flash for dual-bank A-B with MCUboot — shrink the image with `-Os` + dead-code elimination so two banks fit, flash the *inactive* bank, verify its signature against the root of trust, swap, boot, and confirm health before marking the bank good; auto-roll-back on a failed boot. Kept the bootloader itself minimal, verified, and the one piece never OTA'd. This was the fix.

## Resolution

With A-B dual-bank, an interrupted write only ever corrupted the inactive bank — the running image was untouched, so an interruption was a retry, never a brick. A new image that booted but failed its health check rolled back automatically. The next fleet-wide push had zero bricks across the interrupted units. The flash budget that "didn't fit" fit once the image was actually optimized; the single-bank shortcut had been a false economy paid for in truck rolls.

## Lesson

Design OTA from day one as dual-bank A-B with verify-then-swap and automatic rollback — never in-place single-bank on a device you can't physically reach. The failure to plan for is an interrupted write at fleet scale, which is a certainty, not an edge case: the running image must survive it. Budget the second bank in the flash layout up front, keep the bootloader minimal and verified (it's the one piece you can't OTA), and confirm health before marking a bank good.
