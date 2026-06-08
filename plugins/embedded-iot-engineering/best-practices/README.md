# Embedded-IoT-engineering best-practices

Atomic, enforceable rules the embedded-iot-engineering agents apply. Each file is one rule with a short rationale; the agents cite them by filename. Canonical decision logic lives in [`../knowledge/embedded-iot-engineering-decision-trees.md`](../knowledge/embedded-iot-engineering-decision-trees.md); these rules are the always-on priors.

| Rule | Gist |
|---|---|
| budget-flash-ram-power-first | Flash/RAM/power/BOM are the design, stated up front |
| rtos-is-a-cost-not-a-default | Reach for an RTOS only for genuine concurrency |
| isrs-flag-and-defer | Interrupts do the minimum; heavy work runs in main context |
| design-ota-from-day-one | Dual-bank A-B + rollback, not a v2 feature |
| secure-boot-and-hardware-root-of-trust | Keys in secure storage; the boot chain verifies each stage |
| per-device-identity-never-a-shared-secret | Unique identity per device, provisioned at manufacture/first boot |
| pick-the-radio-by-the-power-range-budget | The budget picks BLE/LoRa/Wi-Fi/mesh, not familiarity |
| real-time-is-provably-bounded | Meet deadlines by worst-case analysis, not by hoping |
