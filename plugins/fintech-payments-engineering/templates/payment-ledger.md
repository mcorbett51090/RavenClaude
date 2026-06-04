# Double-entry payment ledger (pattern)

Every money movement = balanced entries (sum to zero), append-only:

| txn_id | account | debit_cents | credit_cents | currency | event | ref (PSP id) |
|---|---|---|---|---|---|---|
| t1 | customer_receivable | 0 | 5000 | USD | charge.succeeded | pi_... |
| t1 | cash_in_transit | 5000 | 0 | USD | charge.succeeded | pi_... |

- Integer minor units + currency. Append-only (corrections are new entries).
- Reconcile to the PSP continuously. Money events -> finance for recognition.
