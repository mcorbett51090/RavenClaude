# Design for the tracking volume and guardian

**Status:** Absolute rule
**Domain:** Physical safety / interaction
**Applies to:** `ar-vr-xr-engineering`

> Engineering rule, not a safety certification. Guardian/boundary APIs are `[verify-at-use]` per runtime. No PII.

---

## Why this exists

An XR user's eyes are covered — the app is responsible for keeping them from hitting a wall, tripping, or swinging into furniture. The tracking volume, the guardian/boundary system, and the play-space size are physical-safety design inputs, not incidental details. A build that assumes a large room-scale space a user doesn't have, or that ignores the boundary, puts real bodies at risk.

## How to apply

- Design for the actual play space: room-scale, standing, and seated are different safety designs — support the smallest one your audience will use.
- Respect the guardian/boundary and use passthrough or boundary cues so users know where the physical edges are (`[verify-at-use]` per runtime).
- Keep required reach and movement inside a realistic tracking volume; don't place critical targets where a user must step blindly.
- Provide a seated mode and height calibration so the experience adapts to the user's real space.

**Do:** test in a small play space; surface the boundary before the user reaches it.
**Don't:** require a large room the audience may lack; hide the boundary or disable passthrough safety cues.

## Edge cases / when the rule does NOT apply

Fully seated, no-translation experiences carry lower physical-safety risk — but still respect reach limits, provide recentering, and keep the guardian available.

## See also

- [`../skills/comfort-safety-and-accessibility/SKILL.md`](../skills/comfort-safety-and-accessibility/SKILL.md), [`../skills/xr-interaction-and-locomotion/SKILL.md`](../skills/xr-interaction-and-locomotion/SKILL.md)
- Template: [`../templates/xr-project-architecture.md`](../templates/xr-project-architecture.md)

## Provenance

Codifies `xr-interaction-engineer` house opinion on physical-space design. Guardian/boundary specifics: [`../knowledge/xr-reference-2026.md`](../knowledge/xr-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
