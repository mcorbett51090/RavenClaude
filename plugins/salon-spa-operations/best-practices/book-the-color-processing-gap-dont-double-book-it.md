# Book the color processing gap, don't double-book it

**Status:** Pattern
**Domain:** Booking / scheduling
**Applies to:** `salon-spa-operations`

---

## Why this exists

Color and chemical services have a built-in dead zone: while a client's color processes (develops), the colorist is free. A colorist who can't use that window wastes 20-45 minutes of paid chair-time per color client. But "book a second client during processing" sounds like a double-booking error — and becomes one if it lives in a stylist's head instead of the booking system. The difference between extra capacity and a furious double-booked client is whether the overlap is *encoded*.

## How to apply

- **Encode processing time** as its own block (or overlapping appointment type) in the booking system, so a second appointment can legitimately slot into it.
- **Match the second service to the window** — a quick cut, a blowout, a consult — not something that collides with the color finish.
- **Never rely on memory.** If the system can't represent the overlap, it's a double-booking risk, not capacity.

**Do:** treat encoded processing-time overlap as planned capacity that lifts color-client throughput.
**Don't:** stack two full services on one stylist with no system representation and call it efficiency.

## Edge cases / when the rule does NOT apply

A solo stylist or a salon whose software can't model overlap should leave buffers instead of improvising — the unencoded "double-book" is the anti-pattern this rule exists to prevent.

## See also

- [`./measure-chair-utilization-not-bookings.md`](./measure-chair-utilization-not-bookings.md)
- [`../knowledge/salon-spa-operations-decision-trees.md`](../knowledge/salon-spa-operations-decision-trees.md) (empty-chair tree)

## Provenance

Codifies the team house opinion ("color services have processing-time overlap — book the gap, don't double-book it").

---

_Last reviewed: 2026-06-25 by `claude`_
