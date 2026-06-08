---
scenario_id: 2026-06-08-building-ahead-of-takt
contributed_at: 2026-06-08
plugin: manufacturing-operations
product: toc
product_version: "unknown"
scope: likely-general
tags: [takt, cycle-time, over-production, wip, machine-utilization, throughput, flow]
confidence: high
reviewed: false
---

## Problem

A high-speed packaging line was run flat-out "to keep the machine busy" — utilization was the floor's headline metric, and the supervisor was rewarded for keeping it near 100%. The line ran well faster than customer demand, and the result was aisles of finished-goods inventory, a chronic cash crunch, and frequent changeover scrambles when the schedule whipsawed to whatever sold. Management read the high utilization as efficiency and couldn't understand why margins were thin and the warehouse was overflowing.

## Constraints context

- Customer demand was ~450 units/shift against ~27000 seconds of available time — a takt of 60 seconds/unit. The machine's measured cycle time was ~40 seconds: it could run far ahead of demand.
- "Efficiency" was measured as machine utilization, so every idle minute looked like waste and the operators were pushed to build whatever could be built, not what was needed next.
- The over-built inventory masked downstream problems (a quality escape and a supplier delay both sat hidden under the WIP for weeks before surfacing).

## Attempts

- Tried: adding warehouse racking and a second forklift to handle the finished-goods pile. Failed — that subsidized the over-production instead of stopping it; the pile kept growing and the cash bind worsened.
- Tried: incentivizing even higher utilization to "earn back" the inventory cost. Failed — building faster than takt makes inventory faster, not money; it deepened exactly the problem it was meant to solve.
- Tried: pacing the line to takt (60s/unit) instead of machine speed, switching the headline metric from utilization to on-time-to-takt and finished-goods turns, and using the freed time for planned changeovers and TPM. This worked.

## Resolution

Paced to takt, the line built what the customer pulled and stopped manufacturing inventory. Finished-goods stock fell sharply, the cash crunch eased, and — the unlock no one predicted — the quality escape and the supplier delay surfaced within days instead of weeks, because they were no longer buried under a mountain of WIP. Utilization dropped on paper and throughput-to-demand and margin both improved; the metric had been measuring the wrong thing.

## Lesson

Produce to takt, not to machine speed. Building faster than the customer demand rate is over-production — the loss that hides every other problem (here, a quality escape and a supplier delay sat invisible under the WIP). Machine utilization is a vanity metric at a non-constraint; the takt-vs-cycle gap is the signal. Pace the line to the drumbeat of demand.
