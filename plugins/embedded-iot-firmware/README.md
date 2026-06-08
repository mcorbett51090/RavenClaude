# embedded-iot-firmware

The embedded systems and IoT firmware specialist team. This plugin helps you design firmware
architecture, write deterministic peripheral drivers, structure RTOS tasks safely, and connect
devices to the cloud with secure OTA updates — across Embedded C/C++/Rust, FreeRTOS/Zephyr,
STM32/ESP32/nRF MCUs, and MQTT/CoAP transport.

> **The one-line philosophy:** firmware runs on constrained, often safety-adjacent hardware with
> no second chances — determinism, minimal ISRs, static allocation in hot paths, and a tested
> rollback path for every OTA update are non-negotiable from day one.

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Bare-metal vs RTOS? Which MCU? How do I structure the firmware?" | **embedded-iot-firmware** (`embedded-architect`) |
| "Write/debug an SPI/I2C/UART driver, DMA transfer, or ISR" | **embedded-iot-firmware** (`firmware-engineer`) |
| "RTOS task design, priority assignment, stack sizing, priority inversion" | **embedded-iot-firmware** (`rtos-engineer`) |
| "MQTT/CoAP, device provisioning, OTA update, secure boot, fleet telemetry" | **embedded-iot-firmware** (`iot-connectivity-engineer`) |
| "Crypto policy, key lifecycle, HSM decisions for secure boot" | `security-engineering` |
| "AWS IoT Core topic routing, device shadow, rules engine" | `aws-cloud` |
| "Azure IoT Hub device twin, DPS provisioning, message routing" | `azure-cloud` |
| "Telemetry ingestion pipeline, stream processing, time-series storage" | `data-streaming-engineering` |
| "CI pipeline for firmware build and flash" | `devops-cicd` |

## What's inside

- **4 agents** — `embedded-architect`, `firmware-engineer`, `rtos-engineer`,
  `iot-connectivity-engineer`.
- **3 skills** — `bare-metal-and-rtos`, `low-power-and-peripherals`, `iot-connectivity-and-ota`.
- **3 commands** — `/embedded-iot-firmware:design-firmware-architecture`,
  `:plan-ota-update`, `:optimize-power-budget`.
- **2 templates** — `hal-layering-spec`, `ota-rollback-plan`.
- **Knowledge bank** — `knowledge/embedded-iot-firmware-decision-trees.md`: Mermaid trees for
  bare-metal vs RTOS, OTA strategy, and power-mode selection, plus a dated 2026 capability map
  of the ecosystem.
- **6 best-practice rules** and **1 advisory hook** (flags ISR blocking, heap in hot path,
  missing OTA rollback, hardcoded credentials).

## House opinions (the short list)

1. Never block in an ISR — set a flag, post a message, get out.
2. No `malloc`/`new` in hot or safety-critical paths — static pools only.
3. Budget power before you write code, not after.
4. Every OTA scheme ships with A/B partitions, a watchdog-guarded boot counter, and rollback.
5. Signed firmware and secure boot for every network-connected device.
6. Watchdog always on; fail to a known-safe state, not an optimistic retry.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and
seams.
