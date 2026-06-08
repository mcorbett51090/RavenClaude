# HAL Layering Specification

> **How to use this template:** fill in every `[PLACEHOLDER]` before this document is used
> as a design reference. Delete this instruction block. Produced by `embedded-architect`.

---

## Project

**Project name:** [PROJECT_NAME]
**MCU / SoC:** [MCU_FAMILY, e.g. STM32L476RGT6]
**Date:** [YYYY-MM-DD]
**Author:** [NAME OR ROLE]
**Status:** Draft / Review / Approved

---

## 1. Layer overview

```
┌──────────────────────────────────────────────────────┐
│  Application layer                                   │
│  (business logic, state machines, protocols)         │
│  Calls HAL API only — never touches registers        │
├──────────────────────────────────────────────────────┤
│  HAL (Hardware Abstraction Layer)                    │
│  (peripheral abstraction — function definitions)     │
│  Owns all register-level and vendor SDK calls        │
├──────────────────────────────────────────────────────┤
│  BSP (Board Support Package)                         │
│  (pin assignments, clock tree, board-specific init)  │
│  One file per board variant                          │
└──────────────────────────────────────────────────────┘
```

**HAL contract:** code above the HAL line must not contain register addresses, vendor SDK
types (`TIM_HandleTypeDef`, `spi_device_handle_t`, etc.), or `#include` of vendor headers.
Code below the HAL line must not contain application concepts (state machine states, protocol
names, business data types).

---

## 2. Peripheral inventory

| Peripheral | HAL module name | Mode | DMA? | ISR? | Power-gated when idle? |
|---|---|---|---|---|---|
| [e.g. SPI1 (sensor)] | `hal_spi.h` | Master, 8-bit | Yes | Yes (DMA) | Yes |
| [UART2 (debug log)] | `hal_uart.h` | TX-only | No | No | Yes |
| [I2C1 (EEPROM)] | `hal_i2c.h` | Master | No | Yes (IRQ) | Yes |
| [GPIO PA5 (LED)] | `hal_gpio.h` | Output | — | — | N/A |
| [ADC1 CH3 (temp)] | `hal_adc.h` | Single / DMA | Yes | Yes (DMA) | Yes |
| [Add rows as needed] | | | | | |

---

## 3. HAL API headers (one section per module)

### 3.1 `hal_spi.h`

```c
/* hal_spi.h — SPI HAL interface. Application code may include ONLY this header. */
#pragma once
#include <stdint.h>
#include <stdbool.h>

/** Initialize the SPI peripheral. Must be called once before any transfer. */
void hal_spi_init(void);

/** Blocking transfer (used only during init/test; prefer async in production). */
bool hal_spi_transfer_blocking(const uint8_t *tx, uint8_t *rx, uint16_t len);

/**
 * Start an asynchronous DMA transfer. Calls @p callback when complete.
 * @p callback is called from ISR context — keep it minimal.
 */
bool hal_spi_transfer_async(const uint8_t *tx, uint8_t *rx, uint16_t len,
                             void (*callback)(bool success));

/** Power-gate the SPI peripheral and its associated DMA stream. */
void hal_spi_power_down(void);
```

### 3.2 `hal_uart.h`

```c
/* hal_uart.h — UART HAL interface. */
#pragma once
#include <stdint.h>
#include <stdbool.h>

void hal_uart_init(uint32_t baud_rate);

/** Non-blocking byte available? */
bool hal_uart_rx_available(void);

/** Read one byte (returns false if no byte available — non-blocking). */
bool hal_uart_rx_byte(uint8_t *out);

/** Transmit len bytes. Returns immediately; callback fires when done. */
void hal_uart_tx_async(const uint8_t *buf, uint16_t len, void (*done_cb)(void));
```

### 3.3 [Add HAL module — copy pattern above]

```c
/* [module_name].h */
```

---

## 4. BSP responsibilities

| BSP item | Implementation file | Description |
|---|---|---|
| System clock init | `bsp_[BOARD].c` | Configure PLL, AHB/APB prescalers |
| GPIO pin mapping | `bsp_[BOARD].c` | All `HAL_GPIO_Init` / `gpio_pin_configure` calls |
| Power domain init | `bsp_[BOARD].c` | Enable peripheral clocks needed at startup |
| Board-specific workaround | `bsp_[BOARD].c` | [Describe any silicon errata workarounds] |

**Porting rule:** to port to a new board, create `bsp_[NEW_BOARD].c` and update the HAL
implementation files. The application layer and the HAL headers do not change.

---

## 5. Mixing-level prohibition

> Rule: a single peripheral must be driven from exactly one level. The HAL either uses the
> vendor SDK (e.g. `HAL_SPI_TransmitReceive`) OR writes registers directly — never both
> on the same peripheral in the same codebase. Mixing levels makes the abstraction fictional.

**Approved vendor SDK usage:** [list SDK and version, e.g. STM32 HAL v1.11, ESP-IDF v5.2]
**Direct register access:** [list any peripheral where direct access is approved and why]

---

## 6. Memory placement (DMA-capable buffers)

| Buffer name | Size (bytes) | Section / region | Alignment | Rationale |
|---|---|---|---|---|
| `spi_tx_buf` | [N] | `.dma_ram` | 32-byte | Cortex-M7 D-cache coherency |
| `spi_rx_buf` | [N] | `.dma_ram` | 32-byte | Same |
| [Add buffers] | | | | |

---

## 7. Decision rationale

| Decision | Option chosen | Why | Rejected alternative |
|---|---|---|---|
| HAL vs direct registers | [HAL / registers] | [Reason] | [Alternative] |
| DMA vs interrupt vs polling for SPI | [DMA] | [Throughput requirement] | [Alternative] |
| [Add decisions] | | | |

---

## 8. Open questions / risks

| # | Question | Owner | Status |
|---|---|---|---|
| 1 | [e.g. Does the DMA reach DTCM on this MCU variant?] | [NAME] | Open |
| 2 | | | |

---

_Last updated: [YYYY-MM-DD] by [AUTHOR]._
