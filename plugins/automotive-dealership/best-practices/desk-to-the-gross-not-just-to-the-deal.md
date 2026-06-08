# Desk to the gross — not just to the deal

**Status:** Pattern
**Domain:** Sales desking, variable ops
**Applies to:** `automotive-dealership`

---

## Why this exists

A deal that closes is not automatically a good deal. A salesperson or manager focused
purely on closing — hitting the customer's payment target, making the trade work, getting
the signature — can close a deal at negative front-end gross with no F&I opportunity
flagged, producing a transaction that costs the store money in variable expense. The goal
is total gross (front-end + F&I back-end + trade spread), not a signed purchase agreement.

The discipline of "desking to the gross" means structuring every deal with an explicit
front-end gross target, a trade spread awareness, and an F&I opportunity flag — and making
sure the store's minimum acceptable structure (the floor) is understood before the first
pencil is thrown.

## How to apply

Manage the desk with three numbers visible at all times: front-end gross, trade spread,
and F&I opportunity flag. Never close a deal without knowing all three.

**Do:**

- Set a front-end gross target before the first pencil. The first pencil should be gross-
  appropriate, not a courtesy offer.
- Track trade spread explicitly: `ACV − customer's asked allowance`. Over-allowancing
  a trade is borrowing from gross and crediting it to the customer.
- Flag F&I opportunity on every deal structure: what products apply, what penetration
  impact does this deal structure have on PVR.
- Establish a "floor" — the minimum acceptable deal structure — before negotiations start.
  Know when to walk.
- Use a desking worksheet (see `templates/desking-worksheet.md`) so all metrics are visible.

**Don't:**

- Pencil a deal without knowing the front-end gross at that pencil.
- Accept a trade over-allowance as a "cost of the deal" without explicitly netting it
  against front-end gross.
- Focus exclusively on payment without checking what rate/term the payment assumes.
- Skip the F&I opportunity flag because "the customer said no F&I" — that is the
  presentation-rate issue for the F&I office to handle, not a reason to not flag it.
- Let the first pencil be so close to the customer's ask that the store negotiates itself
  to a loss.

## Edge cases / when the rule does NOT apply

In manufacturer fleet or incentive programs with defined contract prices, the front-end
gross is constrained by the program terms. The desking discipline still applies to the
trade and F&I elements; the front gross is the program price, not a negotiation.
Volume-bonus transactions where significant backend manufacturer money effectively
supplements front gross require a separate accounting lens — the total deal economics
include the bonus, but the desk should not rely on unsecured backend money in the first pencil.

## See also

- [`./days-supply-drives-floor-plan-cost.md`](./days-supply-drives-floor-plan-cost.md)
- [`./fni-must-clear-compliance-no-payment-packing.md`](./fni-must-clear-compliance-no-payment-packing.md)
- [`../templates/desking-worksheet.md`](../templates/desking-worksheet.md)
- [`../skills/inventory-and-desking/SKILL.md`](../skills/inventory-and-desking/SKILL.md)
- [`../scripts/dealer_calc.py`](../scripts/dealer_calc.py) — `front_back_gross` mode

## Provenance

Standard sales management discipline documented in NADA guides, dealer 20-group manager
training programs, and automotive retail management curriculum. The "four-square" critique
that motivates this rule is documented in FTC and state AG enforcement actions against
payment-obfuscation methods.

---

_Last reviewed: 2026-06-08 by `claude`._
