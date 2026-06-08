# Changelog — embedded-iot-engineering

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The constrained-device / firmware + IoT-edge layer below the existing cloud + app cluster.

- **3 agents** — `firmware-architect` (RTOS vs bare-metal, MCU selection, memory & power budgets, HAL/driver layering,
  boot & OTA strategy, flash partitioning), `embedded-engineer` (C/C++/Rust on MCU, interrupts/ISRs, DMA, I2C/SPI/UART
  peripheral drivers, real-time constraints, watchdogs, JTAG/SWD debugging), `iot-connectivity-engineer` (MQTT/CoAP/BLE/
  LoRa/Zigbee/Wi-Fi, per-device provisioning & identity, fleet management, secure boot & key storage, telemetry). Each
  carries the full scenario-authoring frontmatter.
- **3 skills** — `rtos-vs-bare-metal-architecture`, `embedded-firmware-implementation`, `iot-connectivity-and-provisioning`.
- **Knowledge bank** — `embedded-iot-engineering-decision-trees.md`: Mermaid trees (RTOS-vs-bare-metal, connectivity-
  protocol selection) + a dated 2026 capability map (FreeRTOS / Zephyr / Embassy / BLE / LoRa / MQTT) (`[verify-at-build]`).
- **8 best-practices**, **3 commands** (`design-firmware-architecture`, `implement-driver`, `design-connectivity`),
  **2 templates** (firmware-architecture brief, IoT-connectivity spec), **1 advisory hook**
  (`check-embedded-iot-engineering-anti-patterns.sh`; `EMBEDDED_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: telemetry ingest → `data-streaming-engineering` + the cloud plugins; companion app → `mobile-engineering`;
  device security review → `security-engineering`. Requires `ravenclaude-core@>=0.7.0`.
