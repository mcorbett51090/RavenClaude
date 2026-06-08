# Embedded & IoT Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real embedded/IoT engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real device work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: embedded-iot-engineering
product: <freertos | zephyr | esp32 | nrf52 | lorawan | mqtt | generic | etc.>
product_version: "<version or unknown>"
scope: <likely-general | product-specific>
tags: [<tag>, ...]
confidence: <high | medium | low>
reviewed: false
---
```

## Current bank

| File | Tags | Corroborates |
|---|---|---|
| [`2026-06-08-coin-cell-died-in-weeks.md`](2026-06-08-coin-cell-died-in-weeks.md) | power, sleep, ble, battery, duty-cycle | `power-is-spent-mostly-in-sleep`, `budget-flash-ram-power-first` |
| [`2026-06-08-isr-overrun-dropping-data.md`](2026-06-08-isr-overrun-dropping-data.md) | isr, dma, real-time, uart, watchdog | `isrs-flag-and-defer`, `real-time-is-provably-bounded` |
| [`2026-06-08-lora-duty-cycle-throttled.md`](2026-06-08-lora-duty-cycle-throttled.md) | lora, lorawan, radio, duty-cycle, airtime | `pick-the-radio-by-the-power-range-budget`, `the-cloud-is-the-layer-above` |
| [`2026-06-08-ota-bricked-half-the-fleet.md`](2026-06-08-ota-bricked-half-the-fleet.md) | ota, bootloader, flash, rollback, mcuboot | `design-ota-from-day-one`, `watchdog-is-the-last-line-not-the-plan` |
| [`2026-06-08-shared-key-fleet-cloned.md`](2026-06-08-shared-key-fleet-cloned.md) | provisioning, identity, secure-boot, keys, tls | `per-device-identity-never-a-shared-secret`, `secure-boot-and-hardware-root-of-trust` |
