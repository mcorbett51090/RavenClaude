# Interrupts do the minimum — flag and defer

An ISR reads the hardware that demanded attention, sets a flag or pushes to a queue/ring buffer, and returns. No `printf`, no floating-point, no busy-wait, no mutex acquire, no blocking bus call in interrupt context — the heavy work runs in the main context. Keep ISRs short and bounded, assign interrupt priorities deliberately, and guard ISR/main shared state with atomicity (a critical section or a lock-free ring), not `volatile` alone. A blocking call in an ISR works until the bus stalls, then hangs the whole system.
