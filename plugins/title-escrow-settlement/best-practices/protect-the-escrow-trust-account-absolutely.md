# Protect the escrow trust account absolutely

**Status:** Absolute rule
**Domain:** Escrow / trust accounting / fiduciary
**Applies to:** `title-escrow-settlement`

> Advisory operations rule, not legal or financial advice. State trust-account rules and ALTA pillar specifics are `[verify-at-use]`. No PII.

---

## Why this exists

Every dollar in the escrow trust account belongs to someone else — a buyer, a seller, a lender, a payoff. A shortage is not a bookkeeping lag; it is a **fiduciary breach** that can trigger license loss, underwriter termination, and personal liability. The escrow trust account is the pillar the entire settlement operation stands on, and it is the first thing a regulator or underwriter audits.

## How to apply

- **Reconcile three ways on a set cadence** (`[verify-at-use]`): bank balance = book balance = sum of open file ledgers. A variance is investigated immediately, not carried.
- **Never commingle.** Escrow/trust funds stay separate from operating funds — always.
- **No negative file ledgers.** A negative ledger means one file is spending another file's money. Zero tolerance.
- **Segregate duties.** Whoever reconciles is not whoever disburses; oversight is independent of the disbursing officer.
- **Run daily oversight** — positive pay, ACH blocks, and reconciliation review — so a problem is caught in days, not at the next audit.

**Do:** treat reconciliation as a non-negotiable daily/periodic control; escalate any variance at once.
**Don't:** "borrow" from the trust account to bridge timing; net across files; let one person both disburse and reconcile.

## Edge cases / when the rule does NOT apply

None on the fiduciary points — no commingling and no negative ledgers are absolute. The *cadence and mechanics* of reconciliation and the applicable state rules are `[verify-at-use]`, but the duty to protect the account does not vary.

## See also

- [`./verify-the-wire-before-you-send-a-dollar.md`](./verify-the-wire-before-you-send-a-dollar.md), [`./never-disburse-against-uncollected-funds.md`](./never-disburse-against-uncollected-funds.md)
- [`../skills/wire-fraud-and-trust-account-controls/SKILL.md`](../skills/wire-fraud-and-trust-account-controls/SKILL.md)

## Provenance

Codifies the `title-escrow-lead` house opinions, the ALTA escrow-trust-accounting pillar, and the disbursement-authorization decision tree. Trust-account/ALTA specifics: [`../knowledge/title-escrow-reference-2026.md`](../knowledge/title-escrow-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
