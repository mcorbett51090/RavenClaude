# accounting-bookkeeping

A **Accounting & Bookkeeping Practice specialist team** for an accounting-practice owner, controller, or bookkeeper accountable for a clean, timely close and reliable books across a client portfolio. It closes the books on a cadence and measures days-to-close, reconciles before it reports, reads AR aging and AP timing as working-capital levers, enforces segregation of duties, and states accrual-vs-cash basis before any figure.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Basis-explicit, client-flexible (accrual | cash basis; single-entity | multi-entity).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `accounting-practice-lead`, `close-cycle-analyst`, `ap-ar-cashflow-specialist`, `reconciliation-controls-specialist` |
| **5 skills / commands** | `run-close` · `reconcile-accounts` · `read-working-capital` · `estimate-bad-debt` · `audit-controls` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · close-checklist.md · working-capital-worksheet.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, client financial PII) in generated deliverables |
| **`scripts/acctgops_calc.py`** | stdlib calculator — `working-capital` · `aging` · `close-cycle` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install accounting-bookkeeping@ravenclaude
```

## Quickstart

> "Our monthly close keeps slipping past two weeks — where's the bottleneck?"

The `accounting-practice-lead` scopes the problem, routes to `close-cycle-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a licensed CPA firm rendering tax or audit opinions, a fractional-CFO/FP&A advisory function, or a payroll/tax-filing service. It does not sign tax returns, issue audit opinions, give tax advice, set GAAP positions, or store client financial PII. Tax and audit determinations route to a licensed CPA.
