---
name: reconciliation-summary
description: "Balance-sheet tie-out (book vs sub-ledger, review-by-exception at materiality) plus a materiality-suppressed period-over-period flux table. Runs scripts/reconcile_summary.py; narrative 'why' reuses the variance-commentary skill. Used by `controller`."
---

# Skill: reconciliation-summary

**Purpose:** Produce the two controller-review artifacts that wrap the statements in a close package — a reconciliation tie-out and a period-over-period flux — both governed by the entity's materiality threshold so the reviewer reads the exceptions, not the whole ledger.

Engine: [`../../scripts/reconcile_summary.py`](../../scripts/reconcile_summary.py) (stdlib only).

## When to use

- Step 4 of the close cycle (`run-controller-cycle`), after statements are produced.
- Any time you need a tie-out status across balance-sheet accounts or a material-movement flux.

## Reconciliation (review-by-exception)

Each balance-sheet account's book balance (`debit − credit`) is compared to an optional sub-ledger / third-party balance (`account,subledger_balance` CSV):

- within materiality → **PASS** (the auto-certification discipline behind FloQast/Numeric — the human reviews the exceptions)
- at/beyond materiality → **FLAG** for a human
- no sub-ledger supplied → **self-supported** (marked, never silently passed)

## Flux (materiality-suppressed)

Period-over-period movement per account with `--prior-tb`; movements below materiality are suppressed so only the lines that *moved* surface, ranked by absolute movement. This produces the **movement table**; the narrative **"why"** for each movement is authored via the existing [`variance-commentary`](../variance-commentary/SKILL.md) skill and [`finance_calc.py variance-bridge`](../../scripts/finance_calc.py) (house rule: reuse, don't duplicate).

## Invocation

```shell
python3 scripts/reconcile_summary.py \
  --entity examples/meridian-robotics.json \
  --tb examples/trial-balance-2026-06.csv \
  --prior-tb examples/trial-balance-2026-05.csv \
  --subledger examples/subledger-2026-06.csv \
  --out recon.json
```

## Discipline

**Reconcile before you narrate** (CLAUDE.md §3 #3): flux commentary on an un-reconciled account describes noise, not signal. A flagged reconciliation is owned and dated, not carried.
