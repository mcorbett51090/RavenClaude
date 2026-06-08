# accounting-firm-cpa

US **public-accounting / CPA-firm operations** plugin. This team helps you run a CPA firm's core
workflows: firm economics, tax-season throughput, Client Accounting Services, attest engagements,
and advisory packaging — employer-neutral, US practice norms.

> **The one-line philosophy:** the engagement letter scopes the work, the calendar is the product,
> independence is the license, and realization tells you whether the business is healthy.

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "What's our realization rate / utilization? Build a capacity plan." | **accounting-firm-cpa** (`firm-practice-lead`) |
| "Design our 1040/1120/1065 tax-season workflow / extension strategy" | **accounting-firm-cpa** (`tax-workflow-strategist`) |
| "Scope a CAS engagement / pick a tech stack / price monthly close-as-a-service" | **accounting-firm-cpa** (`cas-engagement-lead`) |
| "Plan this audit / draft PBC list / check independence / review workpapers" | **accounting-firm-cpa** (`audit-engagement-lead`) |
| "Package and price advisory services / CAS upsell strategy" | **accounting-firm-cpa** (`firm-advisory-lead`) |
| "Build a three-statement model / variance walk for a corporate client" | `finance` |
| "Interpret a new IRS rule / AICPA standard / state-board guidance" | `regulatory-compliance` |
| "Billing system architecture / AR automation for the firm" | `fintech-payments-engineering` (pattern only) |

## What's inside

- **5 agents** — `firm-practice-lead`, `tax-workflow-strategist`, `cas-engagement-lead`,
  `audit-engagement-lead`, `firm-advisory-lead`.
- **3 skills** — `tax-season-workflow`, `client-accounting-services`,
  `engagement-and-workpaper-management`.
- **3 commands** — `/accounting-firm-cpa:plan-tax-season`,
  `:scope-cas-engagement`, `:prep-audit-pbc`.
- **2 templates** — `engagement-letter.md`, `pbc-request-list.md`.
- **Knowledge bank** — `knowledge/cpa-firm-decision-trees.md`: Mermaid trees for
  engagement-type / independence, fixed-fee vs. hourly pricing, review-tier routing, plus a dated
  2026 capability map (tax software, workflow tools, CAS stack).
- **6 best-practices**, **1 advisory hook** (flags independence impairment, unsupported numbers,
  plaintext PII, undated fee figures), and **`scripts/firm_calc.py`** (realization, utilization,
  effective rate, leverage, fixed-fee margin).

## House opinions (the short list)

1. Independence is non-negotiable on attest work.
2. Workpapers must support every number.
3. The engagement letter scopes the work and the fee.
4. Realization and utilization drive firm economics.
5. Deadline management is the product.
6. Protect client tax and financial data.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
