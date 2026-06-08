---
description: "Implement a peripheral driver (I2C/SPI/UART) with a flag-and-defer ISR, a non-blocking API, bounded latency, and the datasheet trace — or debug a hang/hard fault over SWD."
argument-hint: "[peripheral + part/datasheet + throughput/timing needs + language]"
---

You are running `/embedded-iot-engineering:implement-driver`. Use `embedded-engineer` + the `embedded-firmware-implementation` skill.

## Steps
1. Trace the register sequence, timing, and errata to the part's datasheet; note where you did. If the datasheet isn't in hand, design from the standard peripheral model and flag the assumption.
2. Write a non-blocking driver API with explicit error/timeout handling.
3. Make the ISR flag-and-defer (read the hardware, push to a queue/ring, return); assign interrupt priorities; guard ISR/main shared state with atomicity, not `volatile` alone.
4. Use DMA + a ring buffer for bursty/high-throughput data; handle half/full-transfer and buffer ownership.
5. State the worst-case latency the driver holds; confirm no unbounded blocking or dynamic allocation in any deadline path.
6. Add fault/watchdog hooks: a fault handler recording context to retained RAM, a health-check-driven watchdog kick; keep SWD access.
7. Emit the driver/fix + the Structured Output block (with `Resource budget impact:` and `Handoff to cloud/app teams:`); escalate architecture changes to firmware-architect, key-handling to security-reviewer.
