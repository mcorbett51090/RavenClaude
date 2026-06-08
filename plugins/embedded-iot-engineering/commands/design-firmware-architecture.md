---
description: "Architect constrained-device firmware: the RTOS-vs-bare-metal call, MCU selection, the memory & power budgets, HAL/driver layering, and the boot/OTA partition layout."
argument-hint: "[device goal + power source + flash/RAM constraints + connectivity]"
---

You are running `/embedded-iot-engineering:design-firmware-architecture`. Use `firmware-architect` + the `rtos-vs-bare-metal-architecture` skill.

## Steps
1. Write the budget first: flash, RAM, clock, power source (mains / battery / coin cell), duty cycle, BOM-cost ceiling. If unknown, state the assumptions.
2. Decide RTOS vs bare-metal from the concurrency/timing needs; name the cost taken on either way.
3. Select an MCU/SoC family that fits the budget with headroom; state the margin held back for the OTA delta + a field fix.
4. Layer the HAL/drivers (vendor-neutral interface vs register-level driver) and lay out the flash partitions (bootloader / app A / app B / config / keys).
5. Design the boot chain + OTA strategy (dual-bank A-B + rollback); route the secure-boot trust anchor + crypto to security review.
6. Route the builds: drivers/ISRs → embedded-engineer; radio/provisioning/secure boot → iot-connectivity-engineer; telemetry ingest → data-streaming-engineering.
7. Emit the firmware-architecture brief + the Structured Output block (with `Resource budget impact:` and `Handoff to cloud/app teams:`).
