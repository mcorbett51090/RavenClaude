# embedded-iot-firmware — best-practice docs

Named, citable rules for the `embedded-iot-firmware` plugin's specialists. Each file is
**one rule**.

---

## Index

_6 rules._

| Doc | Status | Use when |
|---|---|---|
| [`never-block-in-an-isr.md`](./never-block-in-an-isr.md) | Absolute rule | Writing or reviewing any ISR |
| [`no-dynamic-allocation-in-hot-or-safety-critical-paths.md`](./no-dynamic-allocation-in-hot-or-safety-critical-paths.md) | Absolute rule | Allocating memory in firmware, especially in ISRs or tight loops |
| [`design-ota-with-a-b-partitions-and-rollback.md`](./design-ota-with-a-b-partitions-and-rollback.md) | Absolute rule | Designing or reviewing any OTA update scheme |
| [`secure-boot-and-signed-firmware-images.md`](./secure-boot-and-signed-firmware-images.md) | Absolute rule | Any network-connected device that accepts firmware updates |
| [`budget-power-before-you-write-code.md`](./budget-power-before-you-write-code.md) | Pattern | Starting or reviewing a battery-powered or power-constrained design |
| [`watchdog-and-fail-safe-defaults.md`](./watchdog-and-fail-safe-defaults.md) | Pattern | Reviewing production firmware or any fault-handling path |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../knowledge/embedded-iot-firmware-decision-trees.md`](../knowledge/embedded-iot-firmware-decision-trees.md) — decision trees + 2026 capability map.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
