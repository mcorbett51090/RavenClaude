---
name: produce-gaap-statements
description: "Turn a reconciled trial balance + a COA mapping into an income statement, balance sheet, and draft cash flow — classification-tested (blocks on unmapped accounts, catches mis-mapping that a balance-check cannot) with an honest traceability badge. Runs scripts/statement_engine.py. Used by `controller`."
---

# Skill: produce-gaap-statements

**Purpose:** Produce the period's financial statements from a trial balance as a *commodity producer inside a governed close cycle* — not as a differentiator. Every GL (QuickBooks, NetSuite, Xero, Sage Intacct) already emits P&L / balance sheet / cash flow; this engine earns its place by being **classification-correct, blocking, and honest about traceability**, so its output can be trusted inside the review→approve→lock workflow.

Engine: [`../../scripts/statement_engine.py`](../../scripts/statement_engine.py) (stdlib only, Python 3.8+).

## When to use

- You have a reconciled trial balance (CSV: `account,description,debit,credit,entity,period,currency`) and a COA→statement-line mapping, and need the period's IS / BS / draft CF.
- You are wiring the close cycle (`run-controller-cycle`) — this is step 3.

## The three disciplines that make it honest

1. **Blocks on unmapped accounts (`--strict`).** A balanced trial balance produces a balanced balance sheet *regardless of whether accounts map to the right lines* — net income is `Σ(credit − debit)` over IS accounts no matter how they are classified. So "assets == liabilities + equity to the cent" is a **tautology** that proves the arithmetic and catches nothing about mis-classification. Correctness lives in the **subtotals** (gross profit, operating income), which *are* classification-sensitive. The engine refuses to emit a statement while any TB account is unmapped rather than silently plugging it. Verify with `--lint-map`.
2. **Traceability badge.** A trial balance has already discarded the transaction detail an auditor needs (line → account → journal entry → source document). With only a TB the output is badged **`TB-only - NOT audit-traceable`** so the false precision is explicit. Pass `--gl-detail <journal-lines.csv>` to carry account→JE references into the reasoning trail and lift the badge to `GL-detail-traced`.
3. **Cash flow is an unaudited draft.** Indirect-method CF needs operating/investing/financing classification and non-cash adjustments not derivable from a two-period TB alone. With `--prior-tb` the engine emits a best-effort CF **labeled `unaudited_draft`** whose cash tie-out is a *sanity* check, never a correctness proof.

## Invocation

```shell
python3 scripts/statement_engine.py \
  --entity  examples/meridian-robotics.json \
  --coa     examples/coa-mapping.csv \
  --tb      examples/trial-balance-2026-06.csv \
  --prior-tb examples/trial-balance-2026-05.csv \
  --gl-detail examples/gl-detail-2026-06.csv \
  --strict --out statements.json
```

## Correctness discipline (from the FORGE red-team)

- The golden fixture [`examples/expected-subtotals-2026-06.json`](examples/expected-subtotals-2026-06.json) is **hand-derived from the source TB by independent arithmetic**, NOT frozen from an engine run — so a bug cannot ship inside its own golden.
- The negative fixture [`examples/coa-mapping-misclassified.csv`](examples/coa-mapping-misclassified.csv) deliberately mis-maps interest expense to COGS; the acceptance suite asserts gross profit changes (**caught**) while net income does not (proving a balance-check cannot catch it). See [`../../scripts/test_controller_autopilot.py`](../../scripts/test_controller_autopilot.py).

## Reuse per entity

Entities are **data** — a different entity profile + COA mapping runs the same engine with zero code change. Authoring and validating a correct COA mapping is the real per-entity work; see the [`author-coa-mapping`](../author-coa-mapping/SKILL.md) skill.

## What this is not

Not an audit opinion or a GAAP determination — outputs are decision-support (see [`../../CLAUDE.md`](../../CLAUDE.md) §3). Statements from a TB alone are not audit-traceable; the drill-through to journal entries lands with the ELT tier.
