# Watchdog always on; fail-safe defaults

**Status:** Pattern
**Domain:** Embedded firmware — reliability and fault handling
**Applies to:** `embedded-iot-firmware`

---

## Why this exists

Firmware can hang. A peripheral can stop responding. An RTOS task can deadlock. A cosmic ray can
flip a bit in the program counter. Any of these can leave a device in a state where it is
consuming power, ignoring inputs, and not doing anything useful — or, worse, stuck in an
incorrect partial state that could have physical consequences.

The hardware watchdog timer (WDT) is the last-resort recovery mechanism: if the firmware does
not kick the watchdog before it expires, the WDT resets the MCU unconditionally. It is the
only recovery path that survives a software deadlock or a corrupt stack. A device that disables
the watchdog has no recovery mechanism for a hung firmware.

"Fail-safe defaults" means: when the firmware enters an unhandled fault, it resets to a known-
safe state rather than attempting an optimistic recovery that may leave actuators in an unsafe
position, transmit corrupted data, or silently corrupt NVS.

---

## How to apply

**Do:**

- Enable the hardware watchdog unconditionally in production firmware. The watchdog should be
  enabled in the earliest startup code (bootloader or first startup function), before any
  application initialization.
- Kick the watchdog only from a task or code path that proves the system is healthy. A
  dedicated watchdog-manager task (lowest priority, watchdog is only kicked when all higher-
  priority tasks have checked in) is better than kicking the watchdog from every task
  independently.
- Implement a hard-fault handler that: dumps the exception frame to a fault log (SRAM or NVS),
  kicks the watchdog one last time to log, then resets (or halts in debug builds).
- On reset: check the reset-cause register. If the reset was watchdog-triggered, log the event
  and surface it in telemetry. Repeated watchdog resets indicate a systemic bug.
- Apply fail-safe defaults to actuators: on any unhandled fault, drive actuators to their safe
  state (motor off, valve closed, heater off) before resetting.

**Don't:**

```c
/* WRONG — disabling the watchdog in production */
HAL_IWDG_Init_Disabled();   /* or equivalent "skip WDT init" */

/* WRONG — kicking the watchdog unconditionally from a tight loop
   (hides the exact fault the WDT is supposed to catch) */
while (1) {
    HAL_IWDG_Refresh(&hiwdg);  /* kicked every iteration regardless of system health */
    do_stuff();
}

/* WRONG — hard-fault handler that does nothing */
void HardFault_Handler(void) {
    while (1);  /* hangs forever — WDT can't even reset because we keep looping */
}
```

```c
/* Correct — hard-fault handler that logs and resets */
void HardFault_Handler(void) {
    /* Capture stacked register frame for post-mortem */
    uint32_t *sp = (uint32_t *)__get_MSP();
    fault_log_write(sp);          /* write to NVS / SRAM fault region */
    actuator_safe_state();        /* drive all actuators to safe position */
    NVIC_SystemReset();           /* reset cleanly — WDT will catch a hung reset too */
}
```

- Set the watchdog timeout to the worst-case kick interval plus a 2× safety margin. A 30 ms
  timeout on a system that kicks every 20 ms leaves no room — use 100 ms.

---

## Edge cases / when the rule does NOT apply

- **In-system programming / firmware update window (supervised OTA):** the watchdog timeout
  must be extended during OTA download, or the WDT must be kicked by the OTA task. Some
  platforms provide a way to refresh the watchdog from the download task; others require
  explicit WDT management in the OTA state machine.
- **Debug / development builds:** it can be useful to disable the watchdog in debug builds so
  that a breakpoint does not trigger a reset. Mark this clearly with `#ifdef DEBUG` and ensure
  the production build re-enables it. Never leave a watchdog-disabled binary in a releasable
  build configuration.

---

## See also

- [`./never-block-in-an-isr.md`](./never-block-in-an-isr.md)
- [`./design-ota-with-a-b-partitions-and-rollback.md`](./design-ota-with-a-b-partitions-and-rollback.md) — watchdog role in OTA boot validation.
- `firmware-engineer` agent — hard-fault handler design, exception frame analysis.
- `rtos-engineer` agent — watchdog-manager task pattern in FreeRTOS.

## Provenance

Reflects the hard-fault handling and watchdog guidance in ARM Cortex-M Application Note
AN209 (Using Cortex-M3/M4/M7 Fault Exceptions), the FreeRTOS watchdog best-practices note,
and the IEC 61508 SIL requirements for hardware watchdog timers in safety-relevant embedded
systems. The fail-safe-on-fault principle is a standard requirement in industrial embedded
systems design.

---

_Last reviewed: 2026-06-08 by `claude`._
