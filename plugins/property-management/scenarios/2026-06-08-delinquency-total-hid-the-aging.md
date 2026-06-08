---
scenario_id: 2026-06-08-delinquency-total-hid-the-aging
contributed_at: 2026-06-08
plugin: property-management
product: delinquency
product_version: "n/a"
scope: likely-general
tags: [delinquency, aging, collections, bad-debt]
confidence: medium
reviewed: false
---

## Problem

A manager reported delinquency 'about the same as last month' and moved on. The risk: a flat total can hide a dangerous shift in the aging — collectable 0-30 balances clearing while harder 60+ balances grow keeps the total steady while recoverable cash falls (§3 #2).

## Context

- Asset class: workforce housing, monthly billing.
- Constraint: a dollar in 60+ is worth far less than a dollar in 0-30; collections should follow the aging curve (§3 #2).
- The manager reasoned from the single total.

## Attempts

- Tried: **bucketed the balance into 0-30 / 31-60 / 60+** before trusting the total. Outcome: the flat total masked migration — 60+ had grown while 0-30 shrank.
- Tried: **weighted the balance by collectability.** Outcome: realistic recoverable cash had fallen even though the headline number held (§3 #2).
- Tried: **routed the oldest resident-specific balances appropriately.** Outcome: eviction/legal questions went to counsel, not the operating team (§2).

## Resolution

The response was a **0-30-focused collections push to stop migration plus a realistic bad-debt write-down into the EGI bridge** — and legal routing for the 60+ cases. The output was the aged delinquency read and the NOI impact of the write-down.

**Action for the next consultant hitting this pattern:** **age delinquency before trusting the total.** A flat total can hide balances migrating into uncollectable buckets; weight by aging, focus collections on 0-30, and route legal cases to counsel. See Tree 3 and the `property_management_calc.py` `noi` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
