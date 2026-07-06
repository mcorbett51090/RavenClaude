---
name: escrow-closing-and-disbursement
description: "Run the escrow endgame: confirm the commitment requirements are cleared, balance the settlement statement to the lender CD, collect good funds, close/sign, then disburse -> record -> fund in the order the jurisdiction requires. Never disburse against uncollected funds; every good-funds/recording specific is verify-at-use."
---

# Escrow, Closing & Disbursement

The endgame: from clear-to-close to a recorded deed, a funded loan, and every party paid the right amount by verified wire.

> **Advisory, not legal or financial advice.** Good-funds rules, recording requirements, and disbursement/funding order are state- and lender-specific and change — every specific here is `[verify-at-use]`. No PII. You never release funds without verified instructions and satisfied conditions.

## The disbursement-authorization gate (all must be true)

| Condition | Owner | Source |
|---|---|---|
| Schedule B-I requirements cleared, title insurable | `title-examiner` | [`../commitment-and-curative/SKILL.md`](../commitment-and-curative/SKILL.md) |
| Lender conditions met, clear-to-close received | Closer + lender | Closing instructions |
| Settlement statement balances to the lender CD | Closer | Reconcile line by line |
| Funds are **collected/good** (not merely deposited) | Closer | Good-funds rule `[verify-at-use]` |
| Every wire destination verified by callback | Closer | Independently sourced number |

If any is false, you do not disburse.

## Balance the statement to the CD

Reconcile the settlement statement against the lender's Closing Disclosure **line by line** before signing: loan amount, payoffs, prorations (taxes, HOA, interest), credits, seller/buyer fees, title/escrow fees, recording, and cash-to-close. A variance is a defect to resolve **before** the signing, not a rounding tolerance.

## Disburse -> record -> fund (jurisdiction-dependent)

| State type | Order / timing | Note |
|---|---|---|
| Wet-funding | Funds disbursed at/near signing | Good funds must be in hand `[verify-at-use]` |
| Dry-funding | Disbursement after conditions/recording confirmed | Extra confirmation window `[verify-at-use]` |
| Escrow vs table-funding | Who holds and releases | Follow closing instructions + state law |

**Never disburse against uncollected funds.** Deposited is a promise; collected is money. Disburse only against money — a recalled deposit after disbursement is a direct loss.

## Read metrics

| Signal | What it tells you |
|---|---|
| Statement-to-CD variances caught at signing vs after | Whether balancing happens before disbursement |
| Disbursements against uncollected funds (target: zero) | A live good-funds exposure |
| Recording rejections / re-record rate | A document-quality problem upstream |

## See also

- Traverse the **escrow disbursement authorization** and **wire-verification** trees in [`../../knowledge/title-escrow-decision-trees.md`](../../knowledge/title-escrow-decision-trees.md).
- Companion: [`../wire-fraud-and-trust-account-controls/SKILL.md`](../wire-fraud-and-trust-account-controls/SKILL.md); template: [`../../templates/closing-checklist.md`](../../templates/closing-checklist.md); command: [`/run-closing-checklist`](../../commands/run-closing-checklist.md).
- Best practice: [`../../best-practices/never-disburse-against-uncollected-funds.md`](../../best-practices/never-disburse-against-uncollected-funds.md).
