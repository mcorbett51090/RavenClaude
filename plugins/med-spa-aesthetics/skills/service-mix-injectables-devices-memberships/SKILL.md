---
name: service-mix-injectables-devices-memberships
description: "Tilt the med-spa service mix toward contribution: read revenue and margin per provider-hour and per room-hour across injectables, energy devices, skincare retail, and memberships; model capital-device payback on realistic volume; size memberships on redemption and the capacity they pre-commit."
---

# Service Mix — Injectables, Devices, Memberships

The four revenue engines of a med spa — injectables, energy-device treatments, skincare retail, and memberships — carry very different margins and consume capacity differently. This skill tilts the mix toward contribution per scarce hour and puts the capital-device decision on honest math.

## The loop

1. **Rank by contribution per scarce hour, not by popularity.** Compute contribution (price − product/consumable cost − provider time cost) per injector-hour and per room-hour. A busy service that's low-contribution is a busy business losing ground. Margins are `[verify-at-use]`.
2. **Injectables vs devices are different shapes.** Injectables are consumable-heavy and injector-time-bound; devices are capital-heavy and room-time-bound. Read them separately.
3. **Model device payback before the purchase.** Device cost + consumables + provider time vs realistic treatment volume × price, against the room-hours locked up. Name the break-even utilization; compare to the alternative use of that capacity. Traverse the **add a service or device** tree in [`../../knowledge/med-spa-decision-trees.md`](../../knowledge/med-spa-decision-trees.md).
4. **Skincare retail is margin that rides on trust.** Attach at the treatment moment; it's the cheapest incremental margin and doesn't consume injector-hours.
5. **Size memberships on redemption and pre-committed capacity.** A membership pre-fills the book and smooths cash, but the included value is a redemption liability. Model breakage honestly; traverse the **design the membership** tree.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Contribution per injector-hour | (price − consumable − provider time) / hr | The ranking metric for injectables |
| Contribution per room-hour | same, per room | The ranking metric for devices |
| Device payback / break-even utilization | capital + consumables vs volume × price | The go/no-go; `[verify-at-use]` on vendor claims |
| Skincare attach rate | tickets with retail / total | Cheapest incremental margin |
| Membership redemption rate | value redeemed / value sold | Breakage is a liability, not a windfall |

## Anti-patterns

- Ranking services by revenue or headcount instead of contribution per scarce hour.
- Buying a device on the vendor's full-utilization payback.
- Counting membership sales as banked revenue before modeling redemption.
- Treating skincare retail as an afterthought instead of a managed attach.

## See also

- [`../treatment-room-and-injector-utilization/SKILL.md`](../treatment-room-and-injector-utilization/SKILL.md) — the hours the mix consumes.
- Best practices: [`../../best-practices/membership-smooths-cash-but-breakage-is-a-liability.md`](../../best-practices/membership-smooths-cash-but-breakage-is-a-liability.md).
- Commands: [`/model-device-payback`](../../commands/model-device-payback.md), [`/design-membership`](../../commands/design-membership.md).
