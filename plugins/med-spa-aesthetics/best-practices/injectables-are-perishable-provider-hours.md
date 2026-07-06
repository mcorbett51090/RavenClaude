# Injectables are perishable provider-hours

**Status:** Pattern
**Domain:** Operations / capacity
**Applies to:** `med-spa-aesthetics`

> Operations rule. No patient PHI/PII. Utilization and margin benchmarks are `[verify-at-use]`.

---

## Why this exists

A med spa's scarcest inventory is the injector-hour, and it is perishable — an hour that goes empty cannot be resold tomorrow. Practices reflexively "solve" a revenue gap by adding a device or a room, when the real problem is that the injector's book isn't full at peak. Fill the scarce resource before you add cost to the building.

## How to apply

- Compute injector utilization **and** room utilization; the lower one is the binding constraint. Adding the other does nothing.
- Read utilization by daypart — a full Saturday and an empty Tuesday is a demand-shaping problem, not a capacity one.
- Confirm the scarce resource runs full at peak before adding an injector, a room, or a capital device.
- A capital device consumes room-hours; its payback must clear the value of the hours it displaces.

**Do:** fill the binding constraint first; read utilization two ways and by daypart.
**Don't:** buy a device to fix a fill-rate problem; act on a single blended utilization number.

## Edge cases / when the rule does NOT apply

If the scarce resource is genuinely full at peak and demand is turning away, adding capacity is warranted — model the payback on that real, turned-away demand.

## See also

- [`../skills/treatment-room-and-injector-utilization/SKILL.md`](../skills/treatment-room-and-injector-utilization/SKILL.md)
- [`../skills/service-mix-injectables-devices-memberships/SKILL.md`](../skills/service-mix-injectables-devices-memberships/SKILL.md)

## Provenance

Codifies the `med-spa-operations-lead` house opinions and the add-a-service-or-device decision tree. Benchmarks: [`../knowledge/med-spa-reference-2026.md`](../knowledge/med-spa-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-04 by `claude`_
