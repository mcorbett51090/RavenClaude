---
scenario_id: 2026-06-08-control-gap-one-person-did-everything
contributed_at: 2026-06-08
plugin: accounting-bookkeeping
product: controls
product_version: "n/a"
scope: likely-general
tags: [controls, segregation-of-duties, coa-hygiene, reconciliation]
confidence: medium
reviewed: false
---

## Problem

A small practice's client had one person approving payments, entering them, and reconciling — and reports never quite tied out. The risk: no segregation of duties is the classic fraud/error vector, and a miscoded chart of accounts corrupts every report built on it, so the analysis was untrustworthy before it began (§3 #5 #7).

## Context

- Client: a small business with a single bookkeeper, cash basis.
- Constraint: approve ≠ enter ≠ reconcile, and COA hygiene precedes any analysis (§3 #5 #7).
- Leadership trusted the reports without auditing controls or coding.

## Attempts

- Tried: **mapped segregation of duties** (`audit-controls`). Outcome: one person held all three roles — no independent check on payments or reconciliation (§3 #5).
- Tried: **audited the chart of accounts** (§3 #7). Outcome: catch-all accounts and duplicate codes were scrambling expense categorization, so margin reads were meaningless.
- Tried: **gated the analysis until controls and COA were sound** (§3 #5 #7). Outcome: post-cleanup numbers differed materially from the originals.

## Resolution

The fix was **compensating controls (owner approval/review), a COA cleanup, and independent reconciliation** before any reporting — not trusting the existing reports. Any indication of actual fraud routes to a licensed CPA and the qualified authority (§2). The output was the controls read, the COA-hygiene plan, and corrected statements.

**Action for the next consultant hitting this pattern:** **audit segregation of duties and COA hygiene before trusting the books.** Approve = enter = reconcile is the classic gap, and a miscoded chart corrupts every report; add compensating controls and clean the COA first, and route suspected fraud to a licensed CPA. See Tree 3 and the `audit-controls` skill.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
