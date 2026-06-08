---
description: "Build or audit a firmware power budget — traverse sleep modes, gate peripheral clocks, size radio duty cycle, compute average current, and verify the design meets the target battery life before writing or refactoring code."
argument-hint: "[context, e.g. 'nRF52840, BLE, 400 mAh coin cell, 6 month target, temperature sensor reads every 60 s']"
---

You are running `/embedded-iot-firmware:optimize-power-budget`. Use the `embedded-architect`
and `firmware-engineer` disciplines, the `low-power-and-peripherals` skill, and the
`Power-mode selection` decision tree in `knowledge/embedded-iot-firmware-decision-trees.md`.

## Steps

1. **Requirements capture.** Extract: battery capacity (mAh), target battery life (days/months),
   MCU family, peripheral set (radio, sensors, displays, actuators), operating cycle (what the
   device does in one duty cycle).

2. **Traverse the power-mode tree.** Use the `Power-mode selection` tree in
   `knowledge/embedded-iot-firmware-decision-trees.md` to determine the deepest achievable
   sleep mode for each operational phase. State the leaf for each phase.

3. **Phase decomposition.** Break one duty cycle into phases:
   | Phase | Duration | MCU state | Peripherals active | Estimated current |
   |---|---|---|---|---|
   | Sensor read | Tₐ | Active | ADC + I2C | I_active |
   | Radio TX | Tᵣ | Active | Radio | I_radio |
   | Processing | Tₚ | Active | None | I_cpu |
   | Deep sleep | Tₛ | Stop/Hibernate | RTC only | I_sleep |
   Fill with real datasheet figures; mark any estimated value `[estimate—verify on target]`.

4. **Average current calculation.**
   `I_avg = Σ(Iₙ × Tₙ) / T_total`
   Battery life = `capacity_mAh / I_avg_mA` (hours) → convert to days.
   If the target is not met, identify the highest-contributing phase and propose a reduction.

5. **Peripheral clock-gating audit.** For each peripheral: is the clock disabled when idle?
   Check: GPIO ports, SPI/I2C/UART, ADC, radio, any external flash chip. Provide the register
   write or HAL call needed to gate each one.

6. **Radio duty-cycle recommendation.** Compute: radio active time / total cycle time.
   Target: ≤ 1% for battery-primary BLE/cellular. If above target, recommend batching payloads,
   extending the reporting interval, or switching to a lower-power radio mode.

7. **Firmware changes needed.** List specific changes: which sleep-entry call to add, which
   peripheral disable to add, which reporting interval to change. For each: estimated current
   saving and implementation effort (lines of code / risk level).

8. **Output.** A power budget table (phases + currents + durations + I_avg + battery life
   estimate) + a clock-gating audit table + a ranked list of optimization recommendations by
   impact. Emit the Structured Output block with handoffs to:
   - `firmware-engineer` for peripheral clock-gating implementation
   - `rtos-engineer` if tickless idle or power-aware scheduling changes are needed
   - `iot-connectivity-engineer` if radio duty cycle is the primary driver
