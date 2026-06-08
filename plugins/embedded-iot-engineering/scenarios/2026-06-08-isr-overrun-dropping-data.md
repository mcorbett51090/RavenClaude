---
scenario_id: 2026-06-08-isr-overrun-dropping-data
contributed_at: 2026-06-08
plugin: embedded-iot-engineering
product: stm32
product_version: "unknown"
scope: likely-general
tags: [isr, dma, real-time, uart, watchdog]
confidence: high
reviewed: false
---

## Problem

A sensor gateway on a Cortex-M4 read a GPS module over UART at 115200 baud and parsed NMEA sentences in the UART RX interrupt. Under normal load it was fine; during a firmware-heavy operation (a flash write) it intermittently dropped bytes, corrupted fixes, and occasionally the watchdog reset the device. The team had been bumping the UART interrupt priority and shortening the parser, with no durable fix.

## Constraints context

- 192 KB RAM, no RTOS — a bare-metal super-loop.
- The flash write disabled interrupts for milliseconds while it ran, during which UART bytes arrived and overran the single-byte hardware FIFO.
- The watchdog was kicked at the bottom of the main loop, so a long flash write that delayed the loop also looked like a hang.

## Attempts

- Tried: raising the UART ISR priority above everything else. Helped marginally but didn't fix the flash-write window, which disabled interrupts globally regardless of priority.
- Tried: shortening the in-ISR NMEA parser. Reduced the per-byte cost but the real problem was the ISR running at all per byte plus the interrupts-off flash window — bytes were lost while interrupts were off, not while the ISR was slow.
- Tried: DMA-driven UART RX into a ring buffer, with the ISR firing only on the idle-line / half/full-transfer events (not per byte), and the NMEA parse moved entirely into the main loop. Plus moving the watchdog kick to a health check that confirmed the parse task was draining the buffer, and writing flash in smaller chunks that didn't hold interrupts off as long. This worked.

## Resolution

DMA + a ring buffer meant incoming bytes landed in RAM without per-byte CPU involvement, so the brief interrupts-off flash window no longer lost data — the DMA controller kept filling the buffer. The parser, now in the main context, drained the buffer at its own pace. The health-check-driven watchdog stopped firing spuriously because it measured actual progress, not loop timing. Dropped fixes went to zero.

## Lesson

Interrupts flag and defer — and the cheapest interrupt is the one that doesn't fire per byte. For bursty/streamed data, DMA into a ring buffer beats a fast ISR, and real-time correctness comes from bounding the worst case (here, the interrupts-off flash window), not from making the happy-path ISR shorter. Kick the watchdog from a health check that proves progress, never blindly from the loop.
