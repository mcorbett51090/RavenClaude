# Firmware Architecture — Brief

> Output of `firmware-architect` / the `rtos-vs-bare-metal-architecture` skill. Fill every section; an empty
> "Resource budget" or "Non-goals" section is a sign the firmware isn't scoped as a product yet.

## 1. The device + the budget (the constraints are the design)

| Constraint | Value | Margin held back |
|---|---|---|
| Flash | <KB> | <% for OTA delta + field fix> |
| RAM | <KB> | <% headroom> |
| Clock | <MHz> | — |
| Power source | <mains / battery / coin cell> | — |
| BOM-cost ceiling | <$> | — |

## 2. RTOS vs bare-metal

- **Decision:** <bare-metal super-loop / cooperative scheduler / pre-emptive RTOS (FreeRTOS·Zephyr·Embassy)>
- **Concurrency/timing rationale:** <why this model>
- **Cost taken on:** <per-task stack RAM + scheduler footprint, or "none — super-loop">

## 3. MCU/SoC selection

| Candidate | Flash/RAM/power fit | Radio/peripheral fit | Chosen? |
|---|---|---|---|
| <e.g. nRF52840> | | | |
| | | | |

## 4. Power budget (mostly sleep)

| Mode | Current | Duty | Notes |
|---|---|---|---|
| Sleep | <µA> | <%> | <wake sources> |
| Active | <mA> | <%> | <radio dominates> |
| **Battery-life estimate** | <months/years on the cell> | | |

## 5. HAL/driver layering

- **Vendor-neutral HAL interface:** <what the app talks to>
- **Register-level driver (chip-specific):** <the only swappable-on-BOM-change layer>

## 6. Boot chain + OTA + flash partitions

| Partition | Size | Purpose |
|---|---|---|
| Bootloader | | minimal, verified, often not OTA-able |
| App A | | |
| App B | | dual-bank for A-B OTA |
| Config | | |
| Keys | | secure storage / route to secure element |

- **Boot chain:** <each stage verifies the next; root of trust in hardware>
- **OTA strategy:** <dual-bank A-B + rollback-on-failed-boot; transport → iot-connectivity-engineer>

## 7. Explicit non-goals

- <e.g. no on-device ML inference in v1>
- <e.g. no second radio>

## 8. Build handoff

| What | Routed to |
|---|---|
| Drivers / ISRs / DMA paths | `embedded-engineer` |
| Radio / protocol / provisioning / secure boot | `iot-connectivity-engineer` |
| Crypto posture of the boot chain / keys | `security-engineering` / `security-reviewer` |
| Telemetry ingest | `data-streaming-engineering` / the cloud plugins |

---

```
Status: ...
Files changed: ...
Resource budget impact: ...
Safety & security posture: ...
Handoff to cloud/app teams: ...
Open questions: ...
Grounding checks performed: ...
```
