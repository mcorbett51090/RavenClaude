# Hotel & Hospitality Operations KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Revenue & rate

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Occupancy** | Rooms sold ÷ rooms available | Period | One factor of RevPAR, not the goal (§3 #1). |
| **ADR** | Room revenue ÷ rooms sold | Period | The other factor; trades with occupancy (§3 #1). |
| **RevPAR** | Room revenue ÷ rooms available = ADR × occupancy | Period | Optimize the product (§3 #1). |
| **Net rate** | Gross rate − channel acquisition cost | Per booking | The margin a channel keeps (§3 #2). |

## Pace & mix

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Booking pace** | On-the-books vs same point prior cycle | Forward | A forecast signal, not a snapshot (§3 #3). |
| **Pickup** | Bookings added since the last read | Rolling | The momentum of the pace curve (§3 #3). |
| **Length-of-stay** | Avg nights per reservation | Period | Longer stays smooth the pace curve. |
| **Segment mix** | Transient / group / corporate share | Period | Rate vs certainty trade-off (§3 #7). |

## Profit & labor

| Metric | Definition | Window | Note |
|---|---|---|---|
| **GOPPAR** | Gross operating profit ÷ rooms available | Period | What the owner is paid from (§3 #5). |
| **Hours per occupied room** | Labor hours ÷ occupied rooms | Period, by dept | The productivity lever (§3 #4). |
| **Labor cost/occ room** | Labor cost ÷ occupied rooms | Period | Flex to the occupancy forecast (§3 #4). |
| **Flow-through** | Δ GOP ÷ Δ revenue | Period | How much new revenue reaches profit (§3 #5). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
