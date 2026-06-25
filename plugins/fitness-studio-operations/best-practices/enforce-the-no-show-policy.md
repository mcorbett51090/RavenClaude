# Enforce the no-show policy

**Status:** Absolute rule
**Domain:** Schedule / member experience
**Applies to:** `fitness-studio-operations`

---

## Why this exists

Capacity-limited classes are the studio's scarcest resource. A member who books and doesn't show — or cancels too late for the waitlist to fill the spot — turns a sold seat into ghost capacity: the class looks full, the room is half empty, and a member who wanted in was turned away. A policy that exists on paper but isn't enforced does nothing; behavior only changes when the consequence is automatic.

## How to apply

Define all three, or it's decoration:

1. **Window** — how late a cancel becomes a "late cancel" (commonly 12h, some 24h; `[verify-at-use]`).
2. **Penalty** — a fee or a forfeited class credit, sized to change behavior.
3. **Enforcement mechanism** — wired into the booking system and applied automatically, with the waitlist auto-promoting the freed spot.

Set the penalty to **protect capacity, not to earn revenue** — if no-show fees are quietly profitable, your enforcement or your caps are wrong.

**Do:** automate the penalty and the waitlist auto-promote.
**Don't:** ship a policy with no enforcement, or treat the fee as a revenue line.

## Edge cases / when the rule does NOT apply

A brand-new studio building goodwill may run a softer first-offense grace — but the policy and its mechanism still exist from day one, even if the first strike is forgiven.

## See also

- [`./manage-capacity-by-utilization-not-headcount.md`](./manage-capacity-by-utilization-not-headcount.md)
- [`../skills/design-instructor-pay-model/SKILL.md`](../skills/design-instructor-pay-model/SKILL.md)

## Provenance

Boutique-studio booking-policy practice. Codifies the `class-and-instructor-ops-lead` house opinion ("a no-show policy that isn't enforced is decoration").

---

_Last reviewed: 2026-06-25 by `claude`_
