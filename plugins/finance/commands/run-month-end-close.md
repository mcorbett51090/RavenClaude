---
description: Run a month-end close checklist with the controls that survive an audit — sub-ledgers tied to the GL with any over-materiality difference owned and dated, every JE carrying a real memo and a separate reviewer, the revenue-recognition basis stated, and the deferred-revenue roll-forward tying.
argument-hint: "[the period + entity, e.g. 'April close for a mid-sized SaaS business']"
---

# Run a month-end close

You are running `/finance:run-month-end-close`. Drive (or review) the close the user described (`$ARGUMENTS`), following this plugin's `controller` discipline. A difference over materiality is owned, not carried; a JE without a memo is a number an auditor cannot trust six months later.

## When to use this

A month-end / quarter-end close, or a close-readiness review before an audit. Not for the variance commentary that follows close (use the variance command, which gates on this close's reconciliations).

## Steps

1. **Reconcile every sub-ledger to the GL** (`controller-reconcile-the-subledger-to-the-gl`): tie AR, AP, fixed assets, inventory, deferred revenue, intercompany, and suspense to their GL control accounts. Any residual over materiality gets an owner, a root cause, and a dated remediation — never carried unexplained, never plugged.
2. **Match and eliminate intercompany at the period** (`controller-reconcile-the-subledger-to-the-gl`): a net IC imbalance over materiality is an open loop to close before sign-off — small each month, large by year-end, and a guaranteed audit finding.
3. **Give every JE a memo and a separate reviewer** (`controller-every-journal-entry-carries-a-memo-and-reviewer`): the memo names the driver, source doc, period, and basis ("adj per analysis" is not a memo); preparer signs, a different reviewer signs, both before close is declared done. Give round-number accruals a second look — they're usually un-refined estimates.
4. **State the revenue-recognition basis and tie the deferred-revenue roll** (`controller-state-the-revenue-recognition-policy`): recognize revenue as the performance obligation is satisfied (point-in-time vs over-time), maintain opening deferred + new billings - recognized = closing, and label each figure's basis (recognized GAAP vs bookings vs billings vs ARR) — never blend GAAP and management views silently.
5. **Confirm the close is auditable** (house opinion #6): every workpaper carries date prepared, preparer, reviewer, and source-data lineage; reconciliations are signed off before the close is declared complete.

## Guardrails

- Don't plug a GL control account to force a tie — fix the broken feed, don't mask it; every reconciling item is a real timing difference or a bug, never a plug.
- A genuine prior-period restatement is not a quiet reclass — it carries an explicit policy, a memo, and often auditor notification.
- Confidentiality by default — scrub salaries, customer-specific figures, and bank/wire details before sharing examples; any change touching wire instructions or vendor payment routing routes through `ravenclaude-core/security-reviewer`.
