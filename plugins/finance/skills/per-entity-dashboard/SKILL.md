---
name: per-entity-dashboard
description: "Render a close-package JSON (controller_cycle.py --out-json) into a self-contained, CSP-safe, theme-aware per-entity dashboard — headline KPIs (revenue, net income, gross margin, current ratio, DSO), IS/BS summaries, reconciliation exceptions, top flux, and close-state + traceability/self-certified badges. Runs scripts/entity_dashboard.py. Used by `controller`."
---

# Skill: per-entity-dashboard

**Purpose:** Turn the close package `controller_cycle.py` already produced into a single, self-contained per-entity dashboard a controller or a reviewer opens offline — a **presentation surface over the governed close, not a second source of truth**. It recomputes no statement math beyond a few ratio derivations; every number, badge, and materiality suppression flows through from the package unchanged.

Engine: [`../../scripts/entity_dashboard.py`](../../scripts/entity_dashboard.py) (stdlib only, Python 3.8+).

## When to use

- You have a close-package JSON from `controller_cycle.py --out-json` (shape: `entity` / `period` / `currency` / `statements{income_statement, balance_sheet, cash_flow}` / `reconciliation` / `flux` / `workflow_state`).
- You want the reviewer's or the controller's one-screen read of the period: KPIs at the top, statements + exceptions + flux below, governance state on the header.
- This is the productized **presentation** step that sits *after* the cycle, distinct from the reviewer-facing HTML `controller_cycle.py` emits inline.

## Run it

```shell
# 1. produce a close package
python3 scripts/controller_cycle.py --entity entity.json --coa coa-mapping.csv \
    --tb tb-2026-06.csv --prior-tb tb-2026-05.csv --subledger subledger.csv \
    --gl-detail gl-detail.csv --run-dir ./run --out-json close-package.json

# 2. render the per-entity dashboard from it
python3 scripts/entity_dashboard.py --package close-package.json \
    --out dashboard.html
```

A worked sample rendered from the committed `produce-gaap-statements/examples/` inputs lives at [`examples/sample-entity-dashboard.html`](examples/sample-entity-dashboard.html).

## What it shows

| Block | Source in the package | Notes |
|---|---|---|
| Headline KPIs | IS subtotals + BS subtotals + reasoning trail | revenue, net income, gross margin %, net margin %, current ratio, DSO |
| Income statement | `statements.income_statement.subtotals` | revenue → gross profit → operating income → net income |
| Balance sheet | `statements.balance_sheet.subtotals` | current assets, total assets/liabilities/equity, balance check |
| Cash flow | `statements.cash_flow` | carried through with its `unaudited_draft` label + caveat |
| Reconciliation exceptions | `reconciliation.accounts` | FLAG rows surfaced; pass / self-supported counted |
| Top flux movements | `flux.material_movements` | top 8 by absolute movement (already materiality-suppressed upstream) |
| Governance | `workflow_state` + `statements.traceability_badge` | close state, traceability badge, self-certified banner |

## The disciplines that make it honest

1. **KPIs are derived, not asserted — and absent inputs show `n/a`, never a plug.** Revenue / net income / gross margin come straight from the IS subtotals. The **current ratio** needs current liabilities, which the BS subtotals do not carry, so it is recovered from the statement reasoning trail's `CurrentLiabilities` section — using the same **presentation-signed** convention `statement_engine.py` uses (section-natural side, so contra-accounts stay correct), *not* the account normal_balance. If the trail is absent, the KPI is shown `n/a`. **DSO** is an explicit single-period proxy: AR (the BS line whose name carries "receivable") over the period's own revenue times the period's own day count, labeled as such — never silently annualized.
2. **It inherits upstream honesty; it does not manufacture it.** The traceability badge (`TB-only` vs `GL-detail-traced`), the cash-flow `unaudited_draft` label, and the `self-certified / single-actor` governance banner are carried through verbatim. A green KPI on a self-certified, un-locked package is still self-certified, and the banner says so.
3. **Self-contained + CSP-safe.** Inline CSS/JS only, zero external requests (no CDN font, no remote image, no fetch), so it opens from disk and is safe to email to a reviewer. Light + dark via `prefers-color-scheme` with a `data-theme` override; `tabular-nums` so figures align.

## Scope caveat — single-entity tier (read this)

This is the **single-entity, file-in / file-out** tier. The recurring, warehouse-backed, **multi-tenant** version (many entities, row-level isolation, a live embedded dashboard) is **not** this skill and is deliberately not reimplemented here. It reuses `data-platform`'s row-level security and signed-JWT embed work — skills [`rls-policy-authoring`](../../../data-platform/skills/rls-policy-authoring/SKILL.md) and [`jwt-embed-issuance`](../../../data-platform/skills/jwt-embed-issuance/SKILL.md). **Auth, tenant isolation, and token issuance are that plugin's owned surface — do not hand-roll them here.** (Cross-plugin reference is soft/optional per the marketplace's graceful-degradation convention; if `data-platform` is not installed, treat those two skills as the design pointer for the warehouse tier.)

## Honest limitations

- The dashboard is **decision-support**, not an accounting / audit / tax opinion. It presents what the governed cycle produced; it does not attest to it.
- KPIs are only as good as the package. DSO on a single period is a proxy, not a working-capital trend; a `TB-only` package's numbers are not audit-traceable no matter how clean the KPIs look.
- It renders one entity, one period. Consolidation, intercompany elimination, and multi-period trends are out of scope (roadmap: the warehouse tier above).
