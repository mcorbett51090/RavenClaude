# Embedded & IoT Engineering — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the silicon vendor / RTOS / stack docs before quoting. Last reviewed: 2026-06-08._

Traverse before choosing a scheduling model, a radio, or a provisioning posture.

## Decision Tree: RTOS or bare-metal?

An RTOS is a cost you take on for genuine concurrency — not a default.

```mermaid
graph TD
  A[New firmware design] --> B{Multiple independent tasks with separate timing requirements?}
  B -- No, one main flow + interrupts --> C[Bare-metal super-loop + ISRs - smaller, deterministic, easiest to debug]
  B -- Yes --> D{Can a super-loop with a simple scheduler / state machine still meet the deadlines?}
  D -- Yes --> E[Bare-metal cooperative scheduler - avoid RTOS overhead and stack-per-task RAM cost]
  D -- No --> F{Hard real-time deadlines that need pre-emptive priority?}
  F -- Yes --> G[Pre-emptive RTOS - FreeRTOS / Zephyr / Embassy; budget per-task stacks + the scheduler RAM/flash]
  F -- No, just convenience --> H{Is the RAM budget comfortable for per-task stacks?}
  H -- No --> I[Stay bare-metal - per-task stacks will blow a tight RAM budget]
  H -- Yes --> J[RTOS acceptable - but document the cost you took on]
```

_A super-loop with interrupts is often the right, debuggable, smaller answer. Reach for an RTOS when concurrent, independently-timed work genuinely needs pre-emption — and account for the per-task stack RAM._

## Decision Tree: Which connectivity protocol / radio?

The power/range/bandwidth budget picks the radio, not familiarity.

```mermaid
graph TD
  A[Connect the device] --> B{Mains-powered or generous battery, and need real bandwidth?}
  B -- Yes --> C[Wi-Fi - MQTT-over-TLS / HTTPS; highest power draw, highest bandwidth]
  B -- No, battery-constrained --> D{Range needed?}
  D -- Short-range to a phone/gateway --> E[BLE - GATT; pairing + provisioning to a companion app]
  D -- Long-range, low data --> F{How much data, how often?}
  F -- Tiny payloads, infrequent, km-scale --> G[LoRa / LoRaWAN - long range, very low power, low bandwidth, duty-cycle limited]
  F -- Modest data, local area --> H{Mesh topology needed?}
  H -- Yes --> I[Zigbee / Thread - low-power mesh; Thread is IPv6/6LoWPAN]
  H -- No --> J[BLE or a sub-GHz proprietary link - match to range + duty cycle]
  C --> K{Lossy link expected?}
  G --> K
  K -- Yes --> L[MQTT QoS 1 / store-and-forward, or CoAP-over-DTLS with retries - tolerate dropped connectivity]
```

_BLE for short-range low-power, LoRa for long-range low-bandwidth, Wi-Fi for bandwidth at mains power, Zigbee/Thread for low-power mesh. Then pick a protocol that tolerates a dropped link, and duty-cycle the radio — it is the battery budget._

---

## Capability map (2026, `[verify-at-build]`)

| Layer | Options | Notes |
|---|---|---|
| RTOS | FreeRTOS, Zephyr, Embassy (Rust async), bare-metal super-loop | Zephyr for a batteries-included HAL + connectivity; FreeRTOS for minimal footprint; Embassy for async Rust `[verify-at-build]` |
| MCU / SoC family | ARM Cortex-M (STM32, nRF52/53, RP2040), ESP32 (Wi-Fi/BLE), RISC-V | nRF52/53 for BLE; ESP32 for Wi-Fi+BLE at low cost; STM32 for breadth — pick on flash/RAM/power headroom `[verify-at-build]` |
| Firmware language | C, C++ (subset), Rust (`embedded-hal`, Embassy) | Rust for memory-safety on new builds where the toolchain/ecosystem fits; C for breadth of vendor SDKs `[verify-at-build]` |
| Short-range radio | BLE (5.x), Zigbee, Thread (6LoWPAN) | BLE for phone-paired devices; Thread/Zigbee for low-power mesh `[verify-at-build]` |
| Long-range radio | LoRa / LoRaWAN, NB-IoT / LTE-M (cellular) | LoRaWAN for unlicensed km-scale low-bandwidth; LTE-M/NB-IoT for cellular coverage at higher cost `[verify-at-build]` |
| Device protocol | MQTT (over TLS), CoAP (over DTLS), LoRaWAN, HTTP | MQTT for pub/sub telemetry with QoS; CoAP for REST-like on constrained UDP `[verify-at-build]` |
| Secure boot / root of trust | ARm TrustZone-M, secure elements (ATECC608, SE050), MCU fuses, MCUboot | MCUboot for the verified-boot + A-B image flow; a secure element for key storage `[verify-at-build]` |
| OTA / device management | MCUboot (A-B + rollback), vendor cloud agents, LwM2M | Dual-bank A-B + rollback-on-failed-boot is the baseline; LwM2M for standardized device management `[verify-at-build]` |
| Provisioning / identity | X.509 per-device certs, PSK (discouraged at fleet scale), secure-element-stored keys | Per-device identity provisioned at manufacture/first-boot; never a shared fleet secret `[verify-at-build]` |
| Debug / trace | SWD/JTAG, SEGGER J-Link + RTT, OpenOCD, ITM/SWO trace | SWD + a fault handler writing context to retained RAM; RTT for low-overhead logging `[verify-at-build]` |

_Reference budgets: a coin-cell (CR2032 ~225 mAh) device lives on sleep current (µA) and a low duty cycle; the radio dominates active draw. The DORA-equivalent for firmware is field-update success rate + rollback rate — a fleet you can't safely update is a fleet you can't fix. Re-verify any silicon/RTOS/stack specific against its current docs/errata before quoting it to a consumer._
