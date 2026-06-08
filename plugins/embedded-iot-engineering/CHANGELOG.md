# Changelog — embedded-iot-engineering

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth build-out to the v0.2.0 standard — no new agents (team-growth-as-knowledge), deeper knowledge,
runtime, and scenario surface on the same 3-agent / 3-skill roster.

- **Best-practices → 12** — added `power-is-spent-mostly-in-sleep`, `watchdog-is-the-last-line-not-the-plan`,
  `debuggability-is-designed-in`, `the-cloud-is-the-layer-above` to the original 8; `best-practices/README.md`
  index reconciled to all 12.
- **Knowledge bank → 5 Mermaid decision trees** — added the **Peripheral I/O — polling, interrupt, or DMA?**
  tree (the flag-and-defer / DMA-ring-buffer call) alongside RTOS-vs-bare-metal, connectivity-protocol,
  power-budget, OTA/boot, and secure-boot/provisioning. The dated 2026 capability map (`[verify-at-build]`)
  is retained.
- **Runnable calculator** `scripts/embedded_calc.py` (stdlib only, Python 3.9+; `ruff`-clean over F/E9/B/C4/I/UP,
  `py_compile`-clean, executable) — three subcommands: `power-budget` (active/sleep duty cycle → average
  current → battery life from mAh, with the sleep-vs-active share), `baud` (UART clock divisor + percent error
  vs the ~2% per-frame tolerance), `airtime` (LoRa time-on-air + duty-cycle headroom: messages/hour + min TX
  gap under a regulatory cap). Decision-support, not a measurement — battery life is only as honest as the
  *measured* sleep current, and the LoRa model is `[verify-at-build]` against the modem/regional plan.
- **Scenarios bank → 5 dated field notes** — added `2026-06-08-ota-bricked-half-the-fleet` (single-bank OTA
  bricks a fleet → dual-bank A-B + rollback) and `2026-06-08-lora-duty-cycle-throttled` (duty-cycle cap, not
  range, sets the real cadence) to the existing coin-cell / ISR-overrun / shared-key notes; `scenarios/README.md`
  index reconciled to all 5 (9-field schema, `reviewed: false`).
- **Metadata** — `plugin.json` 0.1.0 → 0.2.0; description updated to 12 best-practices, 5 trees, and the calculator.

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
