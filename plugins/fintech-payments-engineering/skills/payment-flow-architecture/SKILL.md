---
name: payment-flow-architecture
description: "Architect money-safe payments: represent money as integer minor units + currency (never floats), keep a double-entry append-only ledger as source of truth (the PSP is an integration you reconcile against), design a money-event model, and reconcile continuously."
---

# Payment Flow Architecture

## Money = integers
Integer **minor units** (cents) + currency code. Never floats — float money = rounding-error disputes.

## Double-entry ledger = source of truth
Every movement = balanced **debits/credits** in an **append-only** ledger you own. The PSP is an integration you **reconcile** against, not your books.

## Reconcile continuously
Match ledger to PSP (payouts/fees/disputes); a discrepancy is a bug or fraud, not rounding. Unreconciled = mystery money.

## Hand off
Money events here; revenue recognition/GL -> `finance`; regulation -> `regulatory-compliance`.
