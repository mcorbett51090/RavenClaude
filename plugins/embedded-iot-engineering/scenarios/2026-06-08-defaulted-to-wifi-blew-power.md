---
scenario_id: 2026-06-08-defaulted-to-wifi-blew-power
contributed_at: 2026-06-08
plugin: embedded-iot-engineering
product: connectivity
product_version: "n/a"
scope: likely-general
tags: [protocol-selection, power-range-bandwidth, lora, wifi]
confidence: medium
reviewed: false
---

## Problem

A team picked Wi-Fi for an outdoor sensor 'because it's familiar,' and the radio drained the battery and couldn't reach the gateway. The risk: protocol is a power/range/bandwidth/cost trade, and defaulting to Wi-Fi for low-rate long-range telemetry blows both the power and range budgets (§3 #6).

## Context

- Device: battery sensor sending small telemetry packets over a long outdoor range.
- Constraint: BLE/LoRa/Wi-Fi/cellular trade power, range, and bandwidth; the app needed long range and a low data rate — a LoRa/NB-IoT regime, not Wi-Fi (§3 #6).
- The team reasoned from familiarity, not the need.

## Attempts

- Tried: **stated the actual need** — data rate, range, and the energy budget — before picking the radio. Outcome: a few bytes per interval over kilometers, with a tight battery budget (§3 #6).
- Tried: **mapped the need to the regime.** Outcome: Wi-Fi's high-rate/high-power profile was wrong on both range and energy; LoRaWAN fit the rate and range at a fraction of the airtime energy (§3 #6).
- Tried: **fed the radio airtime into the power budget and costed the BOM** via `embedded_iot_calc.py bom-cost`. Outcome: the LoRa choice met the battery target and the per-unit cost (§3 #1 #6).

## Resolution

The fix was to **select the protocol from the data-rate/range/energy need (LoRaWAN), not from familiarity** — feeding airtime into the power budget and costing the BOM. The output was the protocol selection on the power/range/bandwidth/cost trade and the airtime-energy implication. Radio certification routed to the lab (§2).

**Action for the next consultant hitting this pattern:** **select the radio from the need, never default to Wi-Fi.** Match data rate, range, and energy budget to the regime (long-range-low-rate ≠ local-high-rate), feed TX airtime into the power budget, and cost the connectivity BOM. See Tree 3 and the `bom-cost` mode (§3 #1 #6).

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
