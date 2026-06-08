# Never block in an ISR

**Status:** Absolute rule
**Domain:** Embedded firmware — interrupt handling
**Applies to:** `embedded-iot-firmware`

---

## Why this exists

An ISR (interrupt service routine) runs with the CPU diverted from its normal execution context.
On a bare-metal system, a blocking ISR starves the main loop — nothing else runs until the ISR
returns. On an RTOS, calling a blocking API (e.g. `xQueueReceive`, `osMutexAcquire`,
`vTaskDelay`) from an ISR invokes undefined behaviour or a fatal RTOS assert because the
scheduler's internal state is not protected against ISR-context blocking. Busy-waiting in an ISR
wastes CPU time, inflates interrupt latency for every subsequent interrupt, and can prevent lower-
priority ISRs from ever running.

The consequences are not theoretical: a 10 ms `HAL_Delay` in an ISR on a 1 kHz system clock
means every other ISR is delayed by up to 10 ms — enough to drop UART bytes, miss a DMA half-
transfer, or miss a sensor data-ready pulse.

---

## How to apply

An ISR must do exactly three things: acknowledge the hardware interrupt (clear the flag), move
data to a shared structure (set a `volatile` flag, push to a ring buffer, call a `FromISR`
API), and return. Any processing belongs in a deferred task, a main-loop handler, or a
bottom-half callback.

**Do:**

```c
/* Correct — ISR acknowledges, writes to ring buffer, returns */
void USART2_IRQHandler(void) {
    uint8_t b = USART2->RDR;             /* clears RXNE flag */
    ring_buf_put(&uart_rx_buf, b);       /* lock-free SPSC write — no blocking */
    /* signal the consumer task via a direct task notification (ISR-safe) */
    BaseType_t higher_prio_woken = pdFALSE;
    vTaskNotifyGiveFromISR(uart_task_handle, &higher_prio_woken);
    portYIELD_FROM_ISR(higher_prio_woken);
}
```

- Use `xQueueSendFromISR`, `xSemaphoreGiveFromISR`, or `vTaskNotifyGiveFromISR` (FreeRTOS) or
  `k_sem_give` (Zephyr, safe from ISR context) — never the non-`FromISR` variants.
- Signal a task to wake up and do the heavy work; never do the heavy work in the ISR itself.

**Don't:**

```c
/* WRONG — blocking delay in an ISR */
void EXTI0_IRQHandler(void) {
    HAL_Delay(10);   /* blocks for 10 ms inside the ISR — starvation */
    process_event(); /* processing that could take variable time */
}

/* WRONG — RTOS blocking call from ISR */
void TIM2_IRQHandler(void) {
    xQueueReceive(my_queue, &data, portMAX_DELAY); /* UB in ISR context */
}
```

---

## Edge cases / when the rule does NOT apply

There is no legitimate exception to this rule. Even a "short" busy-wait (e.g.
`while (!(SPI->SR & SPI_SR_TXE));`) inside an ISR is a blocking pattern and must be removed.
If the hardware requires a short hold time (e.g. a few nanoseconds between bit-banged signals),
use `__NOP()` sequences measured in instruction cycles — not a delay loop.

---

## See also

- [`./no-dynamic-allocation-in-hot-or-safety-critical-paths.md`](./no-dynamic-allocation-in-hot-or-safety-critical-paths.md)
- [`./watchdog-and-fail-safe-defaults.md`](./watchdog-and-fail-safe-defaults.md)
- `firmware-engineer` agent — ISR design and deferred processing patterns.
- `rtos-engineer` agent — `FromISR` API selection and priority ceiling.

## Provenance

Reflects MISRA-C guidelines on interrupt behaviour, FreeRTOS documentation on ISR-safe API
variants, and the consensus of every major embedded RTOS user guide (FreeRTOS, Zephyr, ThreadX).
Mechanically checkable: the hook greps for `delay(`, `sleep(`, and RTOS blocking calls without
`FromISR` inside ISR handlers.

---

_Last reviewed: 2026-06-08 by `claude`._
