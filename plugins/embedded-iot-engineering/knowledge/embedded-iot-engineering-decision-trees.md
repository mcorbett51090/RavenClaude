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

## Decision Tree: Power budget — will the battery last?

Battery life is sleep current × duty cycle. Design sleep first, then check the active path against the budget.

```mermaid
graph TD
  A[Battery device] --> B{Is there a defined sleep state + enumerated wake sources?}
  B -- No --> C[STOP - design sleep modes + wake sources first; an undefined sleep state means an unknown average current]
  B -- Yes --> D{Average current = active_mA × duty + sleep_µA × idle. Computed?}
  D -- No --> E[Compute it - measure or estimate active draw, sleep draw, and the duty cycle; the radio dominates active]
  D -- Yes --> F{battery_mAh / average_mA ≥ target life with margin for self-discharge + temp + OTA?}
  F -- Yes --> G[Budget holds - lock the duty cycle + sleep state as a design constraint]
  F -- No --> H{Is sleep current the dominant term?}
  H -- Yes --> I[Cut sleep leakage - deeper sleep state, power down peripherals, check pull-ups + leakage paths]
  H -- No, active dominates --> J[Cut active energy - lower duty cycle, batch + burst the radio, shorten wake time, slower clock]
```

_A µA of avoidable sleep current dwarfs a wasted mA in a sub-1%-duty active burst. Use the `power-budget` subcommand of `scripts/embedded_calc.py` to turn a duty cycle + battery capacity into a life estimate._

## Decision Tree: OTA + boot flow

Every connected field device needs an update path, designed in from day one — dual-bank with rollback is the baseline.

```mermaid
graph TD
  A[Connected field device] --> B{Is there an OTA path designed in?}
  B -- No --> C[STOP - a device you can't update is a fixed-expiry liability; design OTA before ship, not for v2]
  B -- Yes --> D{Enough flash for two full image banks?}
  D -- Yes --> E[Dual-bank A-B - flash inactive bank, verify, swap, boot; instant rollback on failed boot]
  D -- No --> F{Can the bootloader stage an update from external flash / a scratch region?}
  F -- Yes --> G[Single-bank + external-flash staging - slower, riskier swap window; keep the bootloader minimal + verified]
  F -- No --> H[Re-budget flash or pick a larger part - no safe rollback path is not shippable for a connected device]
  E --> I{Does the new image's signature verify against the hardware root of trust?}
  G --> I
  I -- No --> J[Reject + stay on current image - log the rejection]
  I -- Yes --> K[Boot new image; confirm health, then mark bank good - else roll back automatically]
```

_The bootloader is often the one piece you cannot OTA — keep it minimal and verified, and budget the second bank in the flash layout up front._

## Decision Tree: Secure-boot + provisioning posture

Per-device identity anchored in hardware is the floor for a connected device, not a v2 feature.

```mermaid
graph TD
  A[Connected device key + identity] --> B{Does each device have a unique identity, or one shared fleet secret?}
  B -- Shared secret --> C[STOP - one extraction clones the whole fleet and is unrevocable; move to per-device identity]
  B -- Per-device --> D{Where does the private key live?}
  D -- Plaintext flash --> E[Move it - a flash dump yields the key; use a secure element / TrustZone / encrypted flash]
  D -- Secure element / TrustZone / fuses --> F{Is the boot chain verified against a hardware root of trust?}
  F -- No --> G[Add secure boot - each stage authenticates the next; an anchor in mutable flash is theater]
  F -- Yes --> H{Provisioned at manufacture or first boot, with a rotation/revocation story?}
  H -- No --> I[Add provisioning - issue a per-device X.509 cert; mutual TLS/DTLS so compromise + revocation are per-device]
  H -- Yes --> J[Posture holds - route the crypto specifics algorithms / key sizes / rotation to security review]
```

_Route the cryptographic specifics (algorithms, key sizes, rotation, the trust-anchor design) to `ravenclaude-core/security-reviewer` + `security-engineering`. This tree picks the posture; security review signs off the cryptography._

## Decision Tree: Peripheral I/O — polling, interrupt, or DMA?

The cheapest interrupt is the one that doesn't fire per byte. Move the data path off the CPU when it's bursty or streamed.

```mermaid
graph TD
  A[Read/write a peripheral - I2C/SPI/UART/ADC] --> B{Is the transfer on a hard-real-time deadline or in a tight power budget?}
  B -- No, occasional + slack --> C{Short, infrequent, bounded transfer?}
  C -- Yes --> D[Polling - simplest; busy-wait only if the wait is short and you are not sleeping]
  C -- No --> E[Interrupt-driven - flag-and-defer; ISR moves one unit + signals, main context does the work]
  B -- Yes --> F{Streamed or bursty data - many bytes back-to-back?}
  F -- No, single events --> G[Interrupt-driven, prioritised - short ISR sets a flag / pushes to a queue, returns]
  F -- Yes --> H{Can a per-byte/per-word ISR keep up with the worst case, incl. interrupts-off windows?}
  H -- Yes, comfortably --> I[Interrupt-driven ring buffer - ISR drains the FIFO into RAM; parse in main]
  H -- No, or HW FIFO overruns --> J[DMA into a ring buffer - ISR fires on idle-line / half/full-transfer, not per byte; CPU sleeps while DMA fills RAM]
  E --> K{Does any blocking happen in interrupt context?}
  G --> K
  I --> K
  K -- Yes - printf / float / mutex / busy-wait --> L[STOP - move it to the main context; ISRs flag-and-defer only]
  K -- No --> M[OK - now bound the worst case: ISR cost x rate + the longest interrupts-off window must fit the deadline]
```

_DMA + a ring buffer beats a fast ISR for bursty/streamed data: the data lands in RAM without per-byte CPU involvement, so a brief interrupts-off window (a flash write, a critical section) no longer drops bytes. Bound the worst case — ISR cost and the longest interrupts-off window — not just the happy path. Use the `baud` subcommand of `scripts/embedded_calc.py` to check the UART clock-divisor error before blaming the ISR for corruption._

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
