# An RTOS is a cost, not a default

Reach for an RTOS only when you have genuinely concurrent, independently-timed work that needs pre-emptive scheduling — not reflexively. A bare-metal super-loop with interrupts (or a cooperative scheduler / state machine) is often smaller, more deterministic, and far easier to debug, and it avoids the per-task stack RAM and scheduler overhead an RTOS imposes. When you do take on an RTOS, document the cost — the per-task stacks and the scheduler footprint — against the RAM budget.
