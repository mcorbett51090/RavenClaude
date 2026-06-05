# Eliminate Intercompany Before You Consolidate

**Status:** Absolute rule
**Domain:** Close / consolidation
**Applies to:** `finance`

---

## Why this exists

Intercompany transactions — loans, management fees, cost allocations, sales between subsidiaries — inflate both sides of the consolidated balance sheet and income statement if they are not eliminated. A $10 M intercompany loan left in creates $10 M of phantom assets and liabilities; an uneliminated intercompany sale inflates revenue and cost of goods sold by exactly the same amount and misleads every margin metric derived from them. Auditors trace intercompany to a zero-balance test on day one; failing it signals a fragile close process and risks a restatement.

## How to apply

Run eliminations as a defined, documented step in the close calendar — after subsidiary trial balances are finalized and before the consolidated workpaper is produced.

```
Intercompany Elimination Checklist
────────────────────────────────────────────────
□ Pull the intercompany matrix — row = entity paying, col = entity receiving.
□ Confirm the matrix nets to zero across all accounts:
     Σ IC receivables across all entities = Σ IC payables
     Σ IC revenue across all entities = Σ IC COGS/expense
□ For each non-zero cell: document the source transaction,
  the eliminating JE number, the account, and the period.
□ Flag any timing differences (one side booked in period N,
  counterpart not yet booked) — accrue the missing side before eliminating.
□ Re-check net intercompany profit in ending inventory if goods
  moved between entities — eliminate unrealized profit per ASC 810.
□ Sign off: preparer + reviewer + date.
```

**Do:**
- Run the IC matrix as a structured workpaper, not a verbal reconciliation.
- Trace every IC balance to a source transaction and a documented eliminating JE.
- Resolve timing differences within the period, not by adjusting prior periods.
- Document intercompany profit in inventory separately from balance-sheet eliminations.

**Don't:**
- Consolidate first and "clean up" intercompany later — eliminations are pre-consolidation.
- Assume the net is zero because last month it was zero; test it each period.
- Use round-number plugs to force a net-zero matrix; find the missing entry.
- Skip the unrealized-profit-in-inventory step for entities that sell goods to each other.

## Edge cases / when the rule does NOT apply

- **Single-entity entities with no subsidiaries** — no IC to eliminate; rule is N/A.
- **Equity-method investees (< 50 % / not controlled)** — IC elimination follows ASC 323 partial-elimination rules, not ASC 810 full elimination; the approach differs.
- **Pass-through eliminations that net to a rounding difference** — document the rounding disposition explicitly rather than forcing a hard zero.

## See also

- [`../agents/controller.md`](../agents/controller.md) — owns the close calendar and the IC elimination step.
- [`./controller-reconcile-the-subledger-to-the-gl.md`](./controller-reconcile-the-subledger-to-the-gl.md) — subledger reconciliation is the upstream step that gives you clean subsidiary trial balances to consolidate.

## Provenance

Codifies the controller's consolidation judgment and the ASC 810-10 consolidation standard's elimination requirement. The intercompany matrix approach and the unrealized-profit-in-inventory check reflect standard Big Four close-process practice and the finance plugin's house opinion #1 (source-cite every number) applied at the entity level.

---

_Last reviewed: 2026-06-05 by `claude`_
