# Embedded & IoT Engineering KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Power & energy

| Term | Definition | Note |
|---|---|---|
| **Average current** | active mA × active fraction + sleep mA × sleep fraction | Determines battery life; the spec (§3 #1). |
| **Duty cycle** | Fraction of time the device is active vs asleep | The dominant lever on average current (§3 #1). |
| **Sleep floor** | The lowest sleep-mode current the part draws | Often the dominant sink; datasheet- and measurement-verified (§3 #1 #8). |
| **Battery life** | capacity (mAh) ÷ average current (mA), derated | Derate for self-discharge and end-of-life voltage (§3 #1). |

## Real-time & memory

| Term | Definition | Note |
|---|---|---|
| **WCET** | Worst-case execution time of a task/path | Deadlines are met on worst case, not average (§3 #2). |
| **ISR latency** | Time from interrupt to handler start | Bounded latency is part of meeting a deadline (§3 #2). |
| **Schedulability** | Whether all critical tasks meet deadlines under worst-case load | Rate-monotonic / deadline analysis (§3 #2). |
| **Priority inversion** | A low-priority task blocks a high-priority one | A determinism defect on the control path (§3 #4). |
| **Memory budget** | Flash (image) + static RAM + worst-case stack/heap vs the part | RAM exhaustion in the field is a brick (§3 #3). |

## Connectivity & lifecycle

| Term | Definition | Note |
|---|---|---|
| **BLE / LoRa / Wi-Fi / cellular** | Radios trading power/range/bandwidth/cost | Match to the need; don't default to Wi-Fi (§3 #6). |
| **Airtime** | Time the radio is transmitting | Feeds the power budget via TX current (§3 #1 #6). |
| **OTA** | Over-the-air firmware update | Dual-bank + signed + rollback, before fielding (§3 #5). |
| **Dual-bank / A-B** | Two image slots so a bad update can't brick the device | Doubles image footprint — budget it (§3 #3 #5). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
