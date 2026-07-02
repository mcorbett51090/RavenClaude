# Set the parts matrix once, then manage it

**Status:** Pattern
**Domain:** Parts margin / gross profit
**Applies to:** `auto-repair-shop-operations`

> Advisory operations/financial rule. Matrix tiers and percentages are `[verify-at-use]` against the shop's own margin target. No customer PII.

---

## Why this exists

Parts gross profit is one of the shop's two profit engines, and it is a **decision the shop makes** — not a default the parts vendor makes for you. A flat markup over-prices expensive parts (making the ticket uncompetitive) and under-earns on cheap ones (leaving margin on the counter). A **parts matrix** prices by cost tier — higher markup percentage on low-cost parts, lower on high-cost parts — to hit a target blended parts GP% while staying competitive on big-ticket jobs. The discipline is to set the matrix deliberately against a target margin, load it into the shop system, and then *review it* as costs move — rather than re-deciding every part by hand or letting the vendor's list price set the margin.

## How to apply

- Build the matrix in **cost tiers** with markup percentages that reach a target blended parts GP% (`[verify-at-use]`).
- Handle special categories (tires, batteries, sublet) with their own rules rather than forcing them into the matrix.
- Load it once into the shop management system so pricing is consistent, not advisor-by-advisor.
- **Review** the matrix periodically against parts-cost changes and the shop's realized parts GP% — set-once does not mean set-and-forget.

**Do:** price from a tiered matrix to a target margin; review as costs change.
**Don't:** apply a flat markup; let the vendor's list price set your margin; re-negotiate every part off-the-cuff.

## Edge cases / when the rule does NOT apply

Customer-supplied parts, warranty parts, and price-matched competitive jobs sit outside the matrix and follow their own (documented) policy — the matrix governs the shop's standard parts pricing.

## See also

- [`../skills/effective-labor-rate-and-gross-profit/SKILL.md`](../skills/effective-labor-rate-and-gross-profit/SKILL.md)
- Template: [`../templates/shop-kpi-dashboard.md`](../templates/shop-kpi-dashboard.md)

## Provenance

Codifies `auto-repair-shop-lead` house opinion and the price-a-job decision tree. The matrix concept + tiers: [`../knowledge/auto-repair-shop-reference-2026.md`](../knowledge/auto-repair-shop-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
