---
description: "Walk the bare-metal vs RTOS decision tree, select the MCU, lay out the HAL boundary, and produce a firmware architecture spec — flash/RAM budget, partition map, task table, and HAL layering spec."
argument-hint: "[context, e.g. 'STM32L4, BLE, battery-powered sensor hub, 3 periodic tasks, 2 ISRs, OTA required']"
---

You are running `/embedded-iot-firmware:design-firmware-architecture`. Use the `embedded-architect`
discipline, the `bare-metal-and-rtos` skill, and the decision trees in
`knowledge/embedded-iot-firmware-decision-trees.md`.

## Steps

1. **Parse requirements.** Extract: MCU family (or "TBD"), peripherals, communication protocols,
   power source (battery vs mains), real-time deadlines, concurrency count (ISR sources + periodic
   tasks), OTA requirement (yes/no), and safety/certification level.

2. **MCU selection** (if TBD). Score shortlisted options on: flash/RAM fit (including OTA
   partition budget), peripheral set match, power envelope (active + sleep current), toolchain
   quality, RTOS/SDK support, availability. State the winner and the runner-up with the decisive
   factor.

3. **Bare-metal vs RTOS decision.** Traverse the `Bare-metal vs RTOS selection` tree in
   `knowledge/embedded-iot-firmware-decision-trees.md`. State the leaf you land on. If RTOS, name
   the RTOS (FreeRTOS / Zephyr / Embassy) and the decisive factor.

4. **Flash and RAM budget.** Lay out the partition map:
   - Bootloader (if secure boot / OTA)
   - Slot 0 (active firmware)
   - Slot 1 (OTA update slot, if A/B OTA)
   - NVS / configuration storage
   - Compute utilization ratio: `used / total` for both flash and RAM.

5. **HAL layering spec.** Define the three layers: BSP (board-specific pin/clock init), HAL
   (peripheral abstraction API — function signatures only), Application (calls HAL, never
   registers). Output the HAL API header skeleton for the top 2–3 peripherals in scope.
   Fill `templates/hal-layering-spec.md`.

6. **Task table** (if RTOS). For each task: name, priority, stack size (with sizing rationale),
   activation source, communication channel. Flag any priority inversion risk.

7. **Output.** Emit the filled `templates/hal-layering-spec.md` + a structured summary with the
   Structured Output block including handoffs:
   - `firmware-engineer` for driver implementation
   - `rtos-engineer` for task design (if RTOS selected)
   - `iot-connectivity-engineer` if OTA or connectivity is in scope
