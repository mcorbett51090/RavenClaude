# Never disburse against uncollected funds

**Status:** Absolute rule
**Domain:** Escrow / good funds / disbursement
**Applies to:** `title-escrow-settlement`

> Advisory operations rule, not legal or financial advice. State good-funds rules and funding models are `[verify-at-use]`. No PII.

---

## Why this exists

"Deposited" is a promise; "collected" is money. If you disburse against a deposit that later bounces, is recalled, or is reversed, the funds are already gone to the payees and the shortage lands on your trust account — a direct, often unrecoverable loss and a fiduciary breach. Every state's **good-funds rule** exists precisely to define when incoming funds are safe to disburse.

## How to apply

- **Disburse only against collected/good funds** as defined by your state's good-funds rule (`[verify-at-use]`) — not merely against a deposit posted to the ledger.
- **Know your funding model** — wet vs dry funding, table-funding vs escrow closing — and follow the disburse/record/fund order it requires.
- **Confirm large incoming wires are actually received**, not just "sent," before releasing outgoing funds.
- **Hold the disbursement** when any incoming item is provisional; a fast close is never worth an uncollected-funds loss.

**Do:** treat the good-funds gate as mandatory; verify receipt of incoming funds.
**Don't:** advance your own/other files' money to "bridge" a pending deposit; disburse on the assumption a deposit will clear.

## Edge cases / when the rule does NOT apply

Certain instruments are treated as good funds immediately under some state rules (e.g., verified incoming wires, certain cashier's items) — but *which* ones and *when* is state-specific and `[verify-at-use]`. The rule never bends to time pressure; it bends only to the statute, confirmed.

## See also

- [`./verify-the-wire-before-you-send-a-dollar.md`](./verify-the-wire-before-you-send-a-dollar.md), [`./protect-the-escrow-trust-account-absolutely.md`](./protect-the-escrow-trust-account-absolutely.md)
- [`../skills/escrow-closing-and-disbursement/SKILL.md`](../skills/escrow-closing-and-disbursement/SKILL.md)

## Provenance

Codifies the `closing-settlement-coordinator` house opinions and the disbursement-authorization decision tree. Good-funds specifics: [`../knowledge/title-escrow-reference-2026.md`](../knowledge/title-escrow-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
