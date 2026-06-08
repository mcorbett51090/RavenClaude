---
scenario_id: 2026-06-08-coin-cell-died-in-weeks
contributed_at: 2026-06-08
plugin: embedded-iot-engineering
product: nrf52
product_version: "unknown"
scope: likely-general
tags: [power, sleep, ble, battery, duty-cycle]
confidence: high
reviewed: false
---

## Problem

A BLE door/window sensor on an nRF52832 powered by a CR2032 was specced for "two years on a coin cell" but field units were dying in three to six weeks. The active path was efficient — a short advertising burst on each open/close event — so the team assumed the radio was fine and chased the BLE stack for the leak.

## Constraints context

- CR2032, ~225 mAh nominal; target life was two years, which implies an average current budget around 12 µA.
- The device spent >99.9% of its life idle, advertising only on a sensor event a few times a day.
- The reed switch, an LED left fitted from the dev board, and an external sensor IC's regulator were all still powered in "sleep".

## Attempts

- Tried: optimizing the BLE advertising interval and TX power. Saved a little active energy, but active was already a rounding error against the idle time — no meaningful change to life.
- Tried: switching to a lower-power BLE soft-device config. Same story: the active burst wasn't the problem.
- Tried: actually measuring the sleep current with a µA-capable meter instead of estimating it. Sleep draw was ~480 µA, not the assumed ~3 µA — a fit LED resistor path, the sensor IC never put into shutdown, and a GPIO pull-up fighting the reed switch. Fixing those (remove the LED path, shut down the sensor IC between reads, flip the pull configuration) dropped sleep to ~2.5 µA. This was the fix.

## Resolution

With sleep at ~2.5 µA and the rare active bursts, the computed average current landed near the ~12 µA budget and bench-aged units tracked the two-year target. The lesson stuck: the team added a measured sleep-current gate to the design checklist and a `power-budget` estimate to every battery spec.

## Lesson

A battery device lives or dies on its sleep current, not its active efficiency — design and *measure* sleep first. An assumed sleep figure that's off by 100× swamps any active-path optimization. Enumerate every powered peripheral in "sleep," kill the leakage paths (LEDs, regulators, fighting pull-ups), and divide real battery capacity by the measured average current before believing a life number.
