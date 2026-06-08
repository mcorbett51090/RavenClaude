---
name: rtos-vs-bare-metal-architecture
description: "Architect constrained-device firmware: decide RTOS vs bare-metal against the concurrency and timing needs, select an MCU against the flash/RAM/power/BOM budget, layer the HAL/drivers, and design the boot chain, OTA strategy, and flash partitions."
---

# RTOS vs Bare-Metal Architecture

## Start from the budget, not the feature list
Flash, RAM, clock, power, and BOM cost are the design. Write the budget down first: static RAM/stack/heap, flash usage, sleep current, active current, duty cycle, battery-life math. Hold headroom for the OTA delta and a field fix. A design with no budget is a prototype.

## RTOS vs bare-metal
A super-loop with interrupts is often smaller, more deterministic, and easier to debug. Reach for an RTOS only when genuinely concurrent, independently-timed work needs pre-emptive scheduling — and account for the per-task stack RAM and scheduler footprint. A cooperative scheduler / state machine is the middle ground. Document the cost when you take on an RTOS.

## MCU selection
Pick the family that fits the budget with headroom (not the one you know): nRF52/53 for BLE, ESP32 for Wi-Fi+BLE at low cost, STM32 for breadth, RISC-V where it fits. A part at 95% flash on day one has no room for the OTA delta. State the margin.

## HAL/driver layering
Application logic talks to a vendor-neutral HAL; the register-level driver is the only code that knows the chip. A BOM change should swap the driver, not rewrite the product.

## Boot chain + OTA + partitions
Design OTA from day one: dual-bank / A-B partitioning + rollback-on-failed-boot so one bad update can't brick the fleet. The boot chain verifies each stage; the root of trust lives in hardware (route the crypto to security review). Lay out partitions: bootloader / app A / app B / config / keys, with sizes.

## Output
A firmware-architecture brief: the RTOS-vs-bare-metal call, MCU selection, the memory & power budgets, HAL/driver layering, the boot/OTA flow, the partition layout, and explicit non-goals. Hand driver implementation to `embedded-engineer`, radio/provisioning to `iot-connectivity-engineer`, telemetry ingest to `data-streaming-engineering`.
