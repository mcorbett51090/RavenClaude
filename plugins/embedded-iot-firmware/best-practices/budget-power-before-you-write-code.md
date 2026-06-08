# Budget power before you write code

**Status:** Pattern
**Domain:** Embedded firmware — power management
**Applies to:** `embedded-iot-firmware`

---

## Why this exists

Power management is not a feature you add at the end. The MCU peripheral configuration, the
RTOS tick rate, the radio duty cycle, and the memory access patterns are all architectural
decisions that affect power consumption — and most of them are expensive to change once the
firmware is written and tested.

The most common embedded power failure is discovering, one week before production, that the
device draws 10 mA in "sleep" mode instead of the budgeted 10 µA — a 1000× overshoot that
kills the target battery life. The cause is almost always a peripheral left clocked, a timer
still running, or a radio not receiving an explicit sleep command. These are not hard to fix
individually, but when they are discovered late, the risk of a regression fix breaking something
else is high.

Establishing the power budget during architecture — before drivers are written — forces the
right questions early: which sleep mode is achievable? What is the peripheral wake-up latency
budget? What is the maximum radio duty cycle? These answers constrain the design rather than
surprising the team at tape-out.

---

## How to apply

**Do:**

1. At architecture time: define the battery capacity, target battery life, and the duty cycle
   (how often the device wakes, does work, and sleeps).
2. Look up the current for every operational phase in the MCU datasheet: active current at
   target clock speed, radio TX/RX current, each sleep mode's quiescent current.
3. Calculate the required average current: `I_avg = capacity_mAh / (lifetime_hours)`.
4. Allocate the budget across phases: `Σ(Iₙ × Tₙ) / T_total ≤ I_avg`.
5. Use the power-mode selection tree in the knowledge bank to choose the deepest achievable
   sleep mode for each phase.
6. Document the clock-gating requirement for every peripheral before the driver is written:
   "ADC must be powered down between conversions" is a driver spec, not a post-hoc optimization.
7. Measure on real hardware with a current probe (e.g. Nordic PPK2, Otii Arc, Segger J-Link
   Energy) before committing to a battery size. Datasheet numbers are best-case; real firmware
   is not.

**Don't:**

- Start writing drivers and then measure power "when it's working."
- Assume the MCU is in the deepest sleep mode just because `WFI` is called — check that all
  peripheral clocks are gated and the correct sleep mode is entered.
- Neglect the radio duty cycle. A BLE advertisement every 100 ms is 10× more expensive than
  one every 1000 ms — check whether the use case requires the faster rate.
- Pick a battery capacity after the hardware is designed based on "what fits" — derive it from
  the power budget.

---

## Edge cases / when the rule does NOT apply

- **Mains-powered devices with no battery life concern:** power budgeting is less critical, but
  thermal management and efficiency may still matter. The peripheral clock-gating audit is still
  good practice.
- **Early prototyping (breadboard / dev kit):** a rough budget based on datasheet numbers is
  sufficient at this stage; full measurement is deferred to a production-representative PCB.
  Mark any budget from this stage as `[estimate — verify on target hardware]`.

---

## See also

- [`./watchdog-and-fail-safe-defaults.md`](./watchdog-and-fail-safe-defaults.md)
- `embedded-architect` agent — power mode selection and MCU selection with power envelope.
- `firmware-engineer` agent — peripheral clock gating in drivers.
- `/embedded-iot-firmware:optimize-power-budget` command — guided power budget design.
- [`../skills/low-power-and-peripherals/SKILL.md`](../skills/low-power-and-peripherals/SKILL.md) — the power budget calculation playbook.

## Provenance

Reflects the design discipline described in _The Art of Designing Embedded Systems_ (Jack
Ganssle), Nordic Semiconductor's low-power design guide for nRF52/nRF91, and the power
management sections of the STM32 application notes. The "budget first, measure early" pattern
is consistent across MCU vendor application notes and embedded-systems industry consensus.

---

_Last reviewed: 2026-06-08 by `claude`._
