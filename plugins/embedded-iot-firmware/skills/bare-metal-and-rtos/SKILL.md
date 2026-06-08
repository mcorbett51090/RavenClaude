---
description: "Decide bare-metal vs RTOS, design the concurrency model (super-loop, cooperative, FreeRTOS, Zephyr, Embassy), apply rate-monotonic priority assignment, document the task table, and size stacks from measured high-water marks."
---

# Bare-Metal and RTOS Design

**Purpose:** produce a correct, analysable concurrency model for embedded firmware — from the
initial bare-metal vs RTOS decision through to a fully specified task table with priorities,
stack sizes, synchronization primitives, and a priority-inversion risk summary.

---

## Entry point

1. **Count concurrent concerns.** List every periodic obligation (sensor read at 1 kHz, control
   loop at 100 Hz), every event-driven interrupt source (UART RX, button press, DMA complete),
   and every background job (logging, OTA download). The count and their timing relationships
   drive the OS choice.

2. **Traverse the bare-metal vs RTOS decision tree** in
   [`../../knowledge/embedded-iot-firmware-decision-trees.md`](../../knowledge/embedded-iot-firmware-decision-trees.md).
   State the leaf you land on before proceeding.

---

## Bare-metal super-loop design

When the tree says "bare-metal is sufficient":

- Design the super-loop with non-blocking state machines per concern.
- Assign each ISR the minimal job: set a `volatile` flag or write to a ring buffer.
- Use a cooperative round-robin in the loop body — each state machine checks its flag and
  processes one step per iteration.
- Document the worst-case loop period (sum of all active paths) and confirm it meets every
  deadline.
- **Anti-pattern:** calling `HAL_Delay` or any busy-wait inside the loop or an ISR.

---

## RTOS task design (FreeRTOS / Zephyr)

When the tree says "use an RTOS":

### Task decomposition
- One task per coherent concern. Split by activation source (periodic vs event) and by timing
  criticality (hard-deadline vs soft-deadline vs background).
- Typical structure: `sensor_task` (periodic, high priority), `control_task` (periodic, high),
  `comms_rx_task` (event, medium), `logging_task` (background, low), `ota_task` (background, low).

### Priority assignment (rate-monotonic baseline)
- Periodic tasks: higher frequency → higher priority (rate-monotonic assignment).
- Event-driven tasks: priority = urgency of the event, not the frequency.
- All task priorities must be below `configMAX_SYSCALL_INTERRUPT_PRIORITY` in FreeRTOS
  (`CONFIG_SYSTEM_WORKQUEUE_PRIORITY` in Zephyr).

### Synchronization primitive selection
| Scenario | Primitive |
|---|---|
| ISR signals task | Binary semaphore (`xSemaphoreGiveFromISR`) or direct task notification |
| ISR passes data to task | Queue (`xQueueSendFromISR`) |
| Shared resource, one holder at a time | Mutex with priority inheritance |
| Multiple producers, one consumer | Queue |
| Wait for any of N events | Event group (FreeRTOS) / `k_poll` (Zephyr) |

### Stack sizing
1. Instrument with `uxTaskGetStackHighWaterMark` after a representative stress run.
2. High-water mark < 10 words remaining → increase stack size immediately.
3. Rule of thumb starting point: 512 bytes (Cortex-M0+), 1024 bytes (Cortex-M4), add 128 bytes
   per level of deep call nesting, add 128 bytes if the task uses FPU (Cortex-M4F/M7).
4. Document the final size and the measured minimum remaining words in the task table.

### Priority inversion risk assessment
- For every mutex in the design: list all tasks that acquire it. If the highest-priority acquirer
  and the lowest-priority holder differ by more than one priority level, flag the inversion risk.
- Use `configUSE_MUTEXES = 1` (FreeRTOS mutex, not binary semaphore) so priority inheritance is
  active.

---

## Embassy (Rust async) specifics

- Embassy async tasks share an executor; `await` points are cooperative yield points.
- Long `poll` segments (no `await`) between async calls starve other tasks.
- embassy-time `Delay` and `Timer` replace `HAL_Delay` — they yield the executor.
- Stack is per-task at compile time: `#[embassy_executor::task]` stack = one contiguous buffer;
  no dynamic allocation by default.
- Interrupt priorities: `bind_interrupts!` macro ties an interrupt to a driver; keep RTIC-style
  ceiling-aware design even in async code.

---

## Anti-patterns

- An RTOS for a firmware with one ISR and one periodic task — super-loop wins.
- Missing timeout on any `xQueueReceive` / `osMutexAcquire` in production code.
- Binary semaphore used as a mutex (no ownership → no priority inheritance).
- Stack sizes unchanged from the project-template default without measurement.
- Priority inversion undocumented and untested ("the mutex is only held briefly").

---

## Output

A **task table** (name / priority / stack-size / activation-source / owned-resources /
communication-channel) + a **priority-inversion risk table** + the bare-metal vs RTOS decision
leaf. Reference [`../../templates/hal-layering-spec.md`](../../templates/hal-layering-spec.md)
if the HAL is being designed in the same pass.
