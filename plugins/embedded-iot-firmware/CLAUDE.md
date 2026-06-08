# Embedded IoT Firmware Plugin — Team Constitution

> Team constitution for the `embedded-iot-firmware` Claude Code plugin. Bundles **4** specialist
> agents covering the embedded systems and IoT firmware stack: firmware architecture, peripheral
> driver engineering, RTOS design, and device-to-cloud connectivity. Designed for firmware and
> embedded-systems engineers who need rigorous, safety-aware, resource-constrained thinking — not
> a tour of microcontroller basics.
>
> **Orientation:** this file is **domain-specific** to embedded systems and IoT firmware. For the
> domain-neutral team constitution inherited by every plugin, see
> [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer
> guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`embedded-architect`](agents/embedded-architect.md) | Bare-metal vs RTOS decision, MCU/SoC selection, memory/flash budget, HAL layering, overall firmware architecture | "pick an MCU for this design", "should we use an RTOS?", "how do we structure the firmware?", "HAL vs direct register access" |
| [`firmware-engineer`](agents/firmware-engineer.md) | Peripheral drivers, ISRs, DMA, ring buffers, deterministic memory, on-target debugging | "write an SPI driver", "debug a hard fault", "DMA transfer is corrupting memory", "help me size a ring buffer" |
| [`rtos-engineer`](agents/rtos-engineer.md) | Task design, priority assignment, scheduling, synchronization primitives, priority inversion, stack sizing, WCET | "design the task structure", "fix priority inversion", "size these task stacks", "deadlock in FreeRTOS queues" |
| [`iot-connectivity-engineer`](agents/iot-connectivity-engineer.md) | Device-to-cloud (MQTT/CoAP), provisioning, OTA with A/B partitions + rollback, secure boot + signed images, fleet telemetry | "implement MQTT over TLS", "design the OTA update flow", "set up secure boot", "device provisioning at scale" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses
specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.

---

## 2. Routing rules (Team Lead)

- **"We're starting a new firmware project — what MCU / OS?"** → `embedded-architect` (selection +
  architecture); pull in `rtos-engineer` if RTOS is chosen.
- **"This driver is misbehaving / hard fault / DMA corruption"** → `firmware-engineer` (root-cause +
  fix); pull in `rtos-engineer` if the failure is task-context-related.
- **"Priority inversion / missed deadline / stack overflow"** → `rtos-engineer`; pull in
  `firmware-engineer` for any ISR or driver changes required.
- **"OTA update / secure boot / MQTT provisioning"** → `iot-connectivity-engineer`; pull in
  `embedded-architect` if the partition scheme affects flash budget.
- **"Power consumption is too high"** → `embedded-architect` (architecture review) + `firmware-engineer`
  (peripheral clock gating + sleep mode entry/exit); brief `iot-connectivity-engineer` if radio duty
  cycle is the culprit.
- **Any change touching crypto keys, TLS certs, or secret storage** → also route through
  `ravenclaude-core` `security-reviewer`.

---

## 3. Cross-cutting house opinions (every agent enforces)

1. **Never block in an ISR.** ISRs must be minimal: set a flag, post to a queue, clear a register.
   Any processing belongs in a deferred task or main-loop handler. A blocking ISR is a reliability
   bug, not a style concern.
2. **No dynamic allocation in hot or safety-critical paths.** `malloc`/`new`/`free` in an ISR or a
   tight control loop fragments the heap and introduces non-deterministic latency. Pre-allocate
   static pools; size them at link time.
3. **Budget power before you write code.** Establish the power budget (battery capacity, target
   lifetime, max average current) during architecture — not after. Retrofitting sleep modes into
   an existing firmware is expensive and error-prone.
4. **OTA with no rollback plan is a brick factory.** Every OTA scheme ships with an A/B partition
   swap, a watchdog-guarded boot counter, and a known-good fallback. If a device can't be recovered
   remotely, it's bricked — and bricked devices at scale are catastrophic.
5. **Secure boot and signed firmware images are non-negotiable for network-connected devices.**
   An unsigned image means the update channel is an attack surface. Secure boot verifies the chain
   of trust before executing any code.
6. **Watchdog always on; fail-safe defaults.** Every production firmware enables the hardware
   watchdog unconditionally. On any unhandled fault, reset to a known-safe state, not to an
   optimistic retry loop.

---

## 4. Anti-patterns every agent flags

- `malloc`, `new`, or `free` inside an ISR or a path marked hot/safety-critical
- A blocking delay (`delay()`, `sleep()`, busy-wait) inside an ISR
- An OTA implementation with no rollback or A/B partition scheme
- A hard-coded key, secret, certificate, or credential in firmware source
- Disabling the watchdog in production code
- Calling RTOS blocking APIs (`osDelay`, `xQueueReceive` with `portMAX_DELAY`) inside an ISR
- A task with `portMAX_DELAY` on every blocking call and no timeout / error path
- Peripheral clock left running when the peripheral is idle (unnecessary power drain)
- Stack sizes set to "1KB sounds fine" without a measured worst-case analysis
- Mixing HAL abstraction levels — direct register writes next to HAL calls on the same peripheral

---

## 5. Seams (the bridges to neighbouring plugins)

- **Secure boot / crypto policy / key management** → `security-engineering` — this plugin flags the
  requirement and designs the boot chain; that plugin owns the cryptographic policy, key lifecycle,
  and HSM decisions.
- **Device-to-cloud backplane (MQTT broker, IoT Core, IoT Hub)** → `aws-cloud` (AWS IoT Core) or
  `azure-cloud` (Azure IoT Hub) — this plugin owns the device-side protocol stack and provisioning;
  those plugins own the cloud-side topic routing, device shadow/twin, and rule engines.
- **Telemetry stream processing** → `data-streaming-engineering` — this plugin emits the telemetry
  payload; that plugin owns the ingestion pipeline, stream processing, and time-series storage.
- **CI/CD for firmware build + flash** → `devops-cicd` — this plugin defines what the build produces
  (signed binary, OTA package); that plugin owns the pipeline mechanics.
- **Security review of any change touching crypto, secrets, or network** → `ravenclaude-core`
  `security-reviewer`.

---

## 6. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol
(decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured
Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in
each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the
dated capability map.

---

## 7. Knowledge & scenario banks

The knowledge bank backs the agents with high-trust canonical references:

- **[`knowledge/embedded-iot-firmware-decision-trees.md`](knowledge/embedded-iot-firmware-decision-trees.md)** —
  Mermaid decision trees for bare-metal vs RTOS selection, OTA strategy (A/B vs delta vs
  incremental), and power-mode selection, plus a dated 2026 capability map of the ecosystem
  (FreeRTOS/Zephyr/Embassy, STM32/ESP32/nRF, OTA platforms, secure boot tooling).
  **Traverse the relevant Mermaid tree top-to-bottom before recommending** — the proactive
  complement to the Capability Grounding Protocol.

---

## 8. Milestones

- **v0.1.0** — initial build: 4 agents (embedded-architect, firmware-engineer, rtos-engineer,
  iot-connectivity-engineer), 3 skills, 3 commands, 2 templates, a decision-tree knowledge bank
  + dated 2026 capability map, 6 best-practice rules, and 1 advisory hook (flags ISR blocking,
  heap in hot path, missing OTA rollback, hardcoded secrets). Created 2026-06-08.
