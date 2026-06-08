---
description: "Design peripheral drivers (SPI/I2C/UART/DMA) with correct ISR discipline and static allocation, then apply a power budget — traverse sleep modes, gate peripheral clocks, size the radio duty cycle, and verify the design meets the battery-life target before writing code."
---

# Low-Power Design and Peripheral Driver Engineering

**Purpose:** produce interrupt-safe, DMA-correct peripheral drivers and verify the power budget
(sleep modes, peripheral clock gating, radio duty cycle) before committing to an architecture.

---

## Entry point

1. **Peripheral inventory.** List every peripheral in use, its active current, its idle current
   with clock gated, and whether it needs DMA or interrupt-driven transfer.
2. **Traverse the power-mode selection tree** in
   [`../../knowledge/embedded-iot-firmware-decision-trees.md`](../../knowledge/embedded-iot-firmware-decision-trees.md).
   Identify the deepest achievable sleep mode for each phase of device operation.

---

## Peripheral driver design

### ISR discipline (the minimal ISR contract)

Every ISR must do exactly three things: acknowledge the hardware interrupt, move data to a
shared buffer or set a flag, return. No processing, no printing, no blocking.

```c
void USART2_IRQHandler(void) {
    uint8_t b = USART2->RDR;          // read clears the interrupt flag
    ring_buf_put(&uart_rx_buf, b);    // lock-free single-producer write
    /* No processing here. The consumer task wakes on a semaphore or polls the ring buf. */
}
```

**ISR-to-task signalling patterns (in order of preference):**

| Pattern | When to use | Notes |
|---|---|---|
| Direct task notification (`vTaskNotifyGiveFromISR`) | Single consumer, no data needed | Lowest overhead |
| Queue send from ISR (`xQueueSendFromISR`) | ISR passes a typed value | Bounded capacity — size the queue for worst-case burst |
| Binary semaphore give from ISR | Signal without data | Use mutex (not binary sem) when ownership matters |
| Ring buffer write + polling | High-rate data (UART, ADC) | Lock-free SPSC is safe in ISR without RTOS calls |

### DMA design

1. **Coherency on Cortex-M7:** Before starting a TX DMA, call `SCB_CleanDCache_by_Addr` on the
   source buffer. After RX DMA complete, call `SCB_InvalidateDCache_by_Addr` before the CPU reads
   the destination buffer. Skip this step and data corruption is guaranteed on L1-cache-enabled
   cores.
2. **Alignment:** DMA descriptors require 32-byte alignment on some STM32 families. Use
   `__attribute__((aligned(32)))` on DMA buffers; place them in the DMA-capable RAM region
   (not CCM / DTCM if the DMA bus doesn't reach those).
3. **Double-buffer mode:** for continuous ADC or audio, use circular DMA with half-transfer +
   transfer-complete interrupts; process the first half while the second half fills.
4. **Error handling:** enable DMA error interrupt; a DMA stream stuck on an error is a silent
   failure. Log or reset.

### Static allocation patterns

```c
/* Static pool for N fixed-size messages — no malloc, no fragmentation */
typedef struct { uint8_t data[MSG_SIZE]; } msg_t;
static msg_t   msg_pool[MSG_POOL_DEPTH];
static uint8_t pool_in_use[MSG_POOL_DEPTH];  /* bitmap */

msg_t *pool_alloc(void) {
    for (int i = 0; i < MSG_POOL_DEPTH; i++) {
        if (!pool_in_use[i]) { pool_in_use[i] = 1; return &msg_pool[i]; }
    }
    return NULL;  /* pool exhausted — size MSG_POOL_DEPTH correctly at link time */
}
```

Link-time failure is better than runtime `NULL`: `_Static_assert(sizeof(msg_pool) < RAM_BUDGET, ...);`

---

## Power budget design

### The four power phases
1. **Active with radio** — highest current; minimize time in this phase.
2. **Active without radio** — MCU running, radio off or in standby.
3. **Light sleep** — MCU in sleep/WFI, peripherals clocked, waking on interrupt.
4. **Deep sleep** — MCU in Stop/Standby/Hibernate, only RTC + wake-up pins powered.

### Calculating average current

```
I_avg = (I_active × T_active + I_light_sleep × T_light + I_deep_sleep × T_deep) / T_total
```

Battery life (hours) = `battery_capacity_mAh / I_avg_mA`

Work backwards from the target battery life to derive the maximum allowed `I_avg`, then
allocate the budget across phases.

### Peripheral clock gating checklist
- [ ] Unused GPIO ports: `RCC_AHBxENR` bit cleared when not needed.
- [ ] SPI / I2C / UART: clock gated when no transfer is pending.
- [ ] ADC: powered down between conversions (not just stopped — full power-down sequence).
- [ ] Radio (BLE/Wi-Fi): explicit sleep command after each TX/RX burst; disable if protocol
  allows a long idle.
- [ ] Any timer used only as a one-shot delay: disable after firing.

### Radio duty cycle
- Target a duty cycle ≤ 1% for battery-primary devices where protocol allows it.
- Batch telemetry payloads — one large packet is far more efficient than many small ones.
- Use connection-interval (BLE) or sleep period (Wi-Fi / MQTT keep-alive) to control duty cycle.

---

## Anti-patterns

- Any call to `HAL_Delay`, `vTaskDelay` (without yielding), or a busy-while loop in an ISR.
- DMA on Cortex-M7 without corresponding cache clean/invalidate.
- `malloc` or `new` in any interrupt handler or periodic tight loop.
- Leaving peripheral clocks enabled in sleep mode when the peripheral is idle.
- Ring buffer without power-of-two size (wrap-around with `& (size-1)` instead of `% size`).
- Peripheral initialization left incomplete so the peripheral draws full active current during
  sleep.

---

## Output

A **peripheral driver implementation** (ISR + deferred handler + ring buffer or DMA config) +
a **power budget table** (phase / duration / current / I_avg / battery life) + clock-gating
decisions per peripheral. Reference [`../../templates/hal-layering-spec.md`](../../templates/hal-layering-spec.md)
for the HAL interface shape.
