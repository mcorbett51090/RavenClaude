# Test with concurrent conflicting edits and partition

**Status:** Absolute rule
**Domain:** Testing / verification
**Applies to:** `realtime-collaboration-engineering`

> Engineering craft, not product advice.

---

## Why this exists

The happy-path demo (one user, then another, taking turns) exercises none of the hard parts. The bugs live in **simultaneous conflicting edits, network partitions, and reconvergence** — exactly the cases a manual demo never hits. A collaborative system is only as correct as its concurrency tests.

## How to apply

- Test **two (or more) clients editing the same field at the same instant**; assert the merged result converges **and** matches intention.
- Test a **partition**: split the network, let both sides edit, then heal — assert reconvergence with no lost or duplicated ops.
- Test **offline → reconnect** with a buffered delta; assert no replay-as-new.
- Test the **growth path**: a long-lived document with many deletes; assert compaction/GC keeps it bounded.
- Property-test op-pair commutativity/idempotency where the model claims it.

**Do:** automate concurrent-edit + partition + reconnect scenarios.
**Don't:** sign off on a turn-taking demo as proof of correctness.

## Edge cases / when the rule does NOT apply

None for a shipping collaborative feature. A spike/throwaway can skip it, but then it is a spike, not a product.

## See also

- [`../templates/offline-conflict-test-plan.md`](../templates/offline-conflict-test-plan.md)
- Seam: load behavior under churn → [`../../performance-engineering/CLAUDE.md`](../../performance-engineering/CLAUDE.md)

## Provenance

Codifies the team's verification discipline + `sync-engine-engineer` house opinion.

---

_Last reviewed: 2026-06-24 by `claude`_
