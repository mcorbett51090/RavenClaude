---
name: treatment-room-and-injector-utilization
description: "Read a med spa on its two scarce inventories — injector-hours and treatment-room-hours. Utilization = productive hours booked / available, read by provider and by room and by daypart; confirm the current capacity is full before adding an injector, a room, or a device."
---

# Treatment-Room & Injector Utilization

A med spa is a stack of injector-hours and treatment-room-hours, and the injector is usually the binding constraint. Both are perishable — an hour that goes empty cannot be resold tomorrow. This skill reads utilization before the practice spends on capacity.

## The loop

1. **Compute utilization two ways.** Injector/provider utilization (productive hours booked / available) **and** room utilization. The lower of the two is the real constraint; adding the other does nothing. Benchmarks are `[verify-at-use]`.
2. **Read it by daypart.** A book that's full Saturday and empty Tuesday is a demand-shaping problem (see pricing/membership), not a capacity one.
3. **Separate revenue from busy-ness.** Revenue per available injector-hour and per room-hour catch the full-but-low-contribution book that a headcount view misses.
4. **Test the constraint before adding capacity.** Don't add an injector, a room, or a device until the current scarce resource runs full at peak. A half-full book is a fill problem.
5. **Feed the device decision.** A capital device consumes room-hours; its payback (see below) must clear the value of the room-hours it displaces. Hand the payback model to `med-spa-operations-lead`.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Injector utilization | productive hrs booked / available | Usually the binding constraint; `[verify-at-use]` on norms |
| Room utilization | productive room-hrs booked / available | The other half; the lower one binds |
| Revenue per available injector-hour | service revenue / injector-hours | Catches full-but-low-contribution books |
| Peak vs off-peak fill | daypart utilization spread | Demand-shaping signal |
| Device utilization (if applicable) | device treatment-hrs / available | The payback denominator |

## Anti-patterns

- Adding an injector or a device to fix what is a fill-rate problem.
- Reading a single blended utilization number that hides the binding constraint.
- Buying a device on the vendor's full-utilization payback instead of the practice's realistic volume.
- Ignoring the empty daypart because the peak is full.

## See also

- [`../service-mix-injectables-devices-memberships/SKILL.md`](../service-mix-injectables-devices-memberships/SKILL.md) — mix and device payback ride on these hours.
- Best practices: [`../../best-practices/injectables-are-perishable-provider-hours.md`](../../best-practices/injectables-are-perishable-provider-hours.md).
- Command: [`/model-device-payback`](../../commands/model-device-payback.md).
