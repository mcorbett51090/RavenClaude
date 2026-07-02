---
name: chair-and-room-utilization
description: "Read the salon/spa as a stack of perishable chair-hours and room-hours. Compute utilization (productive hours booked / available), test whether current capacity is full before adding a chair, room, or provider, and tie utilization to the staffing model and demand pattern."
---

# Chair & Room Utilization

Utilization is the master metric of a service-chair business. The inventory is chair-hours (salon/barbershop) and treatment-room-hours (spa) — perishable, finite, and impossible to warehouse. This skill reads that inventory honestly.

## The loop

1. **Define the denominator.** Productive hours available = chairs/rooms x staffed hours x days, net of realistic breaks and turnover time. Overstating availability flatters utilization and hides the gap.
2. **Compute utilization.** Utilization = productive hours booked / productive hours available. Read it by chair, by provider, by daypart, and by day of week — the average hides the empty Tuesday morning and the overbooked Saturday.
3. **Diagnose the gap before spending.** A half-full book is a demand or scheduling problem, not a capacity problem. Traverse toward the pricing tree in [`../../knowledge/salon-spa-decision-trees.md`](../../knowledge/salon-spa-decision-trees.md) — a demand-based menu fills the empty daypart. Treat benchmark utilization targets as `[verify-at-use]`.
4. **Only then size capacity.** Add a chair, room, or provider when the existing inventory runs full at peak and demand overflows — with the staffing-model and payback implication named. See [`../compensation-models-commission-vs-booth-rent/SKILL.md`](../compensation-models-commission-vs-booth-rent/SKILL.md).

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Chair / room utilization | booked productive hrs / available | The master metric; read by daypart, not just average |
| Revenue per available chair-hour | service revenue / available hrs | Catches the low-mix full book |
| Peak vs off-peak split | Saturday vs Tuesday-morning fill | Demand-based pricing target |
| Provider productivity | booked hrs / scheduled hrs per provider | Staffing-model input |

## Anti-patterns

- Reading only the average utilization and missing the empty daypart.
- Adding a chair or room to fix what is a fill-rate problem.
- Counting a full but low-margin book as "at capacity."
- Staffing to peak Saturday all week.

## See also

- [`../retail-attach-and-service-mix/SKILL.md`](../retail-attach-and-service-mix/SKILL.md) — mix tilts revenue per chair-hour.
- Best practice: [`../../best-practices/price-the-menu-on-time-and-demand.md`](../../best-practices/price-the-menu-on-time-and-demand.md).
- Template: [`../../templates/salon-kpi-dashboard.md`](../../templates/salon-kpi-dashboard.md).
