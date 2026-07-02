---
name: wire-fraud-and-trust-account-controls
description: "Protect the money: verify every wire by out-of-band callback before sending, require dual authorization, reject email-changed instructions, and safeguard the escrow trust account with three-way reconciliation, no commingling, and daily oversight. Business-email-compromise sensitive; each control specific is verify-at-use."
---

# Wire-Fraud & Trust-Account Controls

The two controls that keep a settlement operation solvent: no wire leaves without out-of-band verification, and the escrow trust account is reconciled and protected absolutely.

> **Advisory, not legal or financial advice.** These are operational control patterns, not a compliance certification; specific ALTA pillar language, state trust-account rules, and bank product terms are `[verify-at-use]`. No PII. This skill designs controls; a licensed officer executes them.

## Wire-fraud controls (the disbursement never skips these)

| Control | What it is | Why |
|---|---|---|
| **Out-of-band callback** | Verify every payoff/proceeds destination by phone to a number you sourced independently — never from the email/instruction itself | Business email compromise supplies fake numbers |
| **No change by email** | Any account/routing change to instructions already on file is treated as fraud until re-verified by callback | The classic BEC "updated wire instructions" attack |
| **Dual authorization** | A second authorized person approves every outgoing wire | Removes the single point of failure |
| **Positive pay / bank controls** | Bank-side control on outgoing items | Catches altered/unauthorized items |
| **Educate the parties** | Warn buyers/sellers in writing that wire instructions will not change by email | Most consumer wire fraud hits the party, not the agent |

**The rule:** verify the wire **before** you send a dollar. A callback is cheap; a wire loss is often unrecoverable.

## Trust-account controls (protect the escrow account absolutely)

| Control | Standard |
|---|---|
| **Three-way reconciliation** | Bank balance = book balance = sum of open file ledgers, reconciled on a set cadence (`[verify-at-use]`) |
| **No commingling** | Escrow/trust funds never mixed with operating funds |
| **No negative ledgers** | No file ledger goes negative — that is spending another file's money |
| **Daily oversight** | Positive-pay, ACH blocks, and reconciliation reviewed by someone independent of the disbursing officer |
| **Segregation of duties** | Whoever reconciles is not whoever disburses |

Every dollar in the account belongs to someone else. A shortage is a fiduciary breach, not a bookkeeping lag.

## Read metrics

| Signal | What it tells you |
|---|---|
| Wires sent without documented callback (target: zero) | A live fraud exposure |
| Three-way reconciliation variance / age | Trust-account health |
| Days to detect a ledger negative | Oversight cadence adequacy |

## See also

- Traverse the **wire-verification before disbursement** tree in [`../../knowledge/title-escrow-decision-trees.md`](../../knowledge/title-escrow-decision-trees.md).
- Companion: [`../escrow-closing-and-disbursement/SKILL.md`](../escrow-closing-and-disbursement/SKILL.md); ALTA-pillar reference: [`../../knowledge/title-escrow-reference-2026.md`](../../knowledge/title-escrow-reference-2026.md).
- Best practices: [`../../best-practices/verify-the-wire-before-you-send-a-dollar.md`](../../best-practices/verify-the-wire-before-you-send-a-dollar.md), [`../../best-practices/protect-the-escrow-trust-account-absolutely.md`](../../best-practices/protect-the-escrow-trust-account-absolutely.md).
