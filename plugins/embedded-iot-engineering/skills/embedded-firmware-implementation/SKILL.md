---
name: embedded-firmware-implementation
description: "Implement low-level firmware on the metal: peripheral drivers (I2C/SPI/UART) from the datasheet, flag-and-defer ISRs, DMA paths for throughput, bounded-latency real-time code, a health-check-driven watchdog, and JTAG/SWD debugging of hangs and hard faults — in C/C++/Rust."
---

# Embedded Firmware Implementation

## Drivers from the datasheet
Trace the register sequence, timing requirements, and errata to the part's datasheet — and note where you did. A driver written from memory of a similar chip is a field bug. Give the driver a non-blocking API with explicit error/timeout handling.

## ISRs flag and defer
An interrupt handler reads the hardware that demanded attention, sets a flag or pushes to a queue/ring, and returns. No `printf`, floating-point, busy-wait, or mutex acquire in interrupt context. Assign interrupt priorities deliberately. Guard ISR/main shared state with atomicity (a critical section or a lock-free ring), not `volatile` alone.

## DMA for throughput
Use DMA for bursty or back-to-back transfers so the core can sleep or work — the cheapest interrupt is the one that doesn't fire per byte. Handle the half/full-transfer interrupts and the buffer ownership (and cache coherency where it applies) carefully.

## Real-time is bounded
Meet a deadline by analysis: worst-case ISR latency, priority assignment, no unbounded blocking, no dynamic allocation in the path. State the worst case you hold. "Fast enough" on the happy path fails when the bus stalls.

## Watchdog + fault handling + debug
Kick the watchdog only from a health check that proves the system is progressing, never blindly from a timer. Write a fault handler that records the stacked context to retained RAM, keep SWD/JTAG access, and log in a way that survives a reset — so a field fault is diagnosable, not a mystery. Reproduce with a recorded context before theorizing.

## Output
A driver / fix with a flag-and-defer ISR, a non-blocking API, bounded worst-case latency, and the datasheet trace — or a fault diagnosis with the recorded context and root cause. Escalate architecture changes (RTOS task vs super-loop, partition layout) to `firmware-architect`; key-handling code to `security-reviewer`.
