# Verify the wire before you send a dollar

**Status:** Absolute rule
**Domain:** Escrow / disbursement / fraud control
**Applies to:** `title-escrow-settlement`

> Advisory operations rule, not legal or financial advice. Bank product terms and control specifics are `[verify-at-use]`. Wire-fraud sensitive. No PII.

---

## Why this exists

Business email compromise makes wire fraud the largest single loss vector in real-estate settlement. A fraudster inserts fake "updated wire instructions" into an email thread, and a wire sent to the fraudulent account is frequently **unrecoverable**. The settlement agent holds other people's money and moves it in large amounts — one unverified wire can exceed a year of profit.

## How to apply

- **Verify every wire destination by out-of-band callback** to a number you sourced **independently** — from the file, the payoff statement's official channel, or a directory — never a number that arrived in the same email as the instructions.
- **Treat any change** to instructions already on file (new account, new routing, "the bank changed") as **fraud until re-verified** by callback. No changes accepted by email.
- **Require dual authorization** on every outgoing wire — a second authorized approver.
- **Use bank controls** (positive pay, ACH filters/blocks) and reconcile outgoing items.
- **Warn the consumer in writing** that wire instructions will not change by email — most consumer wire fraud targets the buyer/seller, not the agent.

**Do:** slow down and call a verified number; hold any changed instruction.
**Don't:** wire from emailed instructions; trust caller ID or a number in the email; let time pressure skip the callback.

## Edge cases / when the rule does NOT apply

There is no exception for outgoing wires. Even a "trusted" repeat payee gets a callback when anything changed. The reference file is never a source for a wire destination — verify live, every time.

## See also

- [`./never-disburse-against-uncollected-funds.md`](./never-disburse-against-uncollected-funds.md), [`./protect-the-escrow-trust-account-absolutely.md`](./protect-the-escrow-trust-account-absolutely.md)
- [`../skills/wire-fraud-and-trust-account-controls/SKILL.md`](../skills/wire-fraud-and-trust-account-controls/SKILL.md)

## Provenance

Codifies the `title-escrow-lead` and `closing-settlement-coordinator` house opinions and the wire-verification decision tree. Control/bank specifics: [`../knowledge/title-escrow-reference-2026.md`](../knowledge/title-escrow-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
