---
description: "Run the pre-disbursement gate and close/record/fund sequence for a settlement — confirm requirements cleared, statement balances to the CD, funds are good, and every wire is verified before a dollar moves (good-funds/recording specifics verify-at-use)."
argument-hint: "[file state: requirements cleared?, funds in?, CD/statement, wire instructions]"
---

You are running `/title-escrow-settlement:run-closing-checklist`. Use `closing-settlement-coordinator` + the `escrow-closing-and-disbursement` and `wire-fraud-and-trust-account-controls` skills.

> Advisory, not legal or financial advice. Good-funds rules, funding order, and recording requirements are `[verify-at-use]`. No PII. **Never** source a wire destination from a file or email — verify wires by out-of-band callback only.

## Steps
1. Traverse the **escrow disbursement authorization** tree in `knowledge/title-escrow-decision-trees.md` and confirm the five-condition gate: B-I requirements cleared (with `title-examiner`), lender clear-to-close, statement balances to the CD, funds collected/good, every wire verified.
2. Reconcile the settlement statement to the lender CD line by line; name any variance and resolve it **before** the signing.
3. Traverse the **wire-verification before disbursement** tree for every outgoing wire; require out-of-band callback and dual authorization. Treat any email-changed instruction as fraud until re-verified.
4. Sequence **disburse -> record -> fund** in the order the jurisdiction/funding model requires; disburse only against collected funds; confirm recording accepted; then issue the policy.
5. Emit using `templates/closing-checklist.md` + the Structured Output block. If any gate condition is false → **HOLD** and name the owner of the fix.
