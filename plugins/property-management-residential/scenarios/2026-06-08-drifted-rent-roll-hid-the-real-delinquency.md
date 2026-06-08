---
scenario_id: 2026-06-08-drifted-rent-roll-hid-the-real-delinquency
contributed_at: 2026-06-08
plugin: property-management-residential
product: generic
product_version: "unknown"
scope: likely-general
tags: [rent-roll, delinquency, reconciliation, data-integrity, collections]
confidence: high
reviewed: false
---

## Problem

A portfolio's delinquency report showed a manageable number, but cash kept coming in short. The rent roll had drifted from reality: a few units carried stale market rents, two "occupied" units had quietly gone to notice, and several balances didn't reconcile to the ledger. The delinquency aging was computed off the drifted roll, so it understated the real past-due exposure — the team was working a collections problem that was, underneath, a data-integrity problem.

## Constraints context

- The rent roll was a hand-maintained spreadsheet kept alongside (not reconciled to) the system of record.
- Status changes (notice, down) and rent changes weren't flowing back into the roll consistently.
- The collections team chased balances off the report without first checking the report reconciled.

## Attempts

- Tried: escalating collections effort on the reported delinquent accounts. Failed — chasing a wrong list missed real past-due balances and wasted effort on reconciled-but-mislabeled ones.
- Tried: writing off the gap as "timing." Failed — the gap was structural drift, not timing; it recurred every month.
- Tried: reconciling the rent roll to the system of record FIRST (unit, tenant, lease term, market vs. actual rent, balance, status), THEN recomputing the aging buckets off the corrected roll and applying the documented collections ladder uniformly. This worked.

## Resolution

Reconciliation surfaced the stale rents, the mislabeled statuses, and the unreconciled balances. Once the roll matched reality, the aging buckets told the true story — the 90+ bucket was materially larger than the drifted report had shown — and the consistent collections ladder (reminder → late notice → pay-or-quit → counsel) was applied to every delinquent account, with the pay-or-quit and eviction rungs flagged to counsel rather than executed as settled law. Delinquency, occupancy, and NOI all corrected at once because they all read off the same now-accurate roll.

## Lesson

The rent roll is the source of truth or it's nothing — a balance that doesn't reconcile to the ledger is a data-integrity problem before it's a collections problem, so fix the rent roll first. Then run one documented collections ladder uniformly across every account; the legal rungs flag to counsel. A drifted rent roll mis-states delinquency, occupancy, and NOI simultaneously.
