# Controller Autopilot — architecture & honest scope

Last reviewed: 2026-07-06 · Confidence: high (built + acceptance-tested this session)

The controller-autopilot is the `finance` plugin's governed **close-to-report cycle**: a controller (or assistant controller) points it at their books and gets a review-ready close package, leaving them to **review and approve**. This doc records what it is, what it deliberately is *not*, and why — so no agent overclaims it.

## The cycle (one governed run)

```
ingest (TB/CSV; ELT tier later) → lint COA map → produce statements (IS/BS + draft CF)
  → reconcile + flux (materiality) → assemble close package (HTML) → SUBMIT
  → [separate, human, SoD-enforced] review → approve → lock (+ hash-chained audit log)
```

Artifacts: `scripts/statement_engine.py`, `reconcile_summary.py`, `close_state.py`, `controller_cycle.py`; skills `produce-gaap-statements`, `author-coa-mapping`, `reconciliation-summary`, `close-approval-workflow`; command `run-controller-cycle`.

## Where the value actually is (not where it looks)

Producing statements from a trial balance is a **commodity** — QuickBooks, NetSuite, Xero, and Sage Intacct all emit P&L / balance sheet / cash flow natively. The differentiator is **the governed cycle as one auditable unit**:

1. **Enforced controls, not documented ones** — the review→approve→lock state machine refuses same-actor approval above threshold and illegal transitions, with an append-only hash-chained audit log. (The failure mode it targets: the public 2025 "AP agent released ~$92K past a documented control" incident — a control written down but not enforced.)
2. **The COA-mapping authoring/validation asset** — the bespoke, judgment-laden mapping is the real per-entity work and where misstatements hide; it is the unit of reuse across companies.
3. **Classification-correct statements** — the engine blocks on unmapped accounts and is tested on subtotals (gross profit, operating income), because a balance-check is a tautology that cannot catch mis-classification.
4. **Honest traceability** — TB-only output is badged *not audit-traceable*; the cash flow is an *unaudited draft*; drill-through to journal entries arrives with the ELT tier.

## Honest scope — do NOT overclaim

- **Not a replacement for the judgment that produces the trial balance.** Accruals, cutoff, estimates, and the account reconciliations that turn a raw GL into a *reconciled* TB remain human-owned; the autopilot governs and reports the close, it does not invent the underlying accounting.
- **Local-tier controls are tamper-evident, not tamper-preventing.** Identity is config-asserted, not authenticated. Auditor-grade segregation needs an IdP + immutable store at the warehouse/ELT tier. The local workflow makes the honor system honest and testable — nothing more.
- **Statements from a TB are not audit-traceable.** Line → account → journal-entry → document lineage needs transaction detail; supply `--gl-detail` to begin it, full lineage lands with ELT.
- **No live financial actions.** The product is review-and-approve by design; nothing posts to a live ledger or moves cash.

## Roadmap (deferred, per the FORGE plan)

Finance-shaped ELT staging (QBO/NetSuite/Sage Intacct/Xero, local CSV schema held byte-identical to dbt staging columns); reconciliation auto-match/threshold auto-certification; consolidation + intercompany elimination; a productized per-entity dashboard reusing `data-platform`'s RLS + JWT embed; a secrets/PII scan gate for the plugin. Full plan: the FORGE run under `.ravenclaude/runs/forge/financial-controller-autopilot/plan.md`.
