---
scenario_id: 2026-06-08-close-bottleneck-was-reconciliation
contributed_at: 2026-06-08
plugin: accounting-bookkeeping
product: close-cycle
product_version: "n/a"
scope: likely-general
tags: [close, critical-path, reconciliation, bottleneck]
confidence: medium
reviewed: false
---

## Problem

A practice's monthly close routinely slipped past two weeks and the owner wanted to add staff. The risk: a close is a critical-path process, and throwing people at non-critical tasks doesn't move days-to-close — the bottleneck does, and reconciliation gates the whole close (§3 #1 #2).

## Context

- Client: a single-entity services business, accrual basis.
- Constraint: days-to-close is set by the longest dependent task chain, and the books can't close on un-reconciled accounts (§3 #1 #2).
- The owner reasoned from total workload, not the critical path.

## Attempts

- Tried: **mapped the close as a critical path** (`acctgops_calc.py close-cycle`). Outcome: most tasks ran in parallel; one task — reconciling a high-volume bank account — sat on the critical path and blocked statements.
- Tried: **checked reconciliation status before declaring tasks done** (§3 #2). Outcome: that account hadn't been reconciling cleanly, so every downstream statement waited.
- Tried: **parallelized non-critical tasks** instead of adding staff (§3 #1). Outcome: the close compressed once the one bottleneck was fixed.

## Resolution

The fix was to **fix the bank reconciliation feeding the critical path and parallelize the rest** — not hire. The output was the critical-path map, the reconciliation gap, and a days-to-close target.

**Action for the next consultant hitting this pattern:** **find the close bottleneck on the critical path, and reconcile before you call it done.** Total workload doesn't set days-to-close; the longest dependent chain does, and un-reconciled accounts block the close. See Tree 1 and the `acctgops_calc.py` `close-cycle` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
