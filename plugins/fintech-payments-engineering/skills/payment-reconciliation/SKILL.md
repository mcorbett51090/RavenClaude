---
name: payment-reconciliation
description: "Step-by-step playbook for reconciling your internal double-entry ledger against the PSP's payout and transaction reports — identifying discrepancies, classifying them, and closing the books with confidence."
---

# Payment Reconciliation

## When to invoke

Use when building the reconciliation job for a new payments integration, investigating a balance discrepancy, or auditing an existing reconciliation process for gaps.

## Concepts

| Term | Meaning |
|---|---|
| PSP report | CSV/API export of all transactions, fees, refunds, and disputes settled in a period |
| Internal ledger | Your double-entry record of every money movement (credit/debit entries) |
| Settlement | When the PSP actually transfers funds to your bank account |
| Payout | A single bank transfer from PSP; may aggregate many transactions |
| Disputed amount | Chargebacks currently open; may not yet be settled/reversed |

**The goal:** every PSP transaction maps 1:1 to a ledger entry, every payout maps to a bank credit, and the sum of fees matches the PSP's fee report.

## Step 1 — Data collection

Pull two sources daily (or per-payout cycle):

1. **PSP transaction report** — via API (preferred) or SFTP CSV export:
   - Stripe: `GET /v1/balance/history?limit=100&created[gte]=...`
   - Each record: `{id, type, amount, fee, net, currency, created, available_on, description}`

2. **Internal ledger entries** for the same period:
   ```sql
   SELECT
     ledger_entry_id,
     external_transaction_id,   -- PSP charge/refund ID
     amount_minor_units,
     currency,
     entry_type,                -- charge | refund | fee | payout
     created_at
   FROM ledger_entries
   WHERE created_at BETWEEN :start AND :end
   ORDER BY created_at;
   ```

## Step 2 — Matching algorithm

Match on `external_transaction_id` (PSP id = your ledger's `external_transaction_id`):

```
for each psp_record in psp_report:
    ledger_match = find ledger_entry WHERE external_transaction_id = psp_record.id

    if no match:
        flag UNMATCHED_PSP — money in PSP not in ledger
    elif ledger_match.amount != psp_record.net:
        flag AMOUNT_MISMATCH (delta = psp_record.net - ledger_match.amount)
    else:
        mark MATCHED
```

```
for each ledger_entry in ledger WHERE type in (charge, refund):
    if not matched:
        flag UNMATCHED_LEDGER — money in ledger not in PSP
```

## Step 3 — Discrepancy classification

| Code | Description | Typical cause | Resolution |
|---|---|---|---|
| `UNMATCHED_PSP` | PSP record has no ledger entry | Missed webhook; duplicate prevention over-fired | Replay the webhook or create compensating entry |
| `UNMATCHED_LEDGER` | Ledger entry has no PSP record | Phantom charge; ledger bug | Investigate and void/reverse the ledger entry |
| `AMOUNT_MISMATCH` | Amounts differ | Fee deducted at wrong point; currency conversion | Correct fee ledger entries |
| `TIMING_GAP` | Present in one source, absent in other at T | Timing window — PSP and webhook not yet synced | Re-run reconciliation after settlement lag |
| `DISPUTE_OPEN` | Chargeback open; PSP holds funds | Normal during dispute window | Track in a dispute register; reconcile on resolution |

## Step 4 — Fee reconciliation

PSP fees are deducted per transaction. Verify separately:

```
expected_fees = Σ (psp_report.fee for all records in period)
ledger_fees   = Σ (ledger_entries WHERE type = 'fee' AND period)

if abs(expected_fees - ledger_fees) > tolerance:
    flag FEE_RECONCILIATION_FAILURE
```

Tolerance: zero for integer minor-unit systems. Any delta is a real discrepancy.

## Step 5 — Payout reconciliation

```
for each bank_credit (from bank statement):
    psp_payout = find psp_payout WHERE payout_id = bank_credit.reference

    if no match: flag PAYOUT_UNMATCHED
    elif psp_payout.amount != bank_credit.amount: flag PAYOUT_AMOUNT_MISMATCH
```

Payouts aggregate transactions — verify the payout total equals the sum of its constituent transactions minus fees:

```
payout_total = Σ (psp_record.net WHERE payout_id = X)
```

## Step 6 — Reporting and alerting

Run reconciliation on a **scheduled job** (daily, after settlement window closes):

- Emit metrics: `matched_count`, `unmatched_psp_count`, `unmatched_ledger_count`, `discrepancy_amount_minor_units`.
- Alert on-call if `discrepancy_amount > 0` or `unmatched_count > 0`.
- Write a reconciliation report to an audit table — never overwrite, always append-only.
- Route `FEE_RECONCILIATION_FAILURE` and `PAYOUT_UNMATCHED` to finance for the accounting close.

## Pitfalls

- **Reconciling on created-at instead of settled/available-at** — transactions created near midnight may settle the next day; use `available_on` from the PSP for period boundaries.
- **Not handling refunds as negative charges** — a refund reverses a charge; both create ledger entries; matching only on charge IDs misses refund records.
- **Treating `TIMING_GAP` as an error** — PSP webhooks can arrive hours after the transaction; rerun after the settlement lag before flagging.
- **Discarding the discrepancy record after resolution** — always preserve the original mismatch and the resolution action for the audit trail.
- **Floating-point comparison of amounts** — store and compare in integer minor units; a float equality check on currency amounts fails due to rounding.
